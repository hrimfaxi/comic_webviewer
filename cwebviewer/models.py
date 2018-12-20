#!/usr/bin/python3
# coding: utf-8

import os, tempfile, subprocess
from flask import current_app as app
from .consts import *
from .archive import Repo, get_dir_config

def reload_repo(aid):
    dirname = app.repos[aid].dirname
    app.repos[aid] = Repo(dirname, app)

def reload_repo_by_mtime(aid):
    dirname = app.repos[aid].dirname
    timestamp = os.stat(dirname).st_mtime
    config = get_dir_config(dirname, app)
    if config['sort'] == 'random' or app.repos[aid].st_mtime < timestamp:
        reload_repo(aid)

def make_image(ar, pid, width, browser_want_webp, config):
    is_webp = False
    d = ar.read(pid)
    ext_fn = os.path.splitext(ar.fnlist[pid])[-1].lower()
    if ext_fn != ".webp" and browser_want_webp and config.getboolean('webp'):
        # convert into webp
        # cwebp didn't support stdin/stdout, output to temp file
        with tempfile.NamedTemporaryFile(prefix='comic_webviewer') as temp:
            temp.write(d)
            temp.flush()
            null = open(os.devnull, 'wb')
            cwebp_cmd = [ CWEBP_PATH ] + CWEBP_EXTRA_OPTIONS + [ '-resize', '%d' % (width), '0', '-preset', config['webp_preset'], '-q', '%d' % (config.getint('webp_quality')), temp.name, '-o', '-']
            app.logger.warning(cwebp_cmd)
            p = subprocess.Popen(cwebp_cmd, stderr=null, stdout=subprocess.PIPE)
            stdout, _ = p.communicate()
            app.logger.warning('webp compressed: %d/%d %f%%' % (len(stdout), len(d), 100.0 * len(stdout) / len(d)))
            d = stdout
            del null, p
            is_webp = True
    return d, is_webp

# vim: set tabstop=4 sw=4 expandtab:
