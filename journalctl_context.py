#!/usr/bin/env python3

from collections import deque
from datetime import datetime
from typing import List, NamedTuple, Optional
from systemd import journal
import json
import dateparser
import argparse
import sys
import subprocess
import re


def format_entry(entry):
    try:
        # time = entry["__REALTIME_TIMESTAMP"].isoformat(timespec="milliseconds")
        host = entry.get("_HOSTNAME", "(no hostname)")
        sender = (
            entry.get("SYSLOG_IDENTIFIER", entry.get("_COMM", "(no id)"))
            + "["
            + str(entry.get("_PID", "no PID"))
            + "]"
        )
        message = str(entry.get("MESSAGE", "(no message)"))  # some are bytes
        meta = f"{host} {sender}: "
        pad = "\n" + " " * len(meta)
        return meta + pad.join(message.strip().splitlines())
    except:
        print("Bad entry:", file=sys.stderr)
        print(entry, file=sys.stderr)
        raise


def entries_in_range(since: datetime, until: datetime):
    j = journal.Reader()
    j.seek_realtime(since)
    for e in j:
        if e["__REALTIME_TIMESTAMP"] > until:
            break
        else:
            yield e


class LogMessage(NamedTuple):
    ts: datetime
    msg: str

    def __str__(self):
        return self.ts.isoformat(timespec="milliseconds") + " " + self.msg


def journalctl_with_context(
    search_pattern: str,
    seconds_before: float,
    seconds_after: float,
    since: datetime,
    until: datetime,
):
    printing: bool = False
    last_seen: Optional[datetime] = None
    msg_buf = deque()
    for entry in entries_in_range(since, until):
        parsed = LogMessage(entry["__REALTIME_TIMESTAMP"], format_entry(entry))
        match = re.search(search_pattern, parsed.msg)
        # buffer messages that aren't too old
        msg_buf.append(parsed)
        while (parsed.ts - msg_buf[0].ts).total_seconds() > seconds_before:
            msg_buf.popleft()
        # state machine
        if not printing:
            if match:
                printing = True
                last_seen = parsed.ts
                print("\n".join(str(m) for m in msg_buf))  # incl current line
                msg_buf.clear()
        else:
            if match:
                last_seen = parsed.ts
            if (parsed.ts - last_seen).total_seconds() <= seconds_after:
                pass
                print(parsed)
            else:
                print("--")  # separate incidents
                printing = False


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="grep the journal with time-based context. "
    )
    ap.add_argument("-B", "--before", metavar="SECONDS", type=float, default=0)
    ap.add_argument("-A", "--after", metavar="SECONDS", type=float, default=0)
    ap.add_argument("-C", "--context", metavar="SECONDS", type=float, default=0)
    ap.add_argument("-S", "--since", default=None)
    ap.add_argument("-U", "--until", default="now")
    ap.add_argument("pattern", help="python regex search pattern")
    args = ap.parse_intermixed_args()
    # precedence logic
    before = args.before
    after = args.after
    if args.context != 0:
        before = args.context
        after = args.context
    # parse since/until
    if args.since:
        since = dateparser.parse(
            args.since, settings={"RETURN_AS_TIMEZONE_AWARE": True}
        )
    else:
        since = datetime.utcfromtimestamp(0)
    until = dateparser.parse(
        args.until, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    # do it
    journalctl_with_context(
        args.pattern,
        before,
        after,
        since=since,
        until=until,
    )
