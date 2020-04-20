#!/bin/bash

docker build -t get-secret .

docker run -it --rm \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN \
    -e AWS_DEFAULT_REGION \
    -v ~/:/home \
    -u $(id -u):$(id -g) \
    --name get-secret \
    get-secret python build_npmrc.py
