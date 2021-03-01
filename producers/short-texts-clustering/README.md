### Short texts clustering service  
Use-case: clustering small datasets of "twitter-length" texts.  
The output contains cluster id for each input text and generated cluster title.  
Works fine with english, in case of other languages, you'll need to change the language model and tune preprocessing parameters.  

### Recipe  

 1. Extract tfidf features based on chars ngrams.  
 2. Build data points hierarchy via single-linkage / complete-linkage algorithm.  
 3. Form flat clusters from the hierarchy, finding optimal threshold value based on the minimum std of cluster's labels counts.  
 4. Extract the most freuqent ngrams for each of the clusters.  
 5. Unite clusters by measuring the semantic similarity between the most frequent ngrams via some language model.  

**Remember**: since here is used hierarchical clustering, the algorithmic complexity estimate is pretty bad, so expect decent performance on several hundreds of data points.  

### Building and running  
Download pretrained [fasttext model](https://fasttext.cc/docs/en/crawl-vectors.html).  
Manual build and run docker:  
```
docker build -t semantic-clustering:latest .
docker run --rm -it \
           -v ${FASTTEXT_PATH}:/fasttext \
           --env-file ./variables.env \
           -p 8010:5000 semantic-clustering:latest
```  
Or do the same but via docker-compose (don't forget to modify `docker-compose.yaml`):  
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
 * POST: `/get-clusters/{tfidf | fasttext}` - methods for getting clusters by input json data. The only difference is the feature extractor - you have an option to go with tfidf on chars ngrams or fasttext embeddings;  

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
        "titles": {"-1": "cluter title", "1": "another one", ...},
        "labels": {"-1": ["id1", "id2", ...], "1": ["id3", "id4"], ...}
   }
}
```  

#### Useful links:  
   - [fasttext models](https://fasttext.cc/docs/en/crawl-vectors.html) pretrained on the "common-crawl" dataset;  
   - [great article by Google engineer on how he made news-aggregator](https://danlark.org/2020/07/31/news-aggregator-from-scratch-in-2-weeks/)  
