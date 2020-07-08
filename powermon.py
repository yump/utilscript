#!/usr/bin/env python3
# Copyright (C) 2020 Russell Haley
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

# Program for watching the energy monitoring interface exposed by intel_rapl.
# On my machine, CPU core, CPU package, and DRAM power are shown.

import sys
import time
import argparse
import contextlib
from pathlib import Path


def powergen(rapl_sys_path):
    syspath = Path(rapl_sys_path)
    rollover_limit = int(syspath.joinpath("max_energy_range_uj").read_text())
    with open(syspath.joinpath("energy_uj")) as f:
        last_uj = int(f.read())
        last_time = time.time()
        yield 0.0  # can't give meaningful data until we've been run twice
        while True:
            f.seek(0)
            cur_uj = int(f.read())
            cur_time = time.time()
            if cur_uj > last_uj:
                delta_uj = cur_uj - last_uj
            else:
                delta_uj = cur_uj + rollover_limit - last_uj
            power_w = 1e-6 * delta_uj / (cur_time - last_time)
            last_time = cur_time
            last_uj = cur_uj
            yield power_w


def find_rapls():
    for p in Path("/sys/class/powercap/").glob("*"):
        namepath = p.joinpath("name")
        if namepath.is_file():
            yield (namepath.read_text().strip(), p)


def main():
    parser = argparse.ArgumentParser(
        description="Print power estimates for all RPAL energy domains"
    )
    parser.add_argument("-i", "--interval", type=float, default=1)
    args = parser.parse_args()
    rapl_gens = [(name, powergen(path)) for name, path in find_rapls()]
    # eat the inital zeros
    for _, gen in rapl_gens:
        next(gen)
    # measure and print power readings every args.interval seconds, forever
    next_sample_time = time.time() + args.interval
    while True:
        time.sleep(next_sample_time - time.time())
        next_sample_time += args.interval
        print(
            "    ".join(
                "{}: {:6.2f} W".format(name, next(pgen))
                for name, pgen in rapl_gens
            )
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
