# ml-serving-template
Serving large ml models independently via message queue for communication with other services.  

<p align="center"> <img src="https://github.com/gasparian/ml-serving-template/blob/main/pics/logo2.jpg" height=320/> </p>  

*TO DO*  

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

### TO DO  
 - **drop redis and make messages exchange only through message broker**;  
 - add readme to the consumers;  
 - update readme here;  
 - github actions badges! (build / test);  
