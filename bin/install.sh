#!/bin/bash -e

printf  "\n---> sourcing venv"
source venv/bin/activate
printf " venv activated <---\n"
python setup.py sdist
pip install dist/gmaps-extractor-0.1.0.tar.gz
