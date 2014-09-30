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

import sys

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



