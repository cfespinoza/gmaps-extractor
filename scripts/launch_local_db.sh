#!/bin/bash

db_container_name="local-databases"
existing_db_container=$(docker ps | grep ${db_container_name} | awk '{print $1}')

if [[ -z $existing_db_container ]]
then
  echo "no db container found"
else
  echo "db container found: ${existing_db_container}"
  echo "db container will be deleted..."
  deleted_container_id=$(docker rm -f "${existing_db_container}")
  if [[ "${deleted_container_id}" == "${existing_db_container}" ]]
  then
    echo "deleted corredtly"
  else
    echo "something went wrong trying to delete previous container: ${existing_db_container}"
  fi
fi

docker run -dit -e MYSQL_ROOT_PASSWORD=1234 --name local-database --rm -p 3306:3306 mysql:8.0.19
