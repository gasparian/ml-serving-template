# ml-serving-template
Serving large ml models via message queue and key-value storage.  

<p align="center"> <img src="https://github.com/gasparian/ml-serving-template/blob/main/pics/logo.jpg" height=320/> </p>  

### Reference  
*TO DO*

### Building and running  

Running rabbit-mq and redis via docker-compose (preferable way):  
```
./run_compose.sh
```  

Example producers:  
 - [short-texts-clustering service](https://github.com/gasparian/ml-serving-template/blob/main/producers/short-texts-clustering)  

Example consumers:  
 - [fasttext inference](https://github.com/gasparian/ml-serving-template/blob/main/consumers/fasttext)  

### TO DO  
 - migrate `short-texts-clustering` to falcon and bjoern;  
 - add mocking and unittests to `short-texts-clustering`;  
 - add readme to the consumers;  
 - update readme here;  
 - github actions badges! (build / test);  
