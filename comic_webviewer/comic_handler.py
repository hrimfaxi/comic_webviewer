#!/usr/bin/python2
# coding: utf-8

import logging, sys, os, SimpleHTTPServer, BaseHTTPServer
import SocketServer, zipfile, glob
import urllib, urlparse, locale

try:
    import rarfile
except:
    rarfile = None

from comic_webviewer import archive

def popluate_arg(query):
    args = query.split('&')
    r = {}

    for arg in args:
        t = arg.split('=')
        if len(t) > 1:
            k, v = t
            r[k] = v

    return r

def update_archive_list(aid):
    fn = archive.archive[aid]
    a = archive.Archive(fn)

    return fn, a

class ComicWebViewerRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    __base = BaseHTTPServer.BaseHTTPRequestHandler
    __base_handle = __base.handle

    server_version = "Apache"
    rbufsize = 0                        # self.rfile Be unbuffered

    def send_content(self, content, code=200, headers={}):
        self.send_response(code)
        self.send_header("Content-length", len(content))
        for k, v in headers.iteritems():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(content)

    def index(self):
        html = "<html><head><meta charset=\"utf-8\"><title>%s</title></head><body>\n" % ("Comic Web Viewer")
        for a in sorted(archive.archive, key=lambda x: archive.archive[x]):
            html += "<a id=\"aid%s\" href=\"/archive?aid=%s\">%s</a><br>" % (a, a, os.path.basename(archive.archive[a]))
        html += "</body></html>\n"
        self.send_content(html)

    def archive(self, r):
        args = popluate_arg(r.query)

        if 'aid' not in args:
            return self.send_error(403)

        fn, arch = update_archive_list(args['aid'])
        fnlist = arch.fnlist
        aid = args['aid']

        html = "<html><head><meta charset=\"utf-8\"><title>%s</title></head><body>" % (os.path.basename(fn))
        html += "<h1>%s</h1>" % (os.path.basename(fn))
        html += "<a href='/#aid%s'>Up</a><p>\n" % (aid)
        for idx, apath in enumerate(fnlist):
            html += "<a id=\"pid%d\" href=\"view?aid=%s&pid=%d\">%s</a><br>\n" \
                    % (idx, aid, idx, (archive.to_unicode(apath).encode('utf-8')))
        html += "<a href='/#aid%s'>Up</a><p>\n" % (aid)
        html += "</body></html>"

        self.send_content(html)

    def view(self, r):
        args = popluate_arg(r.query)

        if 'aid' not in args:
            return self.send_error(403)

        if 'pid' not in args:
            return self.send_error(403)

        aid, pid = args['aid'], int(args['pid'])
        fn, arch = update_archive_list(args['aid'])
        fnlist = arch.fnlist

        html = """
        <!DOCTYPE html>
<html>
<head>
<title>%s - [%d / %d]</title>
<meta charset="utf-8">
</head>
<head>
<style>
  * {
    padding: 0;
    margin: 0;
  }
  .fit { /* set relative picture size */
    max-width: 100%%;
    max-height: 100%%;
  }
  .center {
    display: block;
    margin: auto;
  }
</style>
</head>
<body>
""" % (archive.to_unicode(fnlist[pid]).encode('utf-8'), pid+1, len(fnlist))
        html += "<div align=center style=\"padding: 4px;\">%d / %d<br>\n" % (pid+1, len(fnlist))
        if pid > 1: html += "<a href='/view?aid=%s&pid=%d'>Prev</a>\n" % (aid, pid-1)
        html += "<a href='/archive?aid=%s#pid%d'>Up</a>\n" % (aid, pid)
        if pid+1 < len(fnlist): html += "<a href='/view?aid=%s&pid=%d'>Next</a>\n" % (aid, pid+1)
        html += "</div>\n"

        if pid+1 < len(fnlist):
            html += "<img src=\"/image?aid=%s&pid=%d\" class=\"center fit\" onclick=\"window.location.href = '/view?aid=%s&pid=%d';\">\n" % (aid, pid, aid, pid+1)
            html += """
            <script src="http://code.jquery.com/jquery-latest.js"></script>
    <script type="text/javascript" language="JavaScript">
      function set_body_width() { // set body width = window width
        $('body').width($(window).width());
      }
      $(document).ready(function() {
        $(window).bind('resize', set_body_width);
        set_body_width();
      });
function getDocHeight() {
var D = document;
return Math.max(
	D.body.scrollHeight, D.documentElement.scrollHeight,
	D.body.offsetHeight, D.documentElement.offsetHeight,
	D.body.clientHeight, D.documentElement.clientHeight
	);
}
$(function() {
	$('html').keydown(function(e) {
	    if ($(window).scrollTop() + $(window).height() == getDocHeight() && (e.keyCode == 34 || e.keyCode == 32)) {
			window.location.href = '/view?aid=%s&pid=%d';
	    }
	});
});
    </script>""" % (aid, pid+1)
        else:
            html += "<img src=\"/image?aid=%s&pid=%d\" class=\"center fit\" onclick=\"window.location.href = '/archive?aid=%s';\">\n" % (aid, pid, aid)
            html += """
            <script src="http://code.jquery.com/jquery-latest.js"></script>
    <script type="text/javascript" language="JavaScript">
      function set_body_width() { // set body width = window width
        $('body').width($(window).width());
      }
      $(document).ready(function() {
        $(window).bind('resize', set_body_width);
        set_body_width();
      });
function getDocHeight() {
var D = document;
return Math.max(
	D.body.scrollHeight, D.documentElement.scrollHeight,
	D.body.offsetHeight, D.documentElement.offsetHeight,
	D.body.clientHeight, D.documentElement.clientHeight
	);
}
$(function() {
	$('html').keydown(function(e) {
	    if ($(window).scrollTop() + $(window).height() == getDocHeight() && (e.keyCode == 34 || e.keyCode == 32)) {
			window.location.href = '/archive?aid=%s';
	    }
	});
});
    </script>""" % (aid)

        self.send_content(html)

    def image(self, r):
        args = popluate_arg(r.query)

        if 'aid' not in args:
            return self.send_error(403)

        if 'pid' not in args:
            return self.send_error(403)

        aid, pid = args['aid'], int(args['pid'])
        fn, arch = update_archive_list(args['aid'])
        d = arch.read(pid)
        self.send_content(d, headers={ "Content-Type" : "image/jpeg" })

    def do_GET(self):
        try:
            r = urlparse.urlparse(self.path)

            if r.path == "/":
                return self.index()
            elif r.path == "/archive":
                return self.archive(r)
            elif r.path == "/view":
                return self.view(r)
            elif r.path == "/image":
                return self.image(r)
            elif r.path == "/favicon.ico":
                return self.send_error(404)
            return self.send_error(503, "invalid request")
        except Exception as e:
            return self.send_error(503, str(e))
