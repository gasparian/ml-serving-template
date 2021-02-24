#!/bin/bash
ID=$(docker ps -aqf name=semantic-clustering | head -n 1)
docker exec -it $ID bash