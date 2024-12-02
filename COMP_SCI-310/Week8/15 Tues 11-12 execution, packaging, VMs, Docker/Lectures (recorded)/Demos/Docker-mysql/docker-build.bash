#!/bin/bash
#
# Linux/Mac BASH script to build docker container
#
docker rmi docker-mysql
docker build -t docker-mysql .
