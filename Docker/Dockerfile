FROM python:latest
WORKDIR /app
COPY data data 
COPY results results 
COPY eval.sh evaluation.py indexing_full.py my-software.sh touche2020-task2-relevance-withbaseline(1).qrels ./
# install python dependency
RUN pip install requests boilerpy3 elasticsearch pandas; \
# download elasticsearch
   wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.10.1-linux-x86_64.tar.gz; \
# unzip elasticsearch
   tar -xvzf elasticsearch-7.10.1-linux-x86_64.tar.gz; \
# delete .tar.gz file
  rm elasticsearch-7.10.1-linux-x86_64.tar.gz; \
# install java
   apt-get update && apt-get install --no-install-recommends -y default-jre; \
# set JAVA variable
   export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64; \
# create new user elasticsearch
   useradd elasticsearch; \
# give elasticsearch dir to user elasticsearch
   chown elasticsearch:elasticsearch -R ./elasticsearch-7.10.1; \
# delete all unnecessary
  apt-get -y autoremove
CMD su elasticsearch -c ./elasticsearch-7.10.1/bin/elasticsearch
