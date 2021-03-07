### Reference  

This is a simple service for extracting features from text via [fasttext model](https://fasttext.cc/docs/en/crawl-vectors.html) pretrained on the "common-crawl" dataset.  
The pipeline is:  
 - listen for messages in message queue (rabbitmq at this case);  
 - on every message apply simple preprocessing and make the representation vectors, by calculating the average. min and max of word-vectors;  
 - write out the answer to the kv-storage (redis at this case);  

### Building and running  

Run locally:  

```
python3 ./consumers/fasttext/src/main.py
```  

Or build and run via docker-compose:  
```
docker-compose build/up/down
```  

You also can run a super-small test on running container, which just publishes the message to queue and read the results for kv-storage:  
```
./docker_test.sh
```  