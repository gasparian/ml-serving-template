# ml-serving-template
Serving large ml models independently via message queue for communication with other services.  

<p align="center"> <img src="https://github.com/gasparian/ml-serving-template/blob/main/pics/logo3.jpg" height=320/> </p>  

*TODO*  

### Reference  

Installing module with helpers:  
```
cd ./common
python3.8 -m pip install .
```  

Running rabbit-mq and redis via docker-compose (preferable way):  
```
./run_compose.sh
```  

And finally you only need to choose and run producers and consumers apps.  

Example producer:  
 - [short-texts-clustering service](https://github.com/gasparian/ml-serving-template/blob/main/producers/short-texts-clustering)  

Example consumer:  
 - [fasttext inference](https://github.com/gasparian/ml-serving-template/blob/main/consumers/fasttext)  

### API  
*TODO*

### TODO  
 - update all readme's;  
 - add ability to clusterize based on passed clusters names;  
 - add load tests via `locust` to the clusterizer;  
