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
filename-unfucker.bash: Remove weird whitespace from file names

Usage:
    filename-unfucker.bash <directory>

Will remove leading whitespace, trailing whitespace, and whitespace
before the file extension from all files in <directory>, recursively.
"

fixup () {
	local dirpart="${1%/*}"
	local fn="${1##*/}"
	newfn="$(echo "${fn}" | fixup_leading | fixup_preext | fixup_trailing)"
	echo "${dirpart}/${newfn}"
}

fixup_leading () {
	sed -r 's/^\s+//'
}

fixup_trailing () {
	sed -r 's/\s+$//'
}

fixup_preext () {
	sed -r 's/\s(\.[^.]+$)/\1/'
}


targetdir="$1"
if ! [ -d "$targetdir" ]; then
	echo "$help"
	exit 1
fi

printf "Fixing filenames with leading spaces\n"
# Note: Temporary IFS="\n" required due to leading/trailing spaces.
find "$targetdir" -regex '^.*/\s+[^/]+$' | while IFS="\n" read line; do
	echo mv -i "\"${line}\"" "\"$(fixup "${line}")\""
	mv -i "${line}" "$(fixup "${line}")"
done

printf "\nFixing filenames with trailing space\n"
find "$targetdir"  -regex '^.*/[^/]+\s+$' | while IFS="\n" read line; do
	echo mv -i "\"${line}\"" "\"$(fixup "${line}")\""
	mv -i "${line}" "$(fixup "${line}")"
done

printf "\nFixing filenames with space inbetween the basename and extension\n"
find "$targetdir" -regex '^.*/[^/]+\s+\.[^.]+$' | while IFS="\n" read line; do
	echo mv -i "\"${line}\"" "\"$(fixup "${line}")\""
	mv -i "${line}" "$(fixup "${line}")"
done

