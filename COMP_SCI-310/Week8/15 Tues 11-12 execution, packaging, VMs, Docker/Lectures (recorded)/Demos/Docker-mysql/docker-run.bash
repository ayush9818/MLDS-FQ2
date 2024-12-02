#!/bin/bash
#
# Linux/Mac BASH script to run docker container
#
# NOTE: using port 3307 because the Dockerfile exposes
# that port since I already have MySQL running locally.
#
docker run -d -p 3307:3307 --name mysql --rm docker-mysql
