#!/usr/bin/python3
# coding: utf-8

from flask import Flask, render_template, request, make_response
from flask import current_app as capp
import argparse, os, archive

app = Flask(__name__)
with app.app_context():
    capp.root_path = os.path.sep.join(app.instance_path.split(os.path.sep)[:-1])
    capp.archives = archive.load(capp.root_path)
    capp.path_timestamp = os.stat(capp.root_path).st_mtime

@app.route('/')
def index():
    timestamp = os.stat(capp.root_path).st_mtime
    if capp.path_timestamp < timestamp:
        # Reloading
        capp.archives = archive.load(capp.root_path)
        capp.path_timestamp = timestamp
    return render_template("index.html", archives=capp.archives, basename=os.path.basename)

@app.route('/archive/<aid>')
def archive_(aid):
    fn = capp.archives[aid]
    ar = archive.Archive(fn)

    return render_template("archive.html", aid=aid, fn=fn, archive=ar, basename=os.path.basename, enumerate=enumerate)

@app.route('/view/<aid>')
def view(aid):
    fn = capp.archives[aid]
    ar = archive.Archive(fn)
    pid = int(request.args.get('pid'))

    return render_template("view.html", ar=ar, aid=aid, pid=pid, fn=fn, archive=ar, basename=os.path.basename, len=len)

@app.route('/image/<aid>')
def image(aid):
    pid = request.args.get('pid')
    fn = capp.archives[aid]
    ar = archive.Archive(fn)
    pid = int(request.args.get('pid'))
    d = ar.read(pid)

    res = make_response(d)
    res.headers.set('Content-Type', 'image/jpeg')
    return res

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
