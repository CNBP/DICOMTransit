#!/usr/bin/env bash
# bach script to automatically remove the image/container to
# Remove all pre-existing volumes.
docker volume rm $(docker volume ls)

docker-compose -f ./ComposeCNBP.yml build --pull
docker-compose -f ./ComposeCNBP.yml up

