#!/usr/bin/python3
# coding: utf-8

import os, tempfile, subprocess, configparser
from flask import current_app as app
from .consts import *
from . import archive

def get_dir_config(dirname):
    config_fn = os.path.join(dirname, ".comic_webviewer.conf")
    config = configparser.ConfigParser()
    config['default'] = {
            "sort": app.config['SORT'],
            "reverse" : app.config['REVERSE'],
            'archive_per_page': app.config['ARCHIVE_PER_PAGE'],
            'webp': app.config['WEBP'],
            'img_per_page' : app.config['IMG_PER_PAGE'],
            'webp_quality': app.config['WEBP_QUALITY'],
            'webp_preset': app.config['WEBP_PRESET'],
            }

    if os.path.isfile(config_fn):
        config.read_file(open(config_fn))

    return config

def reload_repo(aid):
    dirname = app.repo[aid][DIRNAME]
    # check for per-directory config
    config = get_dir_config(dirname)
    app.repo[aid] = [ dirname, os.stat(dirname).st_mtime, archive.load(dirname, config['default']['sort'], config['default'].getboolean('reverse')), config ]

def reload_repo_by_mtime(aid):
    dirname = app.repo[aid][DIRNAME]
    timestamp = os.stat(dirname).st_mtime
    config = get_dir_config(dirname)
    if config['default']['sort'] == 'random' or app.repo[aid][MTIME] < timestamp:
        reload_repo(aid)

def make_image(ar, pid, width, conv_webp, config):
    d = ar.read(pid)
    ext_fn = os.path.splitext(ar.fnlist[pid])[-1].lower()
    if ext_fn != ".webp" and conv_webp:
        # convert into webp
        # cwebp didn't support stdin/stdout, output to temp file
        with tempfile.NamedTemporaryFile(prefix='comic_webviewer') as temp:
            temp.write(d)
            temp.flush()
            null = open(os.devnull, 'wb')
            cwebp_cmd = [ CWEBP_PATH ] + CWEBP_EXTRA_OPTIONS + [ '-resize', '%d' % (width), '0', '-preset', config['default']['webp_preset'], '-q', '%d' % (config['default'].getint('webp_quality')), temp.name, '-o', '-']
            app.logger.warning(cwebp_cmd)
            p = subprocess.Popen(cwebp_cmd, stderr=null, stdout=subprocess.PIPE)
            stdout, _ = p.communicate()
            app.logger.warning('webp compressed: %d/%d %f%%' % (len(stdout), len(d), 100.0 * len(stdout) / len(d)))
            d = stdout
            del null, p
    return d

# vim: set tabstop=4 sw=4 expandtab:
