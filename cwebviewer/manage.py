import os
from flask import Flask, render_template, request, make_response, url_for, redirect, Blueprint
from flask import current_app as app
from itertools import islice

from cwebviewer.config import load_json_file
from .views import cwebviewer_pages
from .consts import *
from .archive import Repo

def create_app(config=None):
    app = Flask(__name__)
    app.secret_key = os.urandom(16)

    if config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(config)

    with app.app_context():
        if CWEBP_PATH is not None:
            app.logger.warning("webp enabled, quality: %d, preset: %s" % (app.config['WEBP_QUALITY'], app.config['WEBP_PRESET']))
            app.config['WEBP'] = True
        else:
            app.config['WEBP'] = False

        app.logger.warning("default sorted by %s order%s" % (app.config['SORT'], ", descending" if app.config['REVERSE'] else ""))
        app.repos = [ Repo(dirname, app) for dirname in app.config['DIRECTORIES']]
        for e in app.repos:
            app.logger.warning("Directory %s: %d archvies loaded." % (e.dirname, len(e.comics)))
        app.register_blueprint(cwebviewer_pages)
        @app.template_filter('strip_path')
        def strip_path(s, subdir):
            return os.path.relpath(s, subdir)
        @app.context_processor
        def inject_config():
            return dict(basename=os.path.basename, islice=islice, app=app)

    return app

# vim: set tabstop=4 sw=4 expandtab:
