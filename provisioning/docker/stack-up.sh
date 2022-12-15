#!/bin/bash

docker -v 2> /dev/null

if [ $? -ne 0 ]
then
    echo "Cannot run docker commands. Is the docker daemon running?"
    exit 1
fi

docker compose \
            --env-file .env \
            up \
            --build \
            --force-recreate \
            --remove-orphans \
            --renew-anon-volumes
