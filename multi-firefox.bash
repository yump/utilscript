#!/bin/bash

invname=$(basename "$0")
version=${invname#ff-}

cd "${HOME}/opt/firefox/${version}" && exec ./firefox "$@"
