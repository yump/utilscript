# utilscript


Various scripts from my personal ~/bin, filtered for possibly being
useful to someone else.

## Hilights


### genpass.py

Versatile password generator.  Uses /dev/random and is reasonably
miserly with the entropy, so it doesn't take too long. Supports
xkcd-style passwords, plus the regular kind.

### trim-common-prefixes.py

Remove common prefixes from the beginnings of lines.  Good for piping to
espeak.

### multi-firefox.bash

Put your firefoxen in ~/opt/firefox, make symlinks to multi-firefox that
start with "ff-", and easily call whichever firefox you want.  Good for
people who frequently switch release channels and CPU architectures.

### wakeme.sh

Test the sound, wait for a specified interval, then play a loud alarm.
Present day. Present time. HA HA HA.

## Disclaimers

The years given in the copyright headers are mostly incorrect. The
scripts were prettied-up and added to this repo in 2014, but most of
them are older.  genpass.py and trim-common-prefixes.py, at least, are
actually from 2014.  
