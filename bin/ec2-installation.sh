#!/bin/bash -e

cwd=$(pwd)
repository_name="gmaps-extractor"


echo "============================================================================="
echo "===== installing system dependencies"
echo "============================================================================="

curl https://intoli.com/install-google-chrome.sh | bash
sudo mv /usr/bin/google-chrome-stable /usr/bin/google-chrome

echo "----- check chrome installation and version"
google-chrome --version && which google-chrome

wget https://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_linux64.zip
unzip chromedriver_linux64.zip

sudo yum install -y git python3

echo "============================================================================="
echo "===== system dependencies installed"
echo "============================================================================="

echo "##########################################################################################################"

echo "============================================================================="
echo "===== clonning repository"
echo "============================================================================="

git clone https://github.com/cfespinoza/${repository_name}

echo "============================================================================="
echo "===== repository cloned"
echo "============================================================================="

echo "##########################################################################################################"

echo "============================================================================="
echo "===== building and installing project"
echo "============================================================================="

echo "----- entering project"
cd ${cwd}/${repository_name}
echo "----- installing pip dependencies"
# pip3 install -U setuptools
pip3 install -r requirements.txt

echo "----- building project"
python3 setup.py sdist

echo "----- installing project"
pip3 install dist/*.tar

echo "============================================================================="
echo "===== project built and installed"
echo "============================================================================="

echo "##########################################################################################################"

echo "============================================================================="
echo "===== launched process"
echo "============================================================================="


python3 $(pwd)/gmaps/gmaps_extractor.py -cp 48005 -d $(pwd)/resources/chromedriver -t Restaurants Bars -p 1 -n 3 -m remote -e 2 -dc $(pwd)/resources/dbconfig.json -d $(pwd)/chromedriver

