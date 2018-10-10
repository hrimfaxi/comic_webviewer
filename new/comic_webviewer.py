#!/usr/bin/python3
# coding: utf-8

from flask import Flask, render_template, request, make_response, url_for
from flask import current_app as capp
import argparse, os, archive, subprocess, tempfile, logging

CWEBP_QUALITY=int(os.getenv('CWEBP_QUALITY', 10))

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

    if pid+1 < len(ar.fnlist):
        next_location = url_for('view', aid=aid, pid=pid+1)
    else:
        next_location = url_for('archive_', aid=aid, _anchor=aid)

    return render_template("view.html", ar=ar, aid=aid, pid=pid, fn=fn, archive=ar, basename=os.path.basename, next_location=next_location, len=len)

@app.route('/image/<aid>')
def image(aid):
    pid = request.args.get('pid')
    fn = capp.archives[aid]
    ar = archive.Archive(fn)
    pid = int(request.args.get('pid'))
    d = ar.read(pid)
    want_webp = False

    if 'image/webp' in request.headers['accept'].split(','):
        # convert into webp
        # cwebp didn't support stdin/stdout, output to temp file
        want_webp = True
        with tempfile.NamedTemporaryFile(prefix='comic_webviewer') as temp:
            temp.write(d)
            temp.flush()
            null = open(os.devnull, 'wb')
            p = subprocess.Popen(['cwebp', '-preset', 'drawing', '-q', '%d' % (CWEBP_QUALITY), temp.name, '-o', '-'], stderr=null, stdout=subprocess.PIPE)
            stdout, _ = p.communicate()
            logging.warning('Webp: %d/%d %f%%' % (len(stdout), len(d), 100.0 * len(stdout) / len(d)))
            d = stdout
            del null, p

    res = make_response(d)
    res.headers.set('Cache-Control', 'max-age=3600')
    res.headers.set('Content-Type', 'image/webp' if want_webp else 'image/jpeg')
    return res

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
