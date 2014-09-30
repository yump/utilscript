#!/bin/bash

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
