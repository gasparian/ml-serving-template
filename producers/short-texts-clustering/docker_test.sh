#!/bin/bash
PROJECT_NAME="semantic-clustering"
ID=$(docker ps -aqf name=${PROJECT_NAME} | head -n 1)
TEST_RES=$(docker exec $ID python3 ./test/tests.py)
TEST_RES="${TEST_RES: -1}"
if [[ $TEST_RES == "0" ]]
then 
    echo " ========================[ Tests failed ]============================= "
    exit 1
fi
echo " ============================[ Tests passed ]============================= "
