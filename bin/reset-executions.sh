#!/bin/bash

CWD=$(pwd)
CONFIG_FILE=${1:-$CWD/resources/db_ops_config.json}

gmaps-db -c "${CONFIG_FILE}" -o reset-executions