#!/usr/bin/env python3

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



