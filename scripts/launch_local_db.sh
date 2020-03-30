#!/bin/bash

db_container_name="local-database"
docker rm -f $(docker ps -a | grep "${db_container_name}" | awk '{print $1}')
docker run -dit -e MYSQL_ROOT_PASSWORD=1234 --name local-database --rm -p 3306:3306 mysql:5.7.29
