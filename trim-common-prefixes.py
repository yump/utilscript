#!/usr/bin/env python3
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

"""
trim-common-prefixes.py: make overly-verbose output more human and
screen-reader friendly by replacing words that don't change between
subsequent lines with "-----".

Usage: 
    journalctl | trim-common-prefixes.py

    Sep 30 18:09:10 hogwarts dnf[28017]: cachedir: /var/cache/dnf/x86_64/20
    Sep 30 18:09:10 hogwarts dnf[28017]: DNF version: 0.5.4
    Sep 30 18:09:10 hogwarts dnf[28017]: Making cache files for all metadata files.
    Sep 30 18:09:10 hogwarts dnf[28017]: Metadata cache refreshed recently.
    Sep 30 18:09:10 hogwarts systemd[1]: Started dnf makecache.
    Sep 30 18:10:10 hogwarts /etc/gdm/Xsession[20359]: => suspend now!-

    becomes:

    Sep 30 18:09:10 hogwarts dnf[28017]: cachedir: /var/cache/dnf/x86_64/20
    --- -- -------- -------- ----------- DNF version: 0.5.4
    --- -- -------- -------- ----------- Making cache files for all metadata files.
    --- -- -------- -------- ----------- Metadata cache refreshed recently.
    --- -- -------- -------- systemd[1]: Started dnf makecache.
    --- -- 18:10:10 hogwarts /etc/gdm/Xsession[20359]: => suspend now!
"""

import sys

if len(sys.argv) > 1:
    print(__doc__)
    exit(1)

oldline = []

for line in sys.stdin:
    prefix = []
    for wordx, word in enumerate(line.split()):
        if wordx >= len(oldline):
            break
        if word != oldline[wordx]:
            break
        prefix.append("-"*len(word))
    print(" ".join(prefix + line.split()[wordx:]))
    oldline = line.split()



