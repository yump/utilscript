#!/bin/sh

head -c 64k /dev/urandom | aplay -f cd 
sleep "$@"
aplay -f cd /dev/urandom
