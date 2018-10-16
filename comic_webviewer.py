#!/usr/bin/python3
# coding: utf-8

from flask import Flask, render_template, request, make_response, url_for, redirect
from flask import current_app as capp
import argparse, os, archive, subprocess, tempfile, shutil, argparse

CWEBP_PATH = shutil.which('cwebp')
CWEBP_EXTRA_OPTIONS = [ '-mt' ]

def create_app(config):
    app = Flask(__name__)
    app.config.update(config)
    with app.app_context():
        DIRNAME = 0
        MTIME   = 1
        ARCHIVE = 2

        app.config['want_webp'] = False
        if app.config['disable_webp'] is False and CWEBP_PATH is not None:
            app.logger.warning("webp enabled, quality: %d, preset: %s" % (app.config['webp_quality'], app.config['webp_preset']))
            app.config['want_webp'] = True
        app.logger.warning("sorted by %s order%s" % (app.config['sort'], ", descending" if app.config['reverse'] else ""))
        capp.repo = [ [ dirname, os.stat(dirname).st_mtime, archive.load(dirname, app.config['sort'], app.config['reverse']) ] for dirname in app.config['directories'] ]
        for e in capp.repo:
            app.logger.warning("Directory %s: %d archvies loaded." % (e[DIRNAME], len(e[ARCHIVE])))

        @app.context_processor
        def inject_config():
            return dict(nowebp=int(request.args.get('nowebp', 0)), basename=os.path.basename, sep=os.path.sep, len=len, min=min, max=max, repo=capp.repo, DIRNAME=DIRNAME, MTIME=MTIME, ARCHIVE=ARCHIVE)

        @app.route('/')
        def index():
            return render_template("index.html")

        @app.route('/<int:aid>/')
        def subindex(aid):
            dirname = capp.repo[aid][DIRNAME]
            timestamp = os.stat(dirname).st_mtime
            if app.config['sort'] == 'random' or capp.repo[aid][MTIME] < timestamp:
                # Reloading
                capp.repo[aid] = [ dirname, os.stat(dirname).st_mtime, archive.load(dirname, app.config['sort'], app.config['reverse']) ]
            return render_template("subindex.html", aid=aid, archives=capp.repo[aid])

        @app.route('/archive/<int:aid>/<fhash>')
        def archive_(aid, fhash):
            fn = capp.repo[aid][ARCHIVE][fhash]['filename']
            ar = archive.Archive(fn)

            return render_template("archive.html", aid=aid, fhash=fhash, fn=fn, archive=ar)

        @app.route('/view/<int:aid>/<fhash>/<int:pid>')
        def view(aid, fhash, pid):
            fn = capp.repo[aid][ARCHIVE][fhash]['filename']
            ar = archive.Archive(fn)
            if pid < 0 or pid >= len(ar.fnlist):
                raise RuntimeError("insane pid: %d" % (pid))
            width = int(request.args.get('width', 512))
            step = app.config['step']

            return render_template("view.html", ar=ar, aid=aid, fhash=fhash, pid=pid, fn=fn, archive=ar, step=step, width=width)

        def make_image(app, ar, pid, width):
            d = ar.read(pid)
            ext_fn = os.path.splitext(ar.fnlist[pid])[-1].lower()
            if ext_fn != ".webp" and app.config['want_webp'] and 'image/webp' in request.headers['accept'].split(',') and int(request.args.get('nowebp', 0)) != 1:
                # convert into webp
                # cwebp didn't support stdin/stdout, output to temp file
                with tempfile.NamedTemporaryFile(prefix='comic_webviewer') as temp:
                    temp.write(d)
                    temp.flush()
                    null = open(os.devnull, 'wb')
                    cwebp_cmd = [ CWEBP_PATH ] + CWEBP_EXTRA_OPTIONS + [ '-resize', '%d' % (width), '0', '-preset', app.config['webp_preset'], '-q', '%d' % (app.config['webp_quality']), temp.name, '-o', '-']
                    app.logger.warning(cwebp_cmd)
                    p = subprocess.Popen(cwebp_cmd, stderr=null, stdout=subprocess.PIPE)
                    stdout, _ = p.communicate()
                    app.logger.warning('webp compressed: %d/%d %f%%' % (len(stdout), len(d), 100.0 * len(stdout) / len(d)))
                    d = stdout
                    del null, p

            res = make_response(d)
            res.headers.set('Cache-Control', 'max-age=3600')
            res.headers.set('Content-Type', 'image/webp' if app.config['want_webp'] or ext_fn == ".webp" else 'image/jpeg')
            return res

        @app.route('/thumbnail/<int:aid>/<fhash>')
        def thumbnail(aid, fhash):
            fn = capp.repo[aid][ARCHIVE][fhash]['filename']
            ar = archive.Archive(fn)
            pid = 0
            width = int(request.args.get('width', 512))
            if len(ar.fnlist) == 0:
                raise RuntimeError("empty archive")
            return make_image(app, ar, pid, width)

        @app.route('/image/<int:aid>/<fhash>/<int:pid>')
        def image(aid, fhash, pid):
            fn = capp.repo[aid][ARCHIVE][fhash]['filename']
            ar = archive.Archive(fn)
            if pid < 0 or pid >= len(ar.fnlist):
                raise RuntimeError("insane pid: %d" % (pid));
            width = int(request.args.get('width', 1080))

            return make_image(app, ar, pid, width)
    return app

def step_type(x):
    x = int(x)
    if x <= 0:
        raise argparse.ArgumentTypeError("Must be greater than 0")
    return x

def main():
    parse = argparse.ArgumentParser(description='comic webviewer')
    parse.add_argument('--debug', '-d', action='store_true', help='debug mode')
    parse.add_argument('--sort', '-s', choices=['name', 'time', 'size', 'random'], default='name', help='archive display order')
    parse.add_argument('--reverse', '-r', action='store_true', help='reversed sort order')
    parse.add_argument('--webp-quality', '-c', type=int, default=5, help='webp quaility [0-100], default: 5')
    parse.add_argument('--webp-preset', choices=[
                            'default', 'photo', 'picture',
                            'drawing', 'icon', 'text'
        ], default='drawing', help='webp preset (default/photo/picture/drawing/icon/text), default: drawing')
    parse.add_argument('--disable-webp', action='store_true', help='disable webp mode')
    parse.add_argument('--port', '-p', type=int, default=5001, help='port to listen on, default: 5001')
    parse.add_argument('--address', '-a', default='127.0.0.1', help='listen address, default: 127.0.0.1')
    parse.add_argument('--step', type=step_type, default=10, help='specify how many image(s) in one view')
    parse.add_argument("directories", nargs="+", help="directory names to serve")
    config = parse.parse_args()

    app = create_app(vars(config))
    app.logger.warning("listen on %s:%d" % (config.address, config.port))
    app.run(debug=config.debug, host=config.address, port=config.port)

if __name__ == "__main__":
    main()

# vim: set tabstop=4 sw=4 expandtab:
