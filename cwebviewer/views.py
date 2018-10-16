#!/usr/bin/python3
# coding: utf-8

from flask import Flask, render_template, request, make_response, url_for, redirect, Blueprint
from flask import current_app as app
from . import archive
from .consts import *
from .models import *

cwebviewer_pages = Blueprint('cwebviewer', __name__)

@cwebviewer_pages.route('/')
def index():
    return render_template("index.html")

@cwebviewer_pages.route('/<int:aid>/')
def subindex(aid):
    reload_repo_by_mtime(aid)
    return render_template("subindex.html", aid=aid, archives=app.repo[aid])

@cwebviewer_pages.route('/archive/<int:aid>/<fhash>')
def archive_(aid, fhash):
    fn = app.repo[aid][ARCHIVE][fhash]['filename']
    ar = archive.Archive(fn)

    return render_template("archive.html", aid=aid, fhash=fhash, fn=fn, archive=ar)

@cwebviewer_pages.route('/view/<int:aid>/<fhash>/<int:pid>')
def view(aid, fhash, pid):
    fn = app.repo[aid][ARCHIVE][fhash]['filename']
    ar = archive.Archive(fn)
    if pid < 0 or pid >= len(ar.fnlist):
        raise RuntimeError("insane pid: %d" % (pid))
    width = int(request.args.get('width', 512))
    step = app.config['STEP']

    return render_template("view.html", ar=ar, aid=aid, fhash=fhash, pid=pid, fn=fn, archive=ar, step=step, width=width)

def make_image_response(data):
    res = make_response(data)
    res.headers.set('Cache-Control', 'max-age=3600')
    res.headers.set('Content-Type', 'image/webp' if app.config['WANT_WEBP'] or ext_fn == ".webp" else 'image/jpeg')
    return res

@cwebviewer_pages.route('/thumbnail/<int:aid>/<fhash>')
def thumbnail(aid, fhash):
    fn = app.repo[aid][ARCHIVE][fhash]['filename']
    ar = archive.Archive(fn)
    pid = 0
    width = int(request.args.get('width', 512))
    if len(ar.fnlist) == 0:
        raise RuntimeError("empty archive")
    d = make_image(ar, pid, width, 'image/webp' in request.headers['accept'].split(',') and int(request.args.get('nowebp', 0)) != 1)
    return make_image_response(d)

@cwebviewer_pages.route('/image/<int:aid>/<fhash>/<int:pid>')
def image(aid, fhash, pid):
    fn = app.repo[aid][ARCHIVE][fhash]['filename']
    ar = archive.Archive(fn)
    if pid < 0 or pid >= len(ar.fnlist):
        raise RuntimeError("insane pid: %d" % (pid));
    width = int(request.args.get('width', 1080))

    d = make_image(ar, pid, width, 'image/webp' in request.headers['accept'].split(',') and int(request.args.get('nowebp', 0)) != 1)
    return make_image_response(d)

# vim: set tabstop=4 sw=4 expandtab:
