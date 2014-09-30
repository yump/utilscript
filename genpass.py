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
Password generator.

Usage:
    genpass [--xkcd] [--entropy] [-c <charset>] [-n <num_passwords>] LENGTH
    genpass -h | --help

Options:
    -c, --charset=SPEC      Character set. [default: a-z0-9]
    -n, --num-passwords=N   Number of passwords. [default: 1]
    -e, --entropy           Interpret LENGTH as a minimum entropy, and choose
                            the required length in characters automatically.
    --xkcd                  Generate correcthorsebatterystaple type passwords.
    -h, --help              Show this message.
"""

import codecs
import sys
import re
import math
import unicodedata
from itertools import *
from pprint import pformat
from docopt import docopt

def genpass(charset, length):
    """
    Generate password of length using characters restricted to charset 
    (a genpass.Charset instance), printing each character as it becomes 
    available.
    """
    for index in islice(strong_randint(len(charset)), length):
        sys.stdout.write(charset[index])
    sys.stdout.write('\n')

_wordcache=None

def xkcd(length=None, entropy=None):
    global _wordcache
    if _wordcache is None:
        with open('/usr/share/dict/words') as wordfile:
            words = list(set(w.strip().lower() for w in wordfile 
                        if re.match('^[a-zA-Z]{3,9}$', w)))
            _wordcache = words
    else:
        words = _wordcache
    if (length is None) == (entropy is None):
        raise ValueError("Must specify entropy xor length")
    if length is None:
        # Get length from entropy
        length = math.ceil(entropy / math.log2(len(words)))
    for index in islice(strong_randint(len(words)), length):
        sys.stdout.write(words[index] + " ")
    sys.stdout.write('\n')

def rangelen(r):
    """
    Find the length of a range without barfing if the length is greater
    than can fit in an ssize_t.
    """
    q = (r.stop - r.start) // r.step
    return q+1 if (r.stop - r.start) % r.step != 0 else q

def strong_randint(*args):
    """
    strong_randint(upper) -> iterable
    strong_randint(lower, upper[, step]) -> iterable

    Generate uniformly distributed random integers from the range
    specified, using /dev/random
    """
    bounds = range(*args)
    cardinality = rangelen(bounds)
    num_bits = math.ceil(math.log2(cardinality)) # Waste not, want not
    bit_source = randbits()
    while True:
        # Generate random integer between zero and the smallest power of
        # 2 greater than the number of possible outputs.
        n = sum(bit << exponent for bit, exponent in 
                zip(islice(bit_source, num_bits), range(num_bits)))
        # Throw away integers that are too big
        if n < cardinality:
            #scale
            yield n*bounds.step + bounds.start

def randbits():
    """Get random bits from /dev/random."""
    with open('/dev/random','rb') as randfile:
        while True:
            byte = ord(randfile.read(1))
            for i in range(8):
                yield byte & 1
                byte >>= 1

class Charset:
    """
    Set of characters from unicode.
    """
    # Regex for parsing
    PARSE_RE = re.compile(r"""
        (   # A range of codepoints
            (?P<start> \\- | [^-] ) # Escaped "-" or unescaped anything else
            -                       # Ranges separated by "-"
            (?P<stop> \\- | [^-] )
        )
        | (?P<single> \\- | [^-] )  # Or a single codepoint
        """, re.VERBOSE)
    # regex for escape sequences
    UNESCAPE_RE = re.compile(r"""
        \\U[0-9a-fA-F]{8}     # UTF-32 
        | \\u[0-9a-fA-F]{4}   # UTF-16
        | \\x[0-9a-fA-F]{2}   # bytes
        | \\[0-7]{1,3}        # octal
        | \\N\{[^}]+\}        # Unicode names
        | \\[\\"'abfnrtv]     # single-character
        """, re.VERBOSE)

    @staticmethod
    def _unescape_token(t):
        return re.sub(r'\\(-)', r'\1' , t)

    @classmethod
    def _unescape_string(cls,string):
        def dosub(match):
            return codecs.decode(match.group(0), 'unicode-escape')
        return cls.UNESCAPE_RE.sub(dosub, string)

    @staticmethod
    def _escape_whitespace(string):
        def dosub(match):
            return codecs.encode(match.group(0), 'unicode-escape').decode()
        return re.sub(r'\s+', dosub, string)

    def __init__(self, tr_repr):
        """
        Create a Charset from a string, with syntax similar to argument
        to unix program tr. Combining unicode diacretics will be reduced
        to the diacreticized character.
        """
        self.repr = "Charset({})".format(pformat(tr_repr))
        # Make unicode pleasant.
        tr_repr = unicodedata.normalize('NFC',tr_repr) #No combining characters
        tr_repr = self._unescape_string(tr_repr)
        self.str = "Charset(\"{}\")".format(self._escape_whitespace(tr_repr))
        # Character set is stored as a sorted list of non-overlapping 
        # ranges. If a character's unicode codepoint is in any of them,
        # it is in the set.
        self.ranges = []
        for match in self.PARSE_RE.finditer(tr_repr):
            if match.group('single'):
                char = self._unescape_token(match.group('single'))
                start = ord(char)
                stop  = start + 1
            else:
                start = ord(self._unescape_token(match.group('start')))
                stop  = ord(self._unescape_token(match.group('stop'))) + 1
            # Overlap not allowed
            for r in self.ranges:
                if start in r or stop - 1 in r:
                    raise ValueError("Overlapping charater ranges not allowed")
            self.ranges.append(range(start,stop))
        self.ranges.sort(key=lambda r: r.start)

    def __repr__(self):
        return self.repr

    def __str__(self):
        return self.str

    def __contains__(self, item):
        return any(ord(item) in r for r in self.ranges)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("indices must be integers")
        for r in self.ranges:
            if index < len(r):
                return chr(r[index])
            else:
                index -= len(r)
        else:
            raise IndexError

    def __len__(self):
        return sum(len(r) for r in self.ranges)

    def __eq__(self, other):
        return self.ranges == other.ranges

    def __iter__(self):
        for r in self.ranges:
            for codepoint in r:
                yield chr(codepoint)

if __name__ == "__main__":
    args = docopt(__doc__)
    charset = Charset(args['--charset'])
    for i in range(int(args['--num-passwords'])):
        if args['--xkcd']:
            if args['--entropy']:
                xkcd(entropy=float(args['LENGTH']))
            else:
                xkcd(length=int(args['LENGTH']))
        else:
            if args['--entropy']:
                entropy = float(args['LENGTH'])
                length = math.ceil(entropy / math.log2(len(charset)))
            else:
                length = int(args['LENGTH'])
            genpass(charset, length)
