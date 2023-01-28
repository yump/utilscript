#!/usr/bin/env python3
# Copyright (C) 2023 Russell Haley
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
Automatically plot data in a variety of simple text formats:

    1. CSV with or without first line column headers.
    2. Whitespace-separated with shell-style comments, where the last comment
       before the first data line contains the column headers. Because all
       further comments are ignored, the headers can be included multiple
       times, which allows concatenating files and makes it easy for humans to 
       scroll through.
    3. Whitespace separated with shell-style comments, where the first
       non-comment line contains the column headers.
"""

from __future__ import annotations
from collections import namedtuple
from collections.abc import Iterable, Collection, Sequence
from dataclasses import dataclass
from datetime import datetime
from matplotlib import pyplot
import argparse
import csv
import enum
import itertools
import itertools
import re
import sys
import typing


def plot_file(
    file: typing.TextIO,
    subplots: bool,
    sharey: bool,
    show_points: bool,
    fields_include: typing.Optional[Collection] = None,
    fields_exclude: typing.Optional[Collection] = None,
    write_output: typing.Optional[str] = None,
):
    # look ahead at the first 16 KiB to figure out the format
    beginning = file.readlines(16 * 2**10)
    all_line_gen: Iterable[str] = itertools.chain(beginning, file)
    file_format = Format.identify(beginning)
    print(f"detected format {file_format}")
    match Format.identify(beginning):
        case Format.NL_COMMENT_HEADER | Format.NL_WHITESPACE_SEP:
            print("plotting whitespace separated with shell comment header")
            columns = parse_commented_or_whitesep(
                all_line_gen, fields_include, fields_exclude
            )
        case Format.NL_CSV:
            print("plotting csv")
            columns = parse_csv(
                all_line_gen, beginning, fields_include, fields_exclude
            )
        case _:
            raise NotImplementedError
    plot_columns(columns, subplots, sharey, show_points, write_output)


class Format(enum.StrEnum):
    # newline-separated
    NL_COMMENT_HEADER = enum.auto()  # column names in comment prefixed with "#"
    NL_KEYVAL = enum.auto()  # column1=value column2=value
    NL_CSV = enum.auto()  # csv, column names in 1st line
    NL_WHITESPACE_SEP = enum.auto()  # | column -t, column names in 1st line
    # TODO: Json (probably better to extract with jq and format to csv anyway)
    JSON_SEQ = enum.auto()  # json objects, concated
    JSON_SINGLE = enum.auto()  # one big json

    @staticmethod
    def identify(lines: list[str]) -> Format:
        # NL_COMMENT_HEADER
        if lines[0][0] == "#":
            return Format.NL_COMMENT_HEADER
        # NL_KEYVAL
        if all(re.fullmatch("(\w+=\w+)+", l) for l in lines):
            return Format.NL_KEYVAL
        # NL_CSV
        try:
            dia = csv.Sniffer().sniff(lines[0], delimiters=",:; \t")
            # check for all records same length
            # otherwise this is probably whitespace-separated
            if 1 == len(set(len(row) for row in csv.reader(lines, dia))):
                return Format.NL_CSV
        except:
            pass
        # NL_WHITESPACE_SEP
        if 1 == len(set(len(l.strip().split()) for l in lines)):
            return Format.NL_WHITESPACE_SEP
        raise NotImplementedError


@dataclass
class Column:
    name: str
    number: int
    data: list[float]

    @staticmethod
    def get_selection(
        colnames: Sequence[str],
        include: typing.Optional[Collection[str]] = None,
        exclude: typing.Optional[Collection[str]] = None,
    ) -> dict[str, Column]:
        """ """
        if include is None:
            include = set(colnames)
        else:
            include = set(include)
            include.add("time")
        if exclude is None:
            exclude = []
        columns: dict[str, Column] = {
            name: Column(name=name, number=num, data=[])
            for num, name in enumerate(colnames)
            if name in include and name not in exclude
        }
        return columns


def append_row(columns: dict[str, Column], rowfields: Sequence[str]):
    for col in columns.values():
        col.data.append(float(rowfields[col.number]))


def plot_columns(
    columns: dict[str, Column],
    subplots: bool,
    sharey: bool,
    show_points: bool,
    write_output: typing.Optional[str] = None,
):
    have_timestamps = "time" in columns
    # Get the X axis values
    if have_timestamps:
        # avoid confusing default date labeling
        pyplot.rcParams["date.autoformatter.minute"] = "%a %m-%d %H:%M"
        pyplot.rcParams["date.autoformatter.hour"] = "%a %m-%d %H:%M"
        pyplot.rcParams["date.autoformatter.day"] = "%Y-%m-%d"
        # pull out the time column and convert to dtatetimes
        xdata = [datetime.fromtimestamp(t) for t in columns.pop("time").data]
    else:
        # use the index
        xdata = range(len(list(columns.values())[0].data))
    # do the plotting
    if show_points:
        fmt_args = {"marker": ".", "linewidth": 0.5, "markersize": 3}
    else:
        fmt_args = {}
    pyplot.style.use("dark_background")
    if subplots:
        fig, axs = pyplot.subplots(
            nrows=len(columns),
            ncols=1,
            sharex=True,
            sharey=sharey,
        )
    else:
        fig, ax = pyplot.subplots(nrows=1, ncols=1, tight_layout=True)
    for i, col in enumerate(columns.values()):
        if subplots:
            axs[i].plot(xdata, col.data, label=col.name, **fmt_args)
            axs[i].set_ylabel(col.name, rotation=0, labelpad=12)
            axs[i].yaxis.set_label_position("right")
            if sharey:
                axs[i].spines["top"].set_visible(False)
                axs[i].spines["bottom"].set_visible(False)
                axs[i].spines["right"].set_visible(False)
                axs[i].tick_params("x", bottom=False)
        else:
            ax.plot(xdata, col.data, label=col.name, **fmt_args)
    if have_timestamps:
        fig.autofmt_xdate()
    if not subplots:
        fig.legend()
    if subplots and sharey:
        # fig.subplots_adjust(hspace=0.1)
        axs[0].tick_params("x", top=True)
        axs[-1].tick_params("x", bottom=True)
    # generic settings
    fig.set_tight_layout(True)
    if write_output:
        fig.savefig(write_output)
    else:
        pyplot.show()


def parse_csv(
    lines: Iterable[str],
    sample_lines: Sequence[str],
    fields_include: typing.Optional[Collection] = None,
    fields_exclude: typing.Optional[Collection] = None,
) -> dict[str, Column]:
    sample_text: str = "".join(sample_lines)
    dialect = csv.Sniffer().sniff(sample_text)
    reader = csv.reader(lines, dialect)
    # set up the columns
    if csv.Sniffer().has_header(sample_text):
        colnames = next(reader)
    else:
        # use column numbers if no header
        num_cols = len(next(csv.reader(sample_lines, dialect)))
        colnames = [str(i + 1) for i in range(num_cols)]
    columns: dict[str, Column] = Column.get_selection(
        colnames, fields_include, fields_exclude
    )
    # parse
    for lineno, vals in enumerate(reader):
        if len(vals) == len(colnames):
            append_row(columns, vals)
        else:
            raise ValueError(f"wrong number of fields on line {lineno+1}")
    return columns


def parse_commented_or_whitesep(
    lines: Iterable[str],
    fields_include: typing.Optional[Collection] = None,
    fields_exclude: typing.Optional[Collection] = None,
) -> dict[str, Column]:
    in_preamble = True
    colnames: typing.Optional[list[str]] = None
    for lineno, line in enumerate(lines):
        if in_preamble:
            match line.strip().split(sep="#", maxsplit=1):
                case []:  # blank line
                    continue
                case ["", comment]:  # comment only
                    colnames = parse_comment_colnames(line)
                case [row] | [row, _]:  # data or data and comment
                    # if we haven't found a header, get names from first row
                    if colnames is None:
                        colnames = [s.strip() for s in row.split()]
                        continue  # data starts on next line
                    else:
                        columns: dict[str, Column] = Column.get_selection(
                            colnames, fields_include, fields_exclude
                        )
                        in_preamble = False  # data starts on this line
        if not in_preamble:  # note lack of "else"
            match line.strip().split(sep="#", maxsplit=1):
                case [] | ["", _]:  # empty or comment only
                    pass
                case [row] | [row, _]:
                    vals = row.split()
                    if len(vals) == len(colnames):
                        append_row(columns, vals)
                    else:
                        raise ValueError(
                            f"wrong number of fields on line {lineno+1}"
                        )
    return columns


def parse_comment_colnames(line: str) -> list[str]:
    """
    concatenable data style:
    line: "#     field_1 field_2 # additional comments"
    """
    m = re.match("#+\s*([^#]+)", line)
    if not m:
        raise ValueError(f'failed to parse as header: "{line}"')
    else:
        return m.group(1).split()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="plot simple data files")
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file", type=argparse.FileType(mode="r"), nargs="?", default=sys.stdin
    )
    parser.add_argument(
        "--include", "-i", help="include fields, comma-separated list"
    )
    parser.add_argument(
        "--exclude", "-e", help="exclude fields, comma-separated list"
    )
    parser.add_argument("--output", "-o", help="write image to file")
    parser.add_argument(
        "--subplots", help="separate plot per column", action="store_true"
    )
    parser.add_argument(
        "--share-y", help="subplots use same y range", action="store_true"
    )
    parser.add_argument(
        "--show-points",
        "-p",
        help="show individual data points",
        action="store_true",
    )
    args = parser.parse_args()
    include = None if args.include is None else args.include.split(sep=",")
    exclude = None if args.exclude is None else args.exclude.split(sep=",")
    plot_file(
        args.file,
        subplots=args.subplots,
        sharey=args.share_y,
        show_points=args.show_points,
        fields_include=include,
        fields_exclude=exclude,
        write_output=args.output,
    )
