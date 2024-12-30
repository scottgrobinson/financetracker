#!/bin/sh

cd /usr/src/app
pip3 install -r requirements.txt

exec "$@"
