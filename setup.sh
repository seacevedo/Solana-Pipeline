#!/bin/bash 

git clone https://github.com/seacevedo/Solana-Pipeline.git
cd Solana-Pipeline

sudo apt-get update -y
sudo apt install python3-pip -y
sudo apt-get install python3-venv -y
python3 -m venv solana-pipeline-env
source solana-pipeline-env/bin/activate
pip3 install -r requirements.txt
python3 -m spacy download en_core_web_sm

curl -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/attributes/SERVICE_ACCOUNT_JSON" >> service_account_keyfile.json



