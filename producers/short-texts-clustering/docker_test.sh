#!/bin/bash
PROJECT_NAME="semantic-clustering"

echo " =============================> Tests start <============================= "
echo " ============================[ run container ]============================ "
docker run --rm -d -v /samsung_drive/fasttext:/fasttext --env-file ./variables.env -e WORKERS=1 --name ${PROJECT_NAME} ${PROJECT_NAME}:latest
sleep 60 # wait for service launch
echo " =============================[ run tests ]=============================== "
ID=$(docker ps -aqf name=${PROJECT_NAME} | head -n 1)
TEST_RES=$(docker exec $ID python3 ./src/test/tests.py)
TEST_RES="${TEST_RES: -1}"
docker stop $ID
echo " ==========================[ container stopped ]========================== "
if [[ $TEST_RES == "0" ]]
then 
    echo " ========================[ Tests failed ]============================= "
    exit 1
fi
echo " ============================[ Tests passed ]============================= "
echo " =============================> Build end <=============================== "
