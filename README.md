# ml-serving-template
Serving large ml models via message queue and key-value storage.  

<p align="center"> <img src="https://github.com/gasparian/ml-serving-template/blob/main/pics/logo.jpg" height=320/> </p>  

### Reference  
*TO DO*

### Building and running  

Running via docker-compose (more preferable):  
```
./run_compose.sh
```  
Or run locally:  

```
python3 -m consumer
```  
You also can run a small test on running container using the producer:  
```
./docker_test.sh
```  

### TO DO  
 - how to merge several env files?;  
 - deal with `common` module distribution across all consumers and producers;  
 - migrate `short-texts-clustering` to falcon and bjoern;  
 - add mocking and unittests to `short-texts-clustering`;  
 - add readme to the consumers;  
 - update readme here;  
 - think of an additional wrapper for producer;  
