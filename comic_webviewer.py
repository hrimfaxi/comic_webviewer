#!/usr/bin/python3
# coding: utf-8

import argparse

from cwebviewer.config import load_json_file
from cwebviewer.manage import create_app
from flask_basicauth import BasicAuth

def positive_type(x):
    x = int(x)
    if x <= 0:
        raise argparse.ArgumentTypeError("Must be greater than 0")
    return x

def main():
    parse = argparse.ArgumentParser(description='comic webviewer')
    parse.add_argument('--debug', '-d', action='store_true', default=argparse.SUPPRESS, help='debug mode')
    parse.add_argument('--sort', '-s', choices=['name', 'time', 'size', 'random'], default=argparse.SUPPRESS, help='default archive display order')
    parse.add_argument('--reverse', '-r', action='store_true', default=argparse.SUPPRESS, help='default reversed sort order')
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

    if app.config['USE_WEBAUTH']:
        app.config['BASIC_AUTH_USERNAME'] = app.config['WEBAUTH_USERNAME']
        app.config['BASIC_AUTH_PASSWORD'] = app.config['WEBAUTH_PASSWORD']
        app.config['BASIC_AUTH_FORCE'] = True

    basic_auth = BasicAuth(app)

    app.logger.warning("listen on %s:%d" % (config_dict['ADDRESS'], config_dict['PORT']))

    ad = {
            'debug': config_dict['DEBUG'],
            'host': config_dict['ADDRESS'],
            'port': config_dict['PORT'],
    }

    # To generate a self-signed cert: openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 3650
    # Or ECC prime256v1: openssl ecparam -out key.pem -name prime256v1 -genkey
    #     openssl req -new -key key.pem -x509 -nodes -days 365 -out cert.pem
    #     openssl x509 -in cert.pem -noout -text
    if app.config['USE_TLS']:
        ad['ssl_context'] = ('cert.pem', 'key.pem')

    app.run(**ad)

if __name__ == "__main__":
    main()

# vim: set tabstop=4 sw=4 expandtab:
