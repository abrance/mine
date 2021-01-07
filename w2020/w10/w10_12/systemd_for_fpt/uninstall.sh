#!/bin/bash

systemctl disable new-fpt
systemctl stop new-fpt

echo "del systemd service success!"
