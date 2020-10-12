#!/bin/bash

DIR="$( cd "$( dirname "$0"  )" && pwd  )"
cp $DIR/new-fpt.service /usr/lib/systemd/system
systemctl enable new-fpt
systemctl restart new-fpt

echo "add systemd service success!"
