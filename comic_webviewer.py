#!/usr/bin/python3
# coding: utf-8

import argparse

from cwebviewer.config import load_json_file
from cwebviewer.manage import create_app


def positive_type(x):
    x = int(x)
    if x <= 0:
        raise argparse.ArgumentTypeError("Must be greater than 0")
    return x

def main():
    parse = argparse.ArgumentParser(description='comic webviewer')
    parse.add_argument('--debug', '-d', action='store_true', default=argparse.SUPPRESS, help='debug mode')
    parse.add_argument('--sort', '-s', choices=['name', 'time', 'size', 'random'], default=argparse.SUPPRESS, help='archive display order')
    parse.add_argument('--reverse', '-r', action='store_true', default=argparse.SUPPRESS, help='reversed sort order')
    parse.add_argument('--webp-quality', '-c', type=int, default=argparse.SUPPRESS, help='webp quaility [0-100], default: 5')
    parse.add_argument('--webp-preset', choices=[
                            'default', 'photo', 'picture',
                            'drawing', 'icon', 'text'
        ], default=argparse.SUPPRESS, help='webp preset (default/photo/picture/drawing/icon/text), default: drawing')
    parse.add_argument('--disable-webp', action='store_true', default=argparse.SUPPRESS, help='disable webp mode')
    parse.add_argument('--port', '-p', type=int, default=argparse.SUPPRESS, help='port to listen on, default: 5001')
    parse.add_argument('--address', '-a', default=argparse.SUPPRESS, help='listen address, default: 127.0.0.1')
    parse.add_argument('--img-per-page', type=positive_type, default=argparse.SUPPRESS, help='specify how many image(s) in '
                                                                                     'one view')
    parse.add_argument('--archive-per-page', type=positive_type, default=argparse.SUPPRESS, help='specify how many archive(s) in one subindex')
    parse.add_argument("directories", nargs="*", default=argparse.SUPPRESS, help="directory names to serve")

    config_namespace = parse.parse_args()
    config_input = { k.upper() : v for k, v in vars(config_namespace).items() }

    config_dict = load_json_file('config.json')
    config_dict.update(config_input)

    app = create_app(config_dict)

    app.logger.warning("listen on %s:%d" % (config_dict['ADDRESS'], config_dict['PORT']))
    app.run(debug=config_dict['DEBUG'], host=config_dict['ADDRESS'], port=config_dict['PORT'])

if __name__ == "__main__":
    main()

# vim: set tabstop=4 sw=4 expandtab:
