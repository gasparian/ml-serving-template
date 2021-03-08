# ml-serving-template  
Serving large ml models independently and asynchronously via message queue and kv-storage for communication with multiple services.  

<p align="center"> <img src="https://github.com/gasparian/ml-serving-template/blob/main/pics/logo3.jpg" height=320/> </p>  

I think many of us are used to place trained ML models for inference right inside the web app with the rest of the logic. Usually, you load the model once, when the app is started, and then run smth like `predict` method from the API handlers.  
And you can keep doing that, when your models are small enough (like simple image classifiers/detectors) and/or you don't need to query a big amount of data to perform the calculations.  
**But** the problems start when you're trying to serve really large model, like some modified ResNets or modern [transformers](https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)), that can easily take >1..10 Gb of RAM/vRAM.  
Or you need to perform some heavy map-reduce operation. At this case, it can become too resource-consuming to scale your app coupled with such complex stuff.  
So I propose a pretty simple (and obvious) solution - just decouple the heavy model and the rest app logic and create a separate inference service that can be called from other apps asynchronously via **RPC**.  
**Which gives you at least one important thing: you'll be able to independently scale client services, inference services, message bus and cache.**  
This repo is a template that you can look at and use some ideas or implementation details in your projects.  

Key points:  
 - implements publish/subscribe interaction model via message queue and kv-storage;  
 - uses [rabbitmq](https://www.rabbitmq.com/) for sending queries from client apps (producers) to the inference services (consumers);  
 - uses [redis](https://redis.io/) for temporarily storing inference results so the producers can grab them. Here the client subscribes to the redis keyspace events and wait until the desired key has been created;  
 - uses `pickle` for serialization;  
 - producer service only needs to implement a [predictor class](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml_serving/inference.py) and just pass it to the [runner](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml_serving/message_processing.py) on it's side. So basically, you don't need to think about communication internals. See the **[library](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml_serving)** to get more context;  
 - uses `*.env` files to hold all needed configuration parameters: [main config](https://github.com/gasparian/ml-serving-template/blob/main/variables.env) and [services configs](https://github.com/gasparian/ml-serving-template/blob/main/consumers/fasttext/variables.env);  

And it's always better to look at example code by yourself:  
 - check out the [library](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml-serving);  
 - example producer - [short-texts-clustering service](https://github.com/gasparian/ml-serving-template/blob/main/producers/short-texts-clustering);  
 - example consumer - [fasttext inference service](https://github.com/gasparian/ml-serving-template/blob/main/consumers/fasttext);  

### Building and running example services  

All you need to run any service here is just to execute this script with the docker-compose commands from the corresponding service dir:  
```
./run_compose.sh
```  
The steps are as follows:  
 - check that configs looks good for you (all in `*.env` files);  
 - first run rabbit and redis from the root dir;  
 - then you're need to run consumer - our fasttext inference service;  
 - and finally run the producer service for text clustering, which just a REST API app;  
 - after you're done - you can run producer's test to ensure that all works fine - `./docker_test.sh`;  

### Reference  

If you want to install library with wrappers locally:  
```
cd ./ml-serving
python3.8 -m pip install .
```  
Here are small code snippets from the examples above.  
On the **consumer** side, you just need to first implement the predictor interface:  
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
from ml_serving.message_processing import start_consume_messages

from config import FasttextConfig
from predictor import Predictor

config = FasttextConfig()
predictor = Predictor(config.model_path)
start_consume_messages(config, predictor) # <-- blocking
```  

On the **producer** side, you just need to replace the usual model initialization and prediction code with the serving client and RPC:  
```python
...
from ml_serving import ServingClient

from .config import ClusteringConfig

...
class FasttextExtractor(TextFeaturesExtractor):
    def __init__(self, preprocessor: Callable[[str], str], config: ClusteringConfig):
        super().__init__(preprocessor)
        self.__model = ServingClient(config)

    def get_features(self, inp: Union[List[str], np.ndarray]) -> Any:
        key = self.__model.run_prediction(inp)
        return self.__model.wait_answer(key)
```  

### Library API  
*TODO*  
