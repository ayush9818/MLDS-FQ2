Docker-client: interactive demo with project 02 of CS 310

build
run
python3 main.py

################################

Docker-MySQL: runs MySQL in the background on port 3307 (since
I have MySQL already installed and running on port 3306)

build
run

docker ps
docker exec -it mysql bash
mysql -u root -p
  <enter pwd abc123>
show databases;
exit
exit

<< connect with MySQL workbench, localhost, port 3307, root, abc123 >>
show databases;

docker stop mysql

########################################
