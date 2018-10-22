#!/usr/bin/python3
# coding: utf-8

from flask import Flask, render_template, request, make_response, url_for, redirect, Blueprint, g, session
from flask import current_app as app
from . import archive
from .consts import *
from .models import *
import os.path

cwebviewer_pages = Blueprint('cwebviewer', __name__)

def fix_up(s):
    try:
        r = s.encode('cp437').decode('gbk', errors='ignore')
    except:
        r = s
    return r

@cwebviewer_pages.before_request
def check_webp():
    g.webp = False
    if app.config['WEBP'] and 'image/webp' in request.headers['accept'].split(','):
        g.webp = True
    g.arch_per_page = app.config['ARCHIVE_PER_PAGE']
    g.fix_up = fix_up
    g.step=app.config['IMG_PER_PAGE']
    g.page=session.get('page', 0)

@cwebviewer_pages.route('/')
def index():
    return render_template("index.html")

@cwebviewer_pages.route('/<int:aid>/')
@cwebviewer_pages.route('/<int:aid>/<int:page>')
def subindex(aid, page=0):
    g.page = session['page'] = page
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

    return render_template("view.html", ar=ar, aid=aid, fhash=fhash, pid=pid, fn=fn, archive=ar, width=width)

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
