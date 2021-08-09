#!/bin/bash

sudo docker login rg.fr-par.scw.cloud/djnd -u nologin -p $SCW_SECRET_TOKEN

# BUILD AND PUBLISH PARSER
sudo docker build -f Dockerfile -t parlaparser-ua:latest .
sudo docker tag parlaparser-ua:latest rg.fr-par.scw.cloud/djnd/parlaparser-ua:latest
sudo docker push rg.fr-par.scw.cloud/djnd/parlaparser-ua:latest
