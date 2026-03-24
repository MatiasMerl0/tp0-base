#!/bin/bash

MSG="test_message"
NETWORK="tp0_testing_net"
SERVER="server"
PORT=12345
IMAGE="netcat:latest"

docker build -f netcat.Dockerfile -t "$IMAGE" . -q

RESPONSE=$(echo "$MSG" | docker run --rm -i --network "$NETWORK" "$IMAGE" -w 3 "$SERVER" "$PORT")

if [ "$RESPONSE" = "$MSG" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
