@echo off
REM
REM Windows BATCH script to build docker container
REM
@echo on
docker rmi docker-mysql
docker build -t docker-mysql .
