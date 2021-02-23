#!/bin/bash
ID=$(docker ps -aqf name=ml-serving_1 | head -n 1)
docker exec -it $ID bash