# utilscript


Various scripts from my personal ~/bin, filtered for possibly being
useful to someone else.

## Hilights

### lazyfox.bash

Script for starting (and installing) multiple versions of Firefox.  Good
for people who frequently switch release channels and CPU architectures.
Firefox tarballs are downloaded lazily, so it's easy on the disk space.
Supports 32 and 64 bit release and nightly channels, along with 32 bit
beta and aurora. Supercedes multi-firefox.bash.

### genpass.py

Versatile password generator.  Uses /dev/random and is reasonably
miserly with the entropy, so it doesn't take too long. Supports
xkcd-style passwords, plus the regular kind.

### trim-common-prefixes.py

Remove common prefixes from the beginnings of lines.  Good for piping to
espeak.

### wakeme.sh

Test the sound, wait for a specified interval, then play a loud alarm.
Present day. Present time. HA HA HA.

## Disclaimers

The years given in the copyright headers are mostly incorrect. The
scripts were prettied-up and added to this repo in 2014, but most of
them are older. lazyfox.bash, genpass.py and trim-common-prefixes.py, at
least, are actually from 2014.  
