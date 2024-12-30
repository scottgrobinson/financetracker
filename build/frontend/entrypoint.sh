#!/bin/sh

cd /usr/src/app
npm -i install

exec "$@"
