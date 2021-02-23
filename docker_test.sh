#!/bin/bash
ID=$(docker ps -aqf name=ml-serving_1 | head -n 1)
docker exec $ID python3 ./producer/test_task.py 1> /dev/null 2>&1
if [ "$?" != 0 ] 
then 
    echo "Test failed"
    exit 1
fi
echo "Test succeed"
