#!/usr/bin/python3
# coding: utf-8

import hashlib, os, zipfile, sys, locale, tools, random, configparser
from collections import OrderedDict
from io import StringIO
from copy import deepcopy
from .ini import load_ini

rarfile = None
try:
    import rarfile
except:
    pass

def is_rar(fn):
    with open(fn, "rb") as f:
        magic = f.read(4)
    return magic == b'Rar!'

def is_zip(fn):
    with open(fn, "rb") as f:
        magic = f.read(2)
    return magic == b'PK'

def is_archive(fn):
    ext_fn = os.path.splitext(fn)[-1].lower()

    return ext_fn in (".rar", ".cbr", ".zip", ".cbz")

def is_image(fn):
    ext_fn = os.path.splitext(fn)[-1].lower()

    return ext_fn in \
            (".jpeg", ".jpg", ".png", ".gif", ".bmp", ".webp")

def every_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for name in files:
            yield os.path.join(root, name)

def strip_path(s, subdir):
    return os.path.relpath(s, subdir)

class Repo(object):
    def __init__(self, dirname, app):
        self.dirname = dirname
        self.config = load_ini(self.dirname, app)
        self.st_mtime = os.stat(dirname).st_mtime
        self.load()

    def sort(self, order, desc):
        if order == 'name':
            self.comics = OrderedDict(sorted(self.comics.items(), key=lambda t:t[1]['filename'], reverse=desc))
        elif order == 'time':
            self.comics = OrderedDict(sorted(self.comics.items(), key=lambda t:t[1]['mtime'], reverse=desc))
        elif order == 'size':
            self.comics = OrderedDict(sorted(self.comics.items(), key=lambda t:t[1]['filesize'], reverse=desc))
        elif order == 'random':
            x = list(self.comics.items())
            random.shuffle(x)
            self.comics = OrderedDict(x)

    def reload(self, app):
        self.config = load_ini(self.dirname, app)
        self.load()

    def load(self):
        self.comics = { hashlib.md5(fn.encode('utf-8')).hexdigest(): { 'filename': fn, 'filesize' : os.stat(fn).st_size, 'mtime': os.stat(fn).st_mtime } \
                for fn in filter(is_archive, every_files_in_directory(self.dirname)) }
        order = self.config['sort']
        desc = self.config.getboolean('reverse')
        self.sort(order, desc)

    def search(self, keyword, order, desc):
        r = deepcopy(self)
        x = {}
        for e in r.comics:
            if keyword.lower() in strip_path(r.comics[e]['filename'], r.dirname).lower():
                x[e] = r.comics[e]
        del r.comics
        r.comics = x
        r.sort(order, desc)

        return r

class Archive(object):
    def __init__(self, path, reverse):
        self.path = path

        if rarfile and is_rar(self.path):
            with rarfile.RarFile(self.path, "r") as f:
                self.fnlist = [ e for e in f.namelist() if is_image(e) ]
                tools.alphanumeric_sort(self.fnlist, reverse)
            return

        if is_zip(self.path):
            with zipfile.ZipFile(self.path, "r") as f:
                self.fnlist = [ e for e in f.namelist() if is_image(e) ]
                tools.alphanumeric_sort(self.fnlist, reverse)
            return

        raise RuntimeError("Cannot open rar: please install python-rarfile")

    def read(self, pid):
        if rarfile and is_rar(self.path):
            with rarfile.RarFile(self.path, "r") as f:
                return f.read(self.fnlist[pid])

        with zipfile.ZipFile(self.path, "r") as f:
            return f.read(self.fnlist[pid])

        raise RuntimeError("Cannot open rar: please install python-rarfile")

# vim: set tabstop=4 sw=4 expandtab:
