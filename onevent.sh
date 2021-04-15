#!/bin/bash
curl -X "POST" "http://localhost:8080/onevent" --data $TRACK_ID --silent --output /dev/null