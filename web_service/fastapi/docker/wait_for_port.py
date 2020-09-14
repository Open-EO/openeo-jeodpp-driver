#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# module: wait4port.py
# Copyright: Fractal Industries Inc.
# URL: https://bitbucket.org/snippets/fractalindustries/Lqnyk
# Version: 0.1.1

"""
Wait until a port opens/closes.

This is actually a wrapper around `nc`.

Examples of usage:

    python3 wait4port.py 13000                          # Wait until port 13000 opens.
    python3 wait4port.py 13000 -c                       # Wait until port 13000 closes.
    python3 wait4port.py 13000 -s                       # Set silent mode on
    python3 wait4port.py 13000 -w 10                    # Set timeout to 10 seconds
    python3 wait4port.py -h 172.17.0.1 13000            # Specify host

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import sys
import time
import shlex
import shutil
import logging
import argparse
import distutils.spawn
import subprocess

logger = logging.getLogger("wait4port")
logger.addHandler(logging.NullHandler())


# Python 2 compatiibility
def which(path):
    if sys.version_info.major == 2:
        return distutils.spawn.find_executable(path)
    else:
        return shutil.which(path)


def check_dependencies(netcat):
    if not which(netcat):
        raise ValueError("<nc> command not found. Please install netcat and try again.")


def check_port(host, port):
    cmd = shlex.split("nc -z '{host:s}' '{port:d}'".format(host=host, port=port))
    return not subprocess.call(cmd)


def wait_for_port(host, port, timeout=30, close_mode=False):
    logger.info("Checking %s:%d", host, port)
    for i in range(1, timeout + 1):
        port_is_open = check_port(host, port)
        if close_mode:
            if not port_is_open:
                logger.info("%s:%d is closed!", host, port)
                sys.exit(0)
        elif port_is_open:
            logger.info("%s:%d is open!", host, port)
            sys.exit(0)
        logger.info("Waiting: %3d/%3d", i, timeout)
        time.sleep(1)
    logger.info("Timeout! %s:%d has not changed state.", host, port)
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wait until a port opens (or closes!)."
    )
    parser.add_argument(
        "--host", default="127.0.0.1", metavar="", help="The host we want to check."
    )
    parser.add_argument("port", help="The port we want to check.", type=int)
    parser.add_argument(
        "-n",
        "--netcat",
        default="nc",
        metavar="",
        help="The path to the <nc> executable.",
    )
    parser.add_argument(
        "-c",
        "--close",
        dest="close_mode",
        default=False,
        action="store_true",
        help="Wait until the port closes",
    )
    parser.add_argument(
        "-s", "--silent", default=False, action="store_true", help="Silent mode"
    )
    parser.add_argument(
        "-t", "--timeout", default=30, metavar="", type=int, help="Default timeout."
    )
    args = parser.parse_args()
    check_dependencies(args.netcat)
    if not args.silent:
        logging.basicConfig(level=20, format="%(name)s: %(message)s")
    wait_for_port(args.host, args.port, args.timeout, args.close_mode)
