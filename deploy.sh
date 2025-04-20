#!/bin/bash



docker container build -t chat .

docker run --name chat chat -m max -v