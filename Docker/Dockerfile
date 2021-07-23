FROM python:latest
WORKDIR /app
COPY data_final data_final 
COPY results_final results_final 
COPY final_version_for_tira.py my-software-final.sh input_dir.txt output_dir.txt ./
# install python dependency
RUN pip install requests boilerpy3 elasticsearch pandas; \
# re sys os zipfile; \
# download elasticsearch
   wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.10.1-linux-x86_64.tar.gz; \
# unzip elasticsearch
   tar -xvzf elasticsearch-7.10.1-linux-x86_64.tar.gz; \
# delete .tar.gz file
  rm elasticsearch-7.10.1-linux-x86_64.tar.gz; \
# install java and dos2unix
   apt-get update && apt-get install --no-install-recommends -y default-jre && apt-get install --no-install-recommends -y dos2unix; \
# set JAVA variable
   export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64; \
# convert .sh files to unix
  dos2unix my-software.sh && dos2unix eval.sh;\
# create new user elasticsearch
   useradd elasticsearch; \
# give elasticsearch dir to user elasticsearch
   chown elasticsearch:elasticsearch -R ./elasticsearch-7.10.1; \
# delete all unnecessary
  apt-get -y autoremove
ENTRYPOINT su elasticsearch -c ./elasticsearch-7.10.1/bin/elasticsearch
