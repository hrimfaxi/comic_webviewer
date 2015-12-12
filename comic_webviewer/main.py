#!/usr/bin/python2
# coding: utf-8

import logging, sys, os, SimpleHTTPServer, BaseHTTPServer
import SocketServer, zipfile, glob
import urllib

from comic_webviewer import archive
from comic_webviewer import comic_handler

PORT = 8181

class ThreadingHTTPServer(SocketServer.ThreadingMixIn,
                           BaseHTTPServer.HTTPServer):
    def __init__ (self, server_address, RequestHandlerClass):
        BaseHTTPServer.HTTPServer.__init__ (self, server_address,
                                            RequestHandlerClass)
        " 定义此值使主线程将不等待子线程结束直接退出，使KeyboardInterrupt得到迅速响应 "
        self.daemon_threads = True

def run():
    path = "."
    if len(sys.argv) >= 2:
        path = sys.argv[1]
    archive.load(path)
    print (path)
    print ("%d archive loaded" % (len(archive.archive)))

    Handler = comic_handler.ComicWebViewerRequestHandler
    Handler.protocol_version = "HTTP/1.1"
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print ("serving at port: %d" %(PORT))
    httpd.serve_forever()

if __name__ == "__main__":
    run()
