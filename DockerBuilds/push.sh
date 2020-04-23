#!/usr/bin/env bash
# bach script to automatically remove the image/container to
docker-compose -f ./ComposeLORIS22.0.0.yml push lorisdb
docker-compose -f ./ComposeLORIS22.0.0.yml push loris
docker-compose -f ./ComposeLORIS22.0.0.yml push lorisdbsetup
