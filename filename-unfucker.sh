#!/bin/bash

targetdir="$1"
if ! [ -d "$targetdir" ]; then
	echo "must specify a valid search directory"
	exit 1
fi

echo "Fixing filenames with leading spaces"
find "$targetdir" | grep -E '^[[:space:]]+.*$' | while read line; do
	echo "'${line}'"
done

echo "Fixing filenames with trailing space"
find "$targetdir" | grep -E '^.*[[:space:]]+$' | while read line; do
	echo "'${line}'"
done

echo "Fixing filenames with space inbetween the basename and extension"
find "$targetdir" | grep -E '^.*[[:space:]]+\..*$' | while read line; do
	echo "'${line}'"
done

