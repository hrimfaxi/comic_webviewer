#!/usr/bin/python2
# coding: utf-8

import argparse, sys

config = {
    "port" : 8181,
    "path" : ".",
}

def load_config():
    parser = argparse.ArgumentParser(description='Comic webviewer')
    parser.add_argument('-p', '--port', dest='port', type=int, help='the port to listen on, default 8181')
    parser.add_argument('path', metavar='PATH', type=str, nargs='?', help='the directory to load as index, current directory by default')
    args = parser.parse_args()

    vargs = vars(args)
    for v in vargs:
        if v in config and vargs[v]:
            config[v] = vargs[v]

# vim: set sw=4 tabstop=4 expandtab :
