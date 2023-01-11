#!/usr/bin/env python3

from collections import deque
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
import json
import argparse
import sys
import subprocess
import re


@dataclass(slots=True)
class LogMessage:
    ts: datetime
    msg: str

    def __str__(self):
        return self.ts.isoformat(timespec="milliseconds") + " " + self.msg

    @classmethod
    def journal_reader(cls, journalctl_args: List[str] = []):
        # delegate to journalctl CLI, because it's better than python systemd
        # library at handling corrupt journal files gracefully
        child = subprocess.Popen(
            ["journalctl"]
            + journalctl_args
            + ["-q", "-o", "short-iso-precise"],
            text=True,
            stdout=subprocess.PIPE,
        )
        # ugly hax for handling multi-line log messages
        def produce(linebuf: List[str]):
            timestamp, firstline = linebuf[0][:-1].split(maxsplit=1)
            message = firstline + "".join(linebuf[1:])[:-1]
            linebuf.clear()
            return cls(datetime.fromisoformat(timestamp), message)

        # put the 1st line in the buffer and loop starting at the 2nd
        linebuf: List[str] = [next(iter(child.stdout))]
        for line in child.stdout:
            if line[0] != " ":  # not a continuation of the last message
                yield produce(linebuf)
            linebuf.append(line)
        yield produce(linebuf)
        child.wait()


def journalctl_with_context(
    search_pattern: str,
    seconds_before: float,
    seconds_after: float,
    extra_args: List[str],
):
    printing: bool = False
    last_seen: Optional[datetime] = None
    msg_buf = deque()
    for logmsg in LogMessage.journal_reader(extra_args):
        match = re.search(search_pattern, logmsg.msg)
        # buffer messages that aren't too old
        msg_buf.append(logmsg)
        while (logmsg.ts - msg_buf[0].ts).total_seconds() > seconds_before:
            msg_buf.popleft()
        # state machine
        if not printing:
            if match:
                printing = True
                last_seen = logmsg.ts
                print("\n".join(str(m) for m in msg_buf))  # incl current line
                msg_buf.clear()
        else:
            if match:
                last_seen = logmsg.ts
            if (logmsg.ts - last_seen).total_seconds() <= seconds_after:
                pass
                print(logmsg)
            else:
                print("--")  # to separate matches, same as grep -C
                printing = False


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="grep the journal with time-based context. "
    )
    ap.add_argument("-B", "--before", metavar="SECONDS", type=float, default=0)
    ap.add_argument("-A", "--after", metavar="SECONDS", type=float, default=0)
    ap.add_argument("-C", "--context", metavar="SECONDS", type=float, default=0)
    ap.add_argument("pattern", help="python regex search pattern")
    args, extra_args = ap.parse_known_args()
    # precedence logic
    before = args.before
    after = args.after
    if args.context != 0:
        before = args.context
        after = args.context
    journalctl_with_context(
        args.pattern,
        before,
        after,
        extra_args,
    )
