FROM mysql:latest
#
# set root password for local execution:
#
ENV MYSQL_ROOT_PASSWORD=abc123
#
# NOTE: changing to port 3307 since I already have MySQL installed
# and running locally on its own. So this docker image is a second
# version. 
#
ENV MYSQL_TCP_PORT=3307
#
# expose the port needed to connect to MySQL server:
#
EXPOSE 3307
#
# start server when container runs:
#
CMD ["mysqld"]
