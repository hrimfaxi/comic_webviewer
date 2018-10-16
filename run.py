#!/usr/bin/python3
# coding: utf-8

from cwebviewer import create_app

app = create_app()
app.run(debug=True, port=app.config['PORT'], host=app.config['ADDRESS'])

# vim: set tabstop=4 sw=4 expandtab:
