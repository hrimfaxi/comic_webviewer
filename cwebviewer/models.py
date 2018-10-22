#!/usr/bin/python3
# coding: utf-8

import os, tempfile, subprocess
from flask import current_app as app
from .consts import *
from . import archive

def reload_repo(aid):
    dirname = app.repo[aid][DIRNAME]
    app.repo[aid] = [ dirname, os.stat(dirname).st_mtime, archive.load(dirname, app.config['SORT'], app.config['REVERSE']) ]

def reload_repo_by_mtime(aid):
    dirname = app.repo[aid][DIRNAME]
    timestamp = os.stat(dirname).st_mtime
    if app.config['SORT'] == 'random' or app.repo[aid][MTIME] < timestamp:
        reload_repo(aid)

def make_image(ar, pid, width, conv_webp):
    d = ar.read(pid)
    ext_fn = os.path.splitext(ar.fnlist[pid])[-1].lower()
    if ext_fn != ".webp" and conv_webp:
        # convert into webp
        # cwebp didn't support stdin/stdout, output to temp file
        with tempfile.NamedTemporaryFile(prefix='comic_webviewer') as temp:
            temp.write(d)
            temp.flush()
            null = open(os.devnull, 'wb')
            cwebp_cmd = [ CWEBP_PATH ] + CWEBP_EXTRA_OPTIONS + [ '-resize', '%d' % (width), '0', '-preset', app.config['WEBP_PRESET'], '-q', '%d' % (app.config['WEBP_QUALITY']), temp.name, '-o', '-']
            app.logger.warning(cwebp_cmd)
            p = subprocess.Popen(cwebp_cmd, stderr=null, stdout=subprocess.PIPE)
            stdout, _ = p.communicate()
            app.logger.warning('webp compressed: %d/%d %f%%' % (len(stdout), len(d), 100.0 * len(stdout) / len(d)))
            d = stdout
            del null, p
    return d

# vim: set tabstop=4 sw=4 expandtab:
