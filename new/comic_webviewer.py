#!/usr/bin/python3
# coding: utf-8

from flask import Flask, render_template, request, make_response, url_for
from flask import current_app as capp
import argparse, os, archive, subprocess, tempfile, logging, shutil, argparse

CWEBP_PATH = shutil.which('cwebp')

def create_app(config):
    app = Flask(__name__)
    app.config.update(config)
    with app.app_context():
        app.config['want_webp'] = False
        if app.config['disable_webp'] is False and CWEBP_PATH is not None:
            logging.warning("webp enabled, quality: %d, preset: %s" % (app.config['webp_quality'], app.config['webp_preset']))
            app.config['want_webp'] = True
        capp.archives = archive.load(".", app.config['sort'], app.config['reverse'])
        capp.path_timestamp = os.stat(".").st_mtime

        @app.route('/')
        def index():
            nowebp = int(request.args.get('nowebp', 0))
            timestamp = os.stat(".").st_mtime
            if capp.path_timestamp < timestamp:
                # Reloading
                capp.archives = archive.load(".")
                capp.path_timestamp = timestamp
            return render_template("index.html", archives=capp.archives, basename=os.path.basename, nowebp=nowebp)

        @app.route('/archive/<aid>')
        def archive_(aid):
            nowebp = int(request.args.get('nowebp', 0))
            fn = capp.archives[aid]['filename']
            ar = archive.Archive(fn)

            return render_template("archive.html", aid=aid, fn=fn, archive=ar, basename=os.path.basename, enumerate=enumerate, nowebp=nowebp)

        @app.route('/view/<aid>')
        def view(aid):
            fn = capp.archives[aid]['filename']
            ar = archive.Archive(fn)
            pid = int(request.args.get('pid'))
            nowebp = int(request.args.get('nowebp', 0))

            if pid+1 < len(ar.fnlist):
                next_location = url_for('view', aid=aid, pid=pid+1, nowebp=nowebp)
            else:
                next_location = url_for('archive_', aid=aid, _anchor=aid, nowebp=nowebp)

            return render_template("view.html", ar=ar, aid=aid, pid=pid, nowebp=nowebp, fn=fn, archive=ar, basename=os.path.basename, next_location=next_location, len=len)

        @app.route('/image/<aid>')
        def image(aid):
            pid = request.args.get('pid')
            fn = capp.archives[aid]['filename']
            ar = archive.Archive(fn)
            pid = int(request.args.get('pid'))
            d = ar.read(pid)

            if app.config['want_webp'] and 'image/webp' in request.headers['accept'].split(',') and request.args.get('nowebp', 0) != "1":
                # convert into webp
                # cwebp didn't support stdin/stdout, output to temp file
                with tempfile.NamedTemporaryFile(prefix='comic_webviewer') as temp:
                    temp.write(d)
                    temp.flush()
                    null = open(os.devnull, 'wb')
                    p = subprocess.Popen([CWEBP_PATH, '-preset', app.config['webp_preset'], '-q', '%d' % (app.config['webp_quality']), temp.name, '-o', '-'], stderr=null, stdout=subprocess.PIPE)
                    stdout, _ = p.communicate()
                    logging.warning('webp compressed: %d/%d %f%%' % (len(stdout), len(d), 100.0 * len(stdout) / len(d)))
                    d = stdout
                    del null, p

            res = make_response(d)
            res.headers.set('Cache-Control', 'max-age=3600')
            res.headers.set('Content-Type', 'image/webp' if app.config['want_webp'] else 'image/jpeg')
            return res
    return app

def main():
    parse = argparse.ArgumentParser(description='comic webviewer')
    parse.add_argument('--debug', '-d', action='store_true', help='debug mode')
    parse.add_argument('--sort', '-s', choices=['name', 'time', 'size'], default='filename', help='archive display order')
    parse.add_argument('--reverse', '-r', action='store_true', help='reversed sort order')
    parse.add_argument('--webp-quality', '-c', type=int, default=5, help='webp quaility [0-100], default: 5')
    parse.add_argument('--webp-preset', choices=[
                            'default', 'photo', 'picture',
                            'drawing', 'icon', 'text'
        ], default='drawing', help='webp preset (default/photo/picture/drawing/icon/text), default: drawing')
    parse.add_argument('--disable-webp', action='store_true', help='disable webp mode')
    parse.add_argument('--port', '-p', type=int, default=5001, help='port to listen on, default: 5001')
    parse.add_argument('--address', '-a', default='127.0.0.1', help='listen address, default: 127.0.0.1')
    config = parse.parse_args()

    app = create_app(vars(config))
    logging.warning("listen on %s" % (config.address))
    app.run(debug=config.debug, host=config.address, port=config.port)

if __name__ == "__main__":
    main()
