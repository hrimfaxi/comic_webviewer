#!/usr/bin/python2
# coding: utf-8

import argparse, sys

config = {
    "port" : 8181,
    "path" : ".",
    "sorted_by" : "name",
}

def load_config():
    parser = argparse.ArgumentParser(description='Comic webviewer')
    parser.add_argument('-p', '--port', type=int, help='the port to listen on, default 8181')
    parser.add_argument('-s', '--sorted_by', type=str, choices=['name', 'size', 'time'], metavar='(name|size|time)', nargs='?', default='name', help='sort index by name/size/time')
    parser.add_argument('path', metavar='PATH', type=str, nargs='?', help='the directory to load as index, current directory by default')
    args = parser.parse_args()

    vargs = vars(args)
    for v in vargs:
        if v in config and vargs[v]:
            config[v] = vargs[v]

# vim: set sw=4 tabstop=4 expandtab :
