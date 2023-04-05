#!/bin/bash 

mkdir ~/spark
cd ~/spark
wget https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
tar xzfv openjdk-11.0.2_linux-x64_bin.tar.gz
echo 'export JAVA_HOME="${HOME}/spark/jdk-11.0.2"' >> ~/.bashrc 
echo 'export PATH="${JAVA_HOME}/bin:${PATH}"' >> ~/.bashrc 
rm openjdk-11.0.2_linux-x64_bin.tar.gz


wget https://dlcdn.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz
tar xzfv spark-3.3.2-bin-hadoop3.tgz
rm spark-3.3.2-bin-hadoop3.tgz
echo 'export SPARK_HOME="${HOME}/spark/spark-3.3.2-bin-hadoop3"' >> ~/.bashrc 
echo 'export PATH="${SPARK_HOME}/bin:${PATH}"' >> ~/.bashrc 

echo 'export PYTHONPATH="${SPARK_HOME}/python/:$PYTHONPATH"' >> ~/.bashrc 
echo 'export PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9.5-src.zip:$PYTHONPATH"' >> ~/.bashrc 

cd ..

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



