#!/bin/bash

db_container_name="local-database"
db_root_password=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
# shellcheck disable=SC2046
docker rm -f $(docker ps -a | grep "${db_container_name}" | awk '{print $1}')
echo "=> using password: ${db_root_password}"
echo "${db_root_password}" > db_password
docker run -dit -e MYSQL_ROOT_PASSWORD="${db_root_password}" --name ${db_container_name} --rm -p 3306:3306 mysql:5.7.29
