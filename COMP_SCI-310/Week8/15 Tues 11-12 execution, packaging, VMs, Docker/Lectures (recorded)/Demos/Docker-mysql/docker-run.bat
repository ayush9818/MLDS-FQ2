@echo off
REM
REM Windows BATCH script to run docker container
REM
@echo on
docker run -d -p 3307:3307 --name mysql --rm docker-mysql
