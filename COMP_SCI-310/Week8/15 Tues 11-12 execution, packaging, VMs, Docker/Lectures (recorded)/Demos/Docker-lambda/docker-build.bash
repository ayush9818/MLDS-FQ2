#!/bin/bash
#
# Linux/Mac BASH script to build docker container
#
docker rmi lambda-add2
docker build -t lambda-add2 .
