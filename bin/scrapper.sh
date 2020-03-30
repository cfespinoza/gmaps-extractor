#!/bin/sh -e

: ${BEGIN:?"Need to set BEGIN env. variable non-empty"}
: ${END:?"Need to set END env. variable non-empty"}
: ${MEDIA:?"Need to set MEDIA env. variable non-empty"}
RESULTS_PATH=${RESULTS_PATH:-/results}

scrapper -b "${BEGIN}" -e "${END}" -m "${MEDIA}" -r "${RESULTS_PATH}"