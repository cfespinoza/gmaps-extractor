#!/bin/bash

# gmaps-db -c $(pwd)/resources/db_ops_config.json
nohup gmaps-url-scrapper -c $(pwd)/resources/urls_execution_config.json &
# nohup gmaps-zip-scrapper -c $(pwd)/resources/zip_execution_config.json &
# insert into execution_info (zip_code, country, place_type) select zip_code as zip_code, country as country, "Restaurants,Bars" as place_type from zip_code_info