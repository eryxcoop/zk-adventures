#!/bin/bash

set -e

CONTAINER_NAME="sage"

# Ensure it's right folder
if [[ ! -f "README.md" ]]; then
    echo "Please run this script from the repo root"
fi

# Check container status
CONTAINER_RUNNING=false
CONTAINER_EXISTS_STOPPED=false
if [[ "$(docker ps -q -f name=$CONTAINER_NAME)" ]]; then
    CONTAINER_RUNNING=true
elif [[ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]]; then
    CONTAINER_EXISTS_STOPPED=true
fi



if $CONTAINER_RUNNING; then
    docker kill $CONTAINER_NAME &> /dev/null
    docker rm $CONTAINER_NAME &> /dev/null
fi

if $CONTAINER_EXISTS_STOPPED; then
    docker rm $CONTAINER_NAME &> /dev/null
fi


docker run --platform linux/amd64 \
    -v `pwd`:/home/sage/zk-adventures \
    --name $CONTAINER_NAME \
    -p 8888:8888 \
    sagemath/sagemath:latest sage-jupyter;

