# ml-serving-template  
Serving large ml models independently and asynchronously via message queue and kv-storage for communication with other services.  

<p align="center"> <img src="https://github.com/gasparian/ml-serving-template/blob/main/pics/logo5.jpg" height=320/> </p>  

I think many of us are used to place trained ML models for inference right inside the web app with the rest of the logic. Usually, you load the model once, when the app is started, and then run smth like `predict` method from the API handlers.  
And you can keep doing that, when your models are small enough (like simple image classifiers/detectors) and/or you don't need to query a big amount of data to perform the calculations.  
**But** the problems starts when you're trying to serve really large model, like some modified ResNets or modern [transformers](https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)), that can easily take >10 Gb of RAM/vRAM. Or your inference pipeline is too slow and you can't go with just a simple synchronous request.  
Or you need to perform some heavy map-reduce operation. Also, it can become too resource-consuming to scale your app coupled with such complex stuff.  
So I propose a pretty simple solution - just decouple the heavy model and the rest app logic and create a separate inference service that can be called from other apps asynchronously and via **RPC**.  
**Which gives you at least one important thing: you'll be able to independently scale client services, inference services, message bus and cache.**  
This repo is just an **example** that you can look at and use some ideas or implementation details in your projects.  
So it's up to you to decide what tools to use - maybe rabbitmq is not the best choice, maybe that could be done with just redis and redismq, or kafka, etc.  

Key points:  
 - implements publisher/subscriber interaction model via message queue and kv-storage as a cache;  
 - uses [rabbitmq](https://www.rabbitmq.com/) for sending queries from client apps (producers) to the inference services (consumers);  
 - no need to worry about rabbit disconnections due to the missed "heartbeats" from clients - connection and channel recreated, when needed (see the [RabbitWrapper](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml_serving/wrappers.py) classes);  
 - uses [redis](https://redis.io/) for temporarily storing inference results so the producers can grab them later;  
 - uses `pickle` for serialization;  
 - producer service only need to implement a [Predictor class](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml_serving/inference.py) and just pass it to the [ServingConsumer](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml_serving/server.py) on it's side. So basically, you don't need to think about communication internals. See the **[library](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml_serving)** to get more context;  
 - client services no need to "know" **anything** except the message queue;  
 - you have an option to use synchronous RPC calls to the inference service by deploying [ServingQueue](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml_serving/server.py) or make it asynchronously to get results later from redis via [ServingCache and ServingCacheQueue](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml_serving/server.py) (should run both at this case);  
 - uses `*.env` files to hold all needed configuration parameters: [main config](https://github.com/gasparian/ml-serving-template/blob/main/variables.env) and producers/consumers configs, [like this](https://github.com/gasparian/ml-serving-template/blob/main/consumers/fasttext/variables.env);  
 
And, as always, it's better to look at the code examples by yourself:  
 - check out the [library](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml-serving);  
 - example producer - [short-texts-clustering service](https://github.com/gasparian/ml-serving-template/blob/main/producers/short-texts-clustering);  
 - example consumer - [fasttext inference service](https://github.com/gasparian/ml-serving-template/blob/main/consumers/fasttext);  

### Building and running example services  

To run any service you just need to execute `./run_compose.sh` script from the corresponding service directory.  
The steps are as follows:  
 - check that configs looks good for you (all `*.env` files);  
 - first run rabbit and redis from the root dir `/`;  
 - then you're need to run consumer - for example our fasttext inference service `./consumers/fasttext`;  
 - and finally run the producer service for text clustering, which just a REST app `./producers/short-texts-clustering`;  
 - after you're done - you can run producer's test to ensure that the app works fine - `./docker_test.sh`;  

And yes - there must be way more tests.  

### Reference  

If you want to install library with wrappers locally:  
```
cd ./ml-serving
python3.8 -m pip install .
```  
Here are small code snippets from the examples above.  
On the [**consumer**](https://github.com/gasparian/ml-serving-template/blob/main/consumers/fasttext/src/predictor.py) side, you just need to first implement the predictor interface:  
```python

from typing import Union, List, Any
import fasttext
from ml_serving.inference import PredictorBase

class Predictor(PredictorBase):
    def __init__(self, path: str):
        self.__model = fasttext.load_model(path)

    def predict(self, data: Union[str, List[str], np.ndarray]) -> Any:
        return self.__model.predict(data)

```  
And then start listening for messages in the queue. All that you need is to define configuration params and apply here the prediction pipeline that you've defined before:  
```python
from ml_serving.server import ServingRpcPredictor

from config import FasttextConfig
from predictor import Predictor

config = FasttextConfig()
predictor = Predictor(config.model_path)
proc = ServingQueue(config, predictor)
proc.consume() # <-- blocking
```  

And **don't forget**, that if you want to communicate asynchronously, you need to run [**one more**](https://github.com/gasparian/ml-serving-template/blob/main/consumers/fasttext/supervisord.conf) consumer which will be acquiring requests for getting the calculation results.  

On the [**producer**](https://github.com/gasparian/ml-serving-template/blob/main/producers/short-texts-clustering/src/clustering/feature_extractors.py) side, you just need to replace the usual model initialization and prediction code with the `ServingClient`:  
```python
...
from ml_serving.client import ServingClient
from .config import ClusteringConfig

...
class FasttextExtractor(TextFeaturesExtractor):
    def __init__(self, preprocessor: Callable[[str], str], config: ClusteringConfig):
        super().__init__(preprocessor)
        self.__model = ServingClient(config)

    def get_features(self, inp: Union[List[str], np.ndarray]) -> Any:
        return self.__model.predict_sync(inp)

    # NOTE: if you use queue + cache to store results
    def request_features_async(self, inp: Union[List[str], np.ndarray]) -> str:
        return self.__model.predict_async(data)

    def get_features_async(self, key: str) -> Any:
        return self.__model.get_result(key)
```  

### Config reference  
#### Common part  
 - `RABBIT_NODES=(127.0.0.1:5672)` - rabbit broker's addresses;  
 - `RABBIT_TTL=60000` - rabbit's messages time-to-live value in ms;  
 - `PREFETCH_COUNT=10` - number of prefetched messages on the rabbit message consumer side;  
 - `RABBIT_HEARTBEAT_TIMEOUT=60` - heartbeat timetout of rabbit clients;  
 - `RABBIT_BLOCKED_CONNECTION_TIMEOUT=300` - rabbit's client connection timeout;  
 - `QUEUE_NAME=task_queue` - name of the "main" task queue which holds messages with data;  
 - `CACHE_QUEUE_NAME=cache_queue` - name of the task queue used to transmit prepared data from redis;  
 - `EXCHANGE_NAME=` - name of rabbit exchange;  
 - `EXCHANGE_TYPE=direct` - rabbit's exchange type;  

#### Services part  
Declare all needed *redis*-related stuff, if your service uses it. These data will be parsed by `Config` object.  
Example consumer:  
 - `REDIS_NODES=(127.0.0.1:6380)` - redis nodes addresses;  
 - `REDIS_TTL=60` - redis time-to-live value is seconds;  
 - `MODEL_PATH=/fasttext/cc.en.300.bin` - path to the feature extractor (as in the example consumer);  
 - `QUEUE_ONLY=1` - 1 | 0: use only for communcation or store result in cache;  

Example producer:  
 - `MIN_CLUSTER_SIZE=3` - minimum number of documents in a single identified cluster;  
 - `COSINE_THRSH=0.1` - minimum cosine distance threshold to say if two vectors are "neighbors";  
