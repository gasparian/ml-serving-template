# ml-serving-template
Serving large ml models via message queue and producer-consumer interaction model.  

### Building and running  

```
docker-compose build/up/down
```  

```
python -m app
```  

### To do  
 - run two parallel processes: for producer (falcon app) and consumer (fasttext prediction);  
 - add basic service tests (mock the service?);  
 - add load tests;  

### Useful links  
 - https://www.rabbitmq.com/tutorials/tutorial-one-python.html  
 - https://hub.docker.com/_/rabbitmq  
 - https://hub.docker.com/_/redis  
 - use [falcon](https://falcon.readthedocs.io/en/stable/) and [bjoern](https://github.com/jonashaag/bjoern). See the [example](https://alexpnt.github.io/2018/01/06/fast-inference-falcon-bjoern/)  
