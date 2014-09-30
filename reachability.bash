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
host=${1:?"Must specify host"}
timeout=${2:-10}

is_reachable ()
{
	ping -c 1 -w 5 $host &>/dev/null
}

print_reachable ()
{
	printf "$(date)\t${host} is reachable.\n"
}

print_unreachable ()
{
	printf "$(date)\t${host} is unreachable.\n"
}

if is_reachable; then
   print_reachable
   state=reachable
else
   print_unreachable
   state=unreachable
fi

while true; do
	case $state in
		reachable)
			if ! is_reachable; then
				print_unreachable
				state=unreachable
			fi	
			;;
		unreachable)
			if is_reachable; then
				print_reachable
				state=reachable
			fi	
			;;
	esac
	sleep $timeout
done
