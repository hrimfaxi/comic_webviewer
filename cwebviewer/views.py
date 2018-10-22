#!/usr/bin/python3
# coding: utf-8

from flask import Flask, render_template, request, make_response, url_for, redirect, Blueprint, g
from flask import current_app as app
from . import archive
from .consts import *
from .models import *
from itertools import islice
import os.path

cwebviewer_pages = Blueprint('cwebviewer', __name__)

@cwebviewer_pages.before_request
def check_webp():
    g.webp = False
    if app.config['WEBP'] and 'image/webp' in request.headers['accept'].split(','):
        g.webp = True

@cwebviewer_pages.route('/')
def index():
    return render_template("index.html")

@cwebviewer_pages.route('/<int:aid>/')
@cwebviewer_pages.route('/<int:aid>/<int:page>')
def subindex(aid, page=0):
    reload_repo_by_mtime(aid)
    return render_template("subindex.html", aid=aid, archives=app.repo[aid], page=page, arch_per_page=app.config['ARCHIVE_PER_PAGE'], islice=islice, relpath=os.path.relpath)

def fix_up(s):
    try:
        r = s.encode('cp437').decode('gbk', errors='ignore')
    except:
        r = s
    return r

@cwebviewer_pages.route('/archive/<int:aid>/<fhash>')
def archive_(aid, fhash):
    fn = app.repo[aid][ARCHIVE][fhash]['filename']
    page = int(request.args.get('page', 0))
    ar = archive.Archive(fn)

    return render_template("archive.html", aid=aid, fhash=fhash, fn=fn, page=page, archive=ar, fix_up=fix_up)

@cwebviewer_pages.route('/view/<int:aid>/<fhash>/<int:pid>')
def view(aid, fhash, pid):
    fn = app.repo[aid][ARCHIVE][fhash]['filename']
    page = int(request.args.get('page', 0))
    ar = archive.Archive(fn)
    if pid < 0 or pid >= len(ar.fnlist):
        raise RuntimeError("insane pid: %d" % (pid))
    width = int(request.args.get('width', 512))

    return render_template("view.html", ar=ar, aid=aid, page=page, fhash=fhash, pid=pid, fn=fn, archive=ar, step=app.config['IMG_PER_PAGE'], width=width)

def make_image_response(data, webp):
    res = make_response(data)
    res.headers.set('Cache-Control', 'max-age=3600')
    res.headers.set('Content-Type', 'image/webp' if webp else 'image/jpeg')
    return res

@cwebviewer_pages.route('/image/<int:aid>/<fhash>')
@cwebviewer_pages.route('/image/<int:aid>/<fhash>/<int:pid>')
def image(aid, fhash, pid=0):
    fn = app.repo[aid][ARCHIVE][fhash]['filename']
    ext_fn = os.path.splitext(fn)[-1]
    ar = archive.Archive(fn)
    if pid < 0 or pid >= len(ar.fnlist):
        raise RuntimeError("insane pid: %d" % (pid));
    width = int(request.args.get('width', 1080))
    d = make_image(ar, pid, width, g.webp)
    return make_image_response(d,  ext_fn == '.webp' or g.webp)

# vim: set tabstop=4 sw=4 expandtab:
