#!/usr/bin/python3
# coding: utf-8

from io import StringIO
import configparser, os

def load_ini(dirname, app):
    config_fn = os.path.join(dirname, ".comic_webviewer.conf")
    config = configparser.ConfigParser()
    config['default'] = {
            "sort": app.config['SORT'],
            "reverse" : app.config['REVERSE'],
            'archive_per_page': app.config['ARCHIVE_PER_PAGE'],
            'archive_reverse' : False,
            'webp': app.config['WEBP'],
            'img_per_page' : app.config['IMG_PER_PAGE'],
            'webp_quality': app.config['WEBP_QUALITY'],
            'webp_preset': app.config['WEBP_PRESET'],
            'resize': True,
            'thumbnail_in_archive' : False,
            'cache_time': 3600,
            'redis': app.config['REDIS'],
            'redis_host' : app.config['REDIS_HOST'],
            'redis_port' : app.config['REDIS_PORT'],
            'redis_expire_time' : app.config['REDIS_EXPIRE_TIME'],
            }

    if os.path.isfile(config_fn):
        inistr = "[default]\n" + open(config_fn).read()
        io = StringIO(inistr)
        config.read_file(io)

    return config['default']

def save_ini(inipath, ini):
    sio = StringIO()
    with open(inipath, "w") as inifp:
        config = configparser.ConfigParser()
        config['default'] = ini
        config.write(sio)
        sio.seek(0)
        for l in sio:
            if l == '[default]\n':
                continue
            inifp.write(l)

# vim: set tabstop=4 sw=4 expandtab:
