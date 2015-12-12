#!/usr/bin/python2
# coding: utf-8

import logging, sys, os, SimpleHTTPServer, BaseHTTPServer
import SocketServer, zipfile, glob
import urllib

PORT = 8181

class ComicWebViewerRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    __base = BaseHTTPServer.BaseHTTPRequestHandler
    __base_handle = __base.handle

    server_version = "Apache"
    rbufsize = 0                        # self.rfile Be unbuffered

    def send_content(self, msg, headers={}):
        self.send_response(200)
        for k, v in headers.iteritems():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(msg)

    def getImage(self):
        fn = self.path.split("getImage?")[1]
        fn = self.filelist[int(fn)]
        with zipfile.ZipFile(self.zipfn, "r") as f:
            d = f.read(fn)
            self.send_content(d, { "Content-length" : "%d" % (len(d)),
                "Content-Type" : "image/jpeg"
                })

    def getImageView(self):
        id = self.path.split("getImageView?")[1]
        id = int(id)
        html = """
        <!DOCTYPE html>
<html>
<head>
<style>
  * {
    padding: 0;
    margin: 0;
  }
  .fit { /* set relative picture size */
    max-width: 100%;
    max-height: 100%;
  }
  .center {
    display: block;
    margin: auto;
  }
</style>
</head>
<body>
"""
        html += "<img src=\"getImage?%d\" class=\"center fit\" onclick=\"window.location.href = 'getImageView?%d';\">" % (id, id+1)
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
</script>"""

        self.send_content(html, { "Content-length" : "%d" % (len(html)),})

    def getZip(self):
        fn = urllib.unquote(self.path.split("getZip?")[1])
        with zipfile.ZipFile(fn, "r") as f:
            self.zipfn = fn
            self.filelist = sorted(f.namelist())
#            r = "\r\n".join(sorted(filelist))
            html = "<html><meta charset=\"utf-8\"><body>"
            i = 0
            for fn in self.filelist:
                html += "<a href=\"getImageView?%d\">%s</a><br>\n" % (i, fn)
                i+=1
            html += "</body></html>"
            self.send_content(html, { "Content-length" : "%d" % (len(html)), })

    def getIndexPage(self):
        html = "<html><meta charset=\"utf-8\"><body>"
        for zipfn in glob.glob("*.zip"):
            html += "<a href=\"getZip?%s\">%s</a><br>\n" % (zipfn, zipfn)
        html += "</body></html>"
        self.send_content(html, { "Content-length" : "%d" % (len(html)), })

    def do_GET(self):
        if self.path == "/":
            return self.getIndexPage()
        if "getZip" in self.path:
            return self.getZip()
        if "getImageView" in self.path:
            return self.getImageView()
        if "getImage" in self.path:
            return self.getImage()
        self.send_error(403, "Invalid request")

def main():
    #Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    Handler = ComicWebViewerRequestHandler
    Handler.protocol_version = "HTTP/1.1"
    SocketServer.TCPServer.allow_reuse_address = True
    SocketServer.TCPServer.daemon_threads = True
    httpd = SocketServer.TCPServer(("0.0.0.0", PORT), Handler)
    print "serving at port", PORT
    httpd.serve_forever()

if __name__ == "__main__":
    main()
