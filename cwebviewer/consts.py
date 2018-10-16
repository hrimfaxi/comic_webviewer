#!/usr/bin/python3
# coding: utf-8

import shutil

DIRNAME, MTIME, ARCHIVE = range(3)
CWEBP_EXTRA_OPTIONS = [ '-mt' ]
CWEBP_PATH = shutil.which('cwebp')

# vim: set tabstop=4 sw=4 expandtab:
