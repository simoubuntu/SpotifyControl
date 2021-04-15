#!/bin/bash
curl -X "POST" "http://localhost:8080/onevent" --data "$TRACK_ID,$PLAYER_EVENT" --silent --output /dev/null