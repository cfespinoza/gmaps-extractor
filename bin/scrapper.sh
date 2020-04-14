#!/bin/sh -e

: ${EXECUTION_CONFIGURATION_FILE:?"Need to set EXECUTION_CONFIGURATION_FILE env. Variable can not be empty and should contains the absolute path to execution ocnfiguration file"}
: ${EXECUTION_TYPE:?"Need to set EXECUTION_TYPE env. Variable can not be empty and indicates which execution launch: 'extract_urls' or 'extract_places'"}

if [ "${EXECUTION_TYPE}" = "extract_urls" ]; then
  gmaps-url-scrapper -c "${EXECUTION_CONFIGURATION_FILE}"
elif [ "${EXECUTION_TYPE}" = "extract_places" ]; then
  gmaps-zip-scrapper -c "${EXECUTION_CONFIGURATION_FILE}"
else
  echo "[ERROR] EXECUTION_TYPE: -${EXECUTION_TYPE}- is not supported"
  exit 1
fi