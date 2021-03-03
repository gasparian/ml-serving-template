#!/bin/bash
ID=$(docker ps -aqf name=ml-serving_1 | head -n 1)
docker exec $ID python3 ./consumers/fasttext/test_task.py 2> /dev/null
if [ "$?" != 0 ] 
then 
    echo " ============================[ Tests failed ]============================= "
    exit 1
fi
echo " ============================[ Tests passed ]============================= "
