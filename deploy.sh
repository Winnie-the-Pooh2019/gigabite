#!/bin/bash



docker build -t chat .

docker run --name chat chat -m max -v