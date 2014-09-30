#!/bin/bash

property="org.gnome.settings-daemon.peripherals.mouse middle-button-enabled"

if [ "$(gsettings get $property)" == "true" ]; then
	gsettings set $property false
else
	gsettings set $property true
fi
