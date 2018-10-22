#!/usr/bin/python3
# coding: utf-8

from flask import Flask, render_template, request, make_response, url_for, redirect, Blueprint
from flask import current_app as app
import os
from itertools import islice
from .views import cwebviewer_pages
from .consts import *

def create_app(config=None):
    app = Flask(__name__)
    app.secret_key = os.urandom(16)
    app.config.from_mapping(
            PORT = 5001,
            ADDRESS = "127.0.0.1",
            WEBP=True,
            WEBP_QUALITY=5,
            WEBP_PRESET='drawing',
            DISABLE_WEBP=False,
            SORT='name',
            REVERSE=False,
            IMG_PER_PAGE=20,
            ARCHIVE_PER_PAGE=20,
            DIRECTORIES=[ '.' ],
    )

    if config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(config)

    with app.app_context():
        app.config['WEBP'] = False
        if app.config['DISABLE_WEBP'] is False and CWEBP_PATH is not None:
            app.logger.warning("webp enabled, quality: %d, preset: %s" % (app.config['WEBP_QUALITY'], app.config['WEBP_PRESET']))
            app.config['WEBP'] = True
        app.logger.warning("sorted by %s order%s" % (app.config['SORT'], ", descending" if app.config['REVERSE'] else ""))
        app.repo = [[dirname, os.stat(dirname).st_mtime, archive.load(dirname, app.config['SORT'], app.config['REVERSE'])] for dirname in app.config['DIRECTORIES']]
        for e in app.repo:
            app.logger.warning("Directory %s: %d archvies loaded." % (e[DIRNAME], len(e[ARCHIVE])))
        app.register_blueprint(cwebviewer_pages)
        @app.context_processor
        def inject_config():
            return dict(basename=os.path.basename, len=len, min=min, max=max, islice=islice, relpath=os.path.relpath, app=app, DIRNAME=DIRNAME, MTIME=MTIME, ARCHIVE=ARCHIVE)

    return app

# vim: set tabstop=4 sw=4 expandtab:
