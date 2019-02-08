#!/usr/bin/python3
# coding: utf-8

import os, tempfile, subprocess, pickle
from flask import current_app as app
from .consts import *
from .archive import Repo
from .ini import load_ini

try:
    import redis
except ModuleNotFoundError:
    redis = None

REDIS = None

def reload_repo(repo_id):
    dirname = app.repos[repo_id].dirname
    app.repos[repo_id] = Repo(dirname, app)

def reload_repo_by_mtime(repo_id):
    dirname = app.repos[repo_id].dirname
    timestamp = os.stat(dirname).st_mtime
    config = load_ini(dirname, app)
    if config['sort'] == 'random' or app.repos[repo_id].st_mtime < timestamp:
        reload_repo(repo_id)

def gen_redis_id(repo_id, ar_path, fn_name, width, browser_want_webp, config):
    webp_str = "nowebp"
    if browser_want_webp and config.getboolean('webp'):
        webp_preset = config['webp_preset']
        webp_quality = config.getint("webp_quality")
        resize = config.getboolean('resize')
        webp_str = "%d_%s" % (webp_quality, webp_preset)
    return "%d_%s_%s_%d_%s_%s" % (repo_id, ar_path, fn_name, width, webp_str, resize)

def make_image(repo_id, ar, pid, width, browser_want_webp, config):
    global REDIS
    if REDIS is None and redis is not None and config.getboolean('redis'):
        REDIS = redis.Redis(host=config['redis_host'], port=config.getint('redis_port'))
        app.logger.warning("Redis enabled")
    if REDIS is not None:
        id_ = gen_redis_id(repo_id, ar.path, ar.fnlist[pid], width, browser_want_webp, config)
        try:
            r = REDIS.get(id_)
            if r is not None:
                app.logger.debug("Cache hit on redis: {}".format(id_))
            img, webp = pickle.loads(r)
            return img, webp
        except:
            pass

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
            cwebp_cmd = [ CWEBP_PATH ] + CWEBP_EXTRA_OPTIONS
            if config.getboolean('resize'):
                cwebp_cmd += [ '-resize', '%d' % (width), '0', ]
            cwebp_cmd += [ '-preset', config['webp_preset'], '-q', '%d' % (config.getint('webp_quality')), temp.name, '-o', '-']
            app.logger.warning(cwebp_cmd)
            p = subprocess.Popen(cwebp_cmd, stderr=null, stdout=subprocess.PIPE)
            stdout, _ = p.communicate()
            app.logger.warning('webp compressed: %d/%d %f%%' % (len(stdout), len(d), 100.0 * len(stdout) / len(d)))
            d = stdout
            del null, p
            is_webp = True

    if REDIS is not None:
        try:
            REDIS.set(id_, pickle.dumps((d, is_webp), protocol=-1), ex=config.getint('redis_expire_time'))
            app.logger.debug("Store {} on redis".format(id_))
        except:
            pass

    return d, is_webp

# vim: set tabstop=4 sw=4 expandtab:
