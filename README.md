# ml-serving-template
Serving large ml models via message queue and key-value storage.  

<p align="center"> <img src="https://github.com/gasparian/ml-serving-template/blob/main/pics/logo.jpg" height=320/> </p>  

### Motivation  
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
 - fill the readme!;  
 - test with the real fasttext model and API client service;  
 - think of an additional wrapper for producer;  
