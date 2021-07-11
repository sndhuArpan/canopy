#!/bin/sh

find ~ -regextype sed -regex ".*\.log" -exec rm -f 0 {} \;