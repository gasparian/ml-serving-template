# ml-serving-template
Serving large ml models via message queue and key-value storage.  

<p align="center"> <img src="https://github.com/gasparian/ml-serving-template/blob/main/pics/logo.jpg" height=300/> </p>  

### Building and running  

```
docker-compose build/up/down
```  

```
python -m app
```  

### Testing  
```
/usr/bin/python3.8 -m venv ./env
source ./env/bin/activate
python -m pip install -r requirements.txt
```  

```
mypy ./app
```  
