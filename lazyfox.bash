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

# lazyfox.bash: Easy and efficient use of multiple Firefox channels. Can 
#               be run directly, or through symlinks for particular 
#               channels of Firefox.  Firefox channels are downloaded and
#               unpacked as needed.

foxdir="$HOME/opt/firefox"
supported=("release-32" \
            "release-64" \
            "beta-32" \
            "beta-64" \
            "aurora-32" \
            "aurora-64" \
            "nightly-32" \
            "nightly-64")

print_usage () {
    cat 1>&2 <<EOF
Usage:
    lazyfox.bash <firefox_channel> [firefox_options...]
        Run <firefox_channel> with the specified options.

    lazyfox.bash install <firefox_channel...>
        Install one or more Firefox channels now, and exit.

    lazyfox.bash install-symlinks <directory>
        Install symlinks to lazyfox.bash in <directory>, for
        all supported channels of Firefox.

    ff-<firefox_channel> [firefox_options...]
        (Called from symlink named as such) Run <firefox_channel>
        with the specified options.     

Supported channels for lazy installation:
    ${supported[@]}

Other versions of Firefox can be started through this script if you 
unpack their tarballs to ${foxdir}/name.
EOF
}

install_ff_channel () {
    channel="$1"
    targdir="${foxdir}/${channel}"
    if [ -d "$targdir" ]; then
        # Already installed
        return
    fi
    check_supported "$channel"
    echo "Installing Firefox $channel"
    case $channel in
        "release-32")
            url="https://download.mozilla.org/?product=firefox-latest&os=linux&lang=en-US"
            ;;
        "release-64")
            url="https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US"
            ;;
        "beta-32")
            url="https://download.mozilla.org/?product=firefox-beta-latest&os=linux&lang=en-US"
            ;;
        "beta-64")
            url="https://download.mozilla.org/?product=firefox-beta-latest&os=linux64&lang=en-US"
            ;;
        "aurora-32")
            url="https://download.mozilla.org/?product=firefox-aurora-latest-ssl&os=linux64&lang=en-US"
            ;;
        "aurora-64")
            url="https://download.mozilla.org/?product=firefox-aurora-latest-ssl&os=linux64&lang=en-US"
            ;;
        "nightly-32")
            dirurl="ftp://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/"
            url="${dirurl}$(curl -sl "$dirurl" | grep 'linux-i686\.tar\.bz2' | sort | tail -n1)"
            ;;
        "nightly-64")
            dirurl="ftp://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/"
            url="${dirurl}$(curl -sl "$dirurl" | grep 'linux-x86_64\.tar\.bz2' | sort | tail -n1)"
            ;;
    esac
    mkdir -p "$targdir" \
        && curl -L "$url" | tar -xjC "$targdir" --strip-components 1
}

lazyexec_ff_channel () {
    channel="$1"
    shift
    install_ff_channel "$channel"
    cd "${foxdir}/${channel}" && exec ./firefox "$@"
}

check_supported () {
    for channel in ${supported[@]}; do
        if [ "$1" == "$channel" ]; then
            return 0
        fi
    done
    print_usage
    echo "$1 is not supported for installation" 1>&2
    exit 2
}

# main
invoked=$(basename "$0")
if [ "$invoked" == "lazyfox.bash" ]; then
    if [ $# -eq 0 ]; then
        print_usage
        exit 1
    fi
    command="$1"
    shift
    case $command in
        install)
            for channel in $@; do
                install_ff_channel "$channel"
            done
            ;;
        install-symlinks)
            directory="$1"
            for channel in ${supported[@]}; do
                ln -s "$0" "${directory}/ff-${channel}" || true
            done
            ;;
        help|-h|--help)
            print_usage
            ;;
        *)
            lazyexec_ff_channel "$command" "$@"
            ;;
    esac
else
    # Invoked from symlink
    channel=${invoked#ff-}
    lazyexec_ff_channel "$channel" "$@"
fi

