#!/bin/bash


docker stop chat
docker rm chat

docker build -t chat .

docker run --name chat -d chat -m max -v