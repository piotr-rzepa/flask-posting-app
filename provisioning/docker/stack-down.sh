#!/bin/bash

# export DOCKER_BUILDKIT=1

docker -v 2> /dev/null

if [ $? -ne 0 ]
then
    echo "Cannot run docker commands. Is the docker daemon running?"
    exit 1
fi
echo "Removing stack..."

docker compose down \
            --remove-orphans \
            --volumes

echo "Stack removed"
