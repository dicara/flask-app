#!/bin/bash
docker ps -a -q -f 'status=exited' | xargs -r docker rm
docker images | grep '<none>' | awk '{print $3}' | xargs -r docker rmi
docker images -q --filter="dangling=true" | xargs -r docker rmi
docker images | grep "^<none>" | awk "{print $3}" | xargs -r docker rmi