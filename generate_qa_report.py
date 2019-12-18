#!/usr/bin/env python3

import argparse
import logging
import sys
import configparser
import pdb
import utils
import squadclient
from os.path import isfile


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s@%(funcName)s: %(message)s"
)
stdout_logger = logging.StreamHandler()
stdout_logger.setLevel(logging.INFO)
stdout_logger.setFormatter(log_formatter)
logger.addHandler(stdout_logger)

reports_cfg = 'reports.cfg'
commands = {
    "get_projects": squadclient.get_proj_slugs,
    "pull_tests": squadclient.Client().get_data(),
    "launch_nb": True,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="A Simple cmd util for pulling tests from SQUAD and generating various types of reports locally.",
        epilog="Gimme a report Goddamn it",
    )
    parser.add_argument(
        "cmd",
        choices=commands.keys(),
        help="`get_projects` list projects slugs for a given group provided by--group-slug arg. "
        "`pull_tests` retrieves all tests data for last N testruns for last N builds for project provided  by --proj-slug arg. "
        "Default is to retrieve last build and its last testrun only. Use --num-builds arg to specify last N builds "
        "Use `launch_nb` launches jupyter notebook",
    )
    parser.add_argument(
        "-g",
        "--group-slug",
        dest="group",
        help="group slug to list projects slugs for",
    )
    parser.add_argument(
        "-p",
        "--proj-slug",
        nargs="+",
        dest="projects",
        help="projects slugs to retrieve last N builds for",
    )
    parser.add_argument(
        "-n",
        "--num-builds",
        nargs="?",
        type=int,
        const=1,
        default=1,
        dest="num_builds",
        help="number of builds to query, starting from latest build and backwards. Default 1",
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    func = commands[args.cmd]
    return func(args)


if __name__ == "__main__":
    sys.exit(main())
