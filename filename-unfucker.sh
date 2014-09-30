#!/bin/bash
# Copyright (C) 2014 Russell Haley
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

