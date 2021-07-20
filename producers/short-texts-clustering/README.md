### Short texts clustering service  
Use-case: clustering small datasets of "twitter-length" texts.  
The output contains cluster id for each input text.  

### Recipe  

Extract fasttext features --> Form clusters using complete-linkage algorithm with cosine distance metric.  

**Remember**: since here is used hierarchical clustering, the algorithmic complexity estimate is pretty bad, so expect decent performance on up to several thousands of data points.  

### Building and running  
Download pretrained [fasttext model](https://fasttext.cc/docs/en/crawl-vectors.html).  
Manual build and run docker:  
```
docker build -t short-texts-clustering:latest .
docker run --rm -it \
           -v ${FASTTEXT_PATH}:/fasttext \
           --env-file ./variables.env \
           -p 8010:5000 short-texts-clustering:latest
```  
Or do the same but via docker-compose (don't forget to modify `docker-compose.yaml`, at least change path to the feature extractor):  
```
docker-compose build
docker-compose up
docker-compose down
```  
Build and test the fresh build right after:  
```
bash ./docker_test.sh
```  

Use `ngrok` for fast testing with the client that needs https:  
```
cp ./ngrok /usr/local/bin/ngrok
ngrok http <PORT>
```  

### API reference  

So here are only 3 endpoints:  
 * GET: `/` - is just for app health check, returns `OK` if app is up and running;  
 * POST: `/api/v1/predict` - methods for getting clusters by input json data;  

IO format for clusters:  
Input:  
```
{
    "id1": "some text",
    "id2": "another text",
    ...
}
```  

Output:  
```
{
   "status": "{success | failed}",
   "result": {
        "labels": {"-1": ["id1", "id2", ...], "1": ["id3", "id4"], ...}
   }
}
```  

#### Useful links:  
   - [great article by Google engineer on how he made news-aggregator](https://danlark.org/2020/07/31/news-aggregator-from-scratch-in-2-weeks/)  
