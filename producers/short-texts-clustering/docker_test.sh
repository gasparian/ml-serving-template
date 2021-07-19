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

	# docker run --rm -it \
    #     -v $(extractor_path):/fasttext \
    #     --env-file ./variables.env \
    #     -m 8192M \
    #     --cpus=8 \
    #     --name=semantic-clustering \
    #     --entrypoint /bin/bash \
    #     semantic-clustering:latest \
    #     -c "python3 ./tests/test_api.py"
