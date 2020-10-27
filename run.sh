#!/bin/bash

docker build -t get-secret .

docker run -it \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN \
    -e AWS_DEFAULT_REGION \
    -v $PWD/test/home:/home \
    -u $(id -u):$(id -g) \
    --name get-secret \
    get-secret python build_npmrc.py $1

docker cp get-secret:/home/.npmrc .npmrc
echo wrote test/home/.npmrc

docker rm get-secret >/dev/null

