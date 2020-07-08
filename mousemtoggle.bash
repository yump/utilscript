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

emu_prop="libinput Middle Emulation Enabled"

device_ids () {
    xinput --list \
        | grep 'slave *pointer' \
        | grep -vi 'virtual' \
        | sed -r 's/.*id=([[:digit:]]+).*/\1/'
}

on () {
    device_ids | while read device_id; do
        xinput set-prop $device_id "$emu_prop" 1
    done
}

off () {
    device_ids | while read device_id; do
        xinput set-prop $device_id "$emu_prop" 0
    done
}

toggle () {
    device_ids | while read device_id; do
        if xinput list-props $device_id | grep "$emu_prop (" | grep -q '0$'; then
            xinput set-prop $device_id "$emu_prop" 1
        else
            xinput set-prop $device_id "$emu_prop" 0
        fi
    done
}

usage () {
    echo "Usage: mousemtoggle.bash [on|off]" 1>&2
    exit 1
}

if (( $# == 1 )); then
    if [[ "$1" == "on" ]]; then
        on
    elif [[ "$1" == "off" ]]; then
        off
    else
        usage
    fi
elif (( $# == 0 )); then
    toggle
else
    usage
fi
