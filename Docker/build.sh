#!/bin/bash

CONTAINER=monroe-cli

docker pull $(awk '/FROM/{ print $2 }' Dockerfile)
docker build --rm --no-cache -t ${CONTAINER} . && echo "Finished building ${CONTAINER}"
