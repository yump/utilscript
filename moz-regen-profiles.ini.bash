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

help="\
moz-regen-profiles.ini.bash: generate a valid profiles.ini for the
Firefox or Thunderbird profiles in the current directory.

Usage: 
	moz-regen-profiles.ini.bash [-h | --help]
"

if [[ $# -ne 0 ]]; then
	echo "$help"
	exit 1
fi

profilenum=0

echo "[General]"
echo "StartWithLastProfile=0"
echo ""

for file in ./*; do
	if [[ $file =~ [0-9a-zA-Z]{8}\..+ ]]; then
		if [ -d "$file" ]; then
			echo "[Profile${profilenum}]"
			echo "Name=${file#./*.}"
			echo "IsRelative=1"
			echo "Path=${file#./}"
			echo "Default=0"
			echo ""
			profilenum=$(( $profilenum + 1 ))
		fi
	fi
done
