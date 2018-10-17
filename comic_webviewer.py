#!/usr/bin/python3
# coding: utf-8

import argparse, os, subprocess, tempfile, shutil, argparse
from cwebviewer import create_app

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
    parse.add_argument('--step', type=step_type, default=20, help='specify how many image(s) in one view')
    parse.add_argument("directories", nargs="+", help="directory names to serve")
    config = parse.parse_args()
    d = { k.upper() : v for k, v in vars(config).items() }
    app = create_app(d)
    app.logger.warning("listen on %s:%d" % (config.address, config.port))
    app.run(debug=config.debug, host=config.address, port=config.port)

if __name__ == "__main__":
    main()

# vim: set tabstop=4 sw=4 expandtab:
