#!/usr/bin/python3
# coding: utf-8

import os.path
from math import ceil, floor

from flask import Flask, render_template, request, make_response, url_for, redirect, Blueprint, g, session, flash
from flask import current_app as app
from .consts import *
from .models import *
from .archive import Repo, Archive
from .ini import save_ini

cwebviewer_pages = Blueprint('cwebviewer', __name__)

def fix_up_encoding(s):
    try:
        r = s.encode('cp437').decode(app.config['ARCHIVE_FILENAME_ENCODING'], errors='ignore')
    except:
        r = s
    return r

@cwebviewer_pages.before_request
def check_webp():
    g.fix_up_encoding = fix_up_encoding
    g.page=session.get('page', 0)

@cwebviewer_pages.route('/')
def index():
    flash('<h1>Comic index: </h1>')
    return render_template("index.html")

# 根据fhash和repo查找对应页号
def fhash2page(config, repo, fhash):
    # 未找到返回0
    if fhash not in repo.comics:
        return 0

    idx = list(repo.comics.keys()).index(fhash)
    arch_per_page = config.getint('archive_per_page')
    page = floor(idx / arch_per_page)
    return page

@cwebviewer_pages.route('/<int:repo_id>/')
@cwebviewer_pages.route('/<int:repo_id>/<int:page>')
def subindex(repo_id, page=0):
    reload_repo_by_mtime(repo_id)
    config = app.repos[repo_id].config
    g.arch_per_page = config.getint('archive_per_page')
    total_page = ceil(len(app.repos[repo_id].comics) / g.arch_per_page)
    g.page = session['page'] = max(min(page, total_page), 0)
    flash('<div align=center>%d/%d</div>' % (page+1, total_page))
    return render_template("subindex.html", repo_id=repo_id, repo=app.repos[repo_id])

@cwebviewer_pages.route('/search', methods=['GET'])
def search():
    repo_id = int(request.args.get('repo_id'))
    keyword = request.args.get('keyword')
    if keyword is None:
        return redirect(url_for('.index'))
    page = int(request.args.get('page', 0))
    reload_repo_by_mtime(repo_id)
    config = app.repos[repo_id].config
    g.arch_per_page = config.getint('archive_per_page')
    order = config['sort']
    if order == 'random':
        order = 'name'
    s = app.repos[repo_id].search(keyword, order, config.getboolean('reverse'))
    total_page = ceil(len(s.comics) / g.arch_per_page)
    g.page = session['page'] = max(min(page, total_page), 0)
    flash('<div align=center>%d/%d</div>' % (page+1, total_page))
    return render_template("search.html", repo_id=repo_id, repo=s, keyword=keyword, page=page)

@cwebviewer_pages.route('/archive/<int:repo_id>/<fhash>')
def archive_(repo_id, fhash):
    g.config = app.repos[repo_id].config
    g.fhash2page = fhash2page
    fn = app.repos[repo_id].comics[fhash]['filename']
    ar = Archive(fn, g.config.getboolean('archive_reverse'))
    flash('<h1>%s</h1>'%(os.path.basename(fn)))

    return render_template("archive.html", repo_id=repo_id, fhash=fhash, fn=fn, archive=ar)

@cwebviewer_pages.route('/night')
def night():
    try:
        session['night'] = not session['night']
    except KeyError:
        session['night'] = True

    return redirect(url_for('.index'))

@cwebviewer_pages.route('/view/<int:repo_id>/<fhash>/<int:pid>')
def view(repo_id, fhash, pid):
    g.config = app.repos[repo_id].config
    g.fhash2page = fhash2page
    g.step = g.config.getint('img_per_page')
    fn = app.repos[repo_id].comics[fhash]['filename']
    ar = Archive(fn, g.config.getboolean('archive_reverse'))
    if pid < 0 or pid >= len(ar.fnlist):
        raise RuntimeError("insane pid: %d" % (pid))
    width = int(request.args.get('width', 512))
    return render_template("view.html", ar=ar, repo_id=repo_id, fhash=fhash, pid=pid, fn=fn, archive=ar, width=width)

def make_image_response(data, webp, config):
    res = make_response(data)
    res.headers.set('Cache-Control', 'max-age=%d' % (config.getint('cache_time')))
    res.headers.set('Content-Type', 'image/webp' if webp else 'image/jpeg')
    return res

@cwebviewer_pages.route('/image/<int:repo_id>/<fhash>')
@cwebviewer_pages.route('/image/<int:repo_id>/<fhash>/<int:pid>')
def image(repo_id, fhash, pid=0):
    config = app.repos[repo_id].config
    fn = app.repos[repo_id].comics[fhash]['filename']
    ext_fn = os.path.splitext(fn)[-1]
    ar = Archive(fn, config.getboolean('archive_reverse'))
    if pid < 0 or pid >= len(ar.fnlist):
        raise RuntimeError("insane pid: %d" % (pid));
    width = int(request.args.get('width', 1080))
    d, is_webp = make_image(repo_id, ar, pid, width, 'image/webp' in request.headers['accept'].split(','), config)
    return make_image_response(d,  ext_fn == '.webp' or is_webp, config)

def normalize_boolean(dict_, name):
    if name in dict_ and dict_[name] == 'on':
        dict_[name] = True
    else:
        dict_[name] = False

def normalize_int(dict_, name):
    dict_[name] = int(dict_[name])

@cwebviewer_pages.route('/option/<int:repo_id>', methods=['GET', 'POST'])
def option(repo_id=0):
    repo = app.repos[repo_id]
    config = repo.config

    if request.method == "POST":
        t = request.form.to_dict(flat=True)
        normalize_boolean(t, 'webp')
        normalize_boolean(t, 'reverse')
        normalize_boolean(t, 'resize')
        normalize_boolean(t, 'archive_reverse')
        if 'webp_quality' in t:
            normalize_int(t, 'webp_quality')
        normalize_int(t, 'img_per_page')
        normalize_int(t, 'cache_time')
        if 'submit' in t:
            del(t['submit'])
        print (t)
        config_fn = os.path.join(repo.dirname, ".comic_webviewer.conf")
        print (config_fn)
        save_ini(config_fn, t)
        repo.reload(app)

        return redirect(url_for('.subindex', repo_id=repo_id))
    return render_template('option.html', config=config, repo=repo, repo_id=repo_id)

# vim: set tabstop=4 sw=4 expandtab:
