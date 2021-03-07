# ml-serving-template  
Serving large ml models independently via message queue and kv-storage for communication with multiple services.  

<p align="center"> <img src="https://github.com/gasparian/ml-serving-template/blob/main/pics/logo3.jpg" height=320/> </p>  

I think many of us are used to place trained ML models for inference right inside the web app with the rest of the logic. Usually, you load it once, when the app is started, and run smth like predict inside API handler functions.  
And you can keep doing that, when your models are small enough (like simple image classifiers/detectors) and/or you don't need to query a big amount of data to perform the calculations.  
**But** the problems start when you're trying to serve some really large model, like some modified ResNets or modern [transformers](https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)), that can easily take >1..10 Gb of RAM/vRAM. Or you need to perform some heavy map-reduce operation. And at this case, it can become too resource-consuming to scale your app coupled with such complex stuff.
So I propose a pretty simple (and obvious) solution - just decouple the heavy model and the rest app logic and create a separate inference service that can be called from other apps via RPC.  
Here is a template that you can look at and use some ideas or implementation details in your projects.  

### Reference  

Key points:  
 - implements publish/subscribe interaction model via message queue and kv-storage;  
 - uses [rabbitmq](https://www.rabbitmq.com/) for sending queries from client apps (producers) to the inference services (consumers);  
 - uses [redis](https://redis.io/) for temporarily storing inference results so the producers can grab them. Here the client just subscribes to the redis keyspace events and wait until the desired key has been created;  
 - uses `pickle` for serialization;  
 - producer service only needs to implement a [predictor class](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml_serving/inference.py) and just pass it to the [runner](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml_serving/message_processing.py) on it's side. So basically, you don't need to think about communication internals;  
 - uses `*.env` files to hold configuration parameters: [main config](https://github.com/gasparian/ml-serving-template/blob/main/variables.env) and [services configs](https://github.com/gasparian/ml-serving-template/blob/main/consumers/fasttext/variables.env);  

It's actually better to look at code by yourself:  
 - check out the [module](https://github.com/gasparian/ml-serving-template/blob/main/ml-serving/ml-serving) with all helpers;  
 - example producer - [short-texts-clustering service](https://github.com/gasparian/ml-serving-template/blob/main/producers/short-texts-clustering);  
 - example consumer - [fasttext inference service](https://github.com/gasparian/ml-serving-template/blob/main/consumers/fasttext);  

Installing module with helpers locally:  
```
cd ./ml-serving
python3.8 -m pip install .
```  

### Building and running examples  

All you need to run any service here is just to execute this script with docker-compose commands from the corresponding root dir:  
```
./run_compose.sh
```  
The steps are as follows:  
 - check that configs looks good for you (all in `*.env` files);  
 - first run rabbit and redis from the root dir;  
 - then you're need to run consumer - our fasttext inference service;  
 - and finally run the producer service for text clustering, which just a REST API app;  
 - after you're done - you can run producer's test to ensure that all works fine - `./docker_test.sh`;  
