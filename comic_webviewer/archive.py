#!/usr/bin/python2
# coding: utf-8

import glob, hashlib, os.path, zipfile, sys, locale
from comic_webviewer import tools

try:
    import rarfile
except:
    rarfile = None

""" chardet是一个非常优秀的编码识别模块 """
try:
    import chardet
except ImportError:
    chardet = None

archive = {}

def is_rar(fn):
    ext_fn = os.path.splitext(fn)[-1].lower()

    return True if ext_fn in (".rar", ".cbr") else False

def is_zip(fn):
    ext_fn = os.path.splitext(fn)[-1].lower()

    return True if ext_fn in (".zip", ".cbz") else False

def is_archive(fn):
    return is_rar(fn) or is_zip(fn)

def is_image(fn):
    ext_fn = os.path.splitext(fn)[-1].lower()

    return True if ext_fn in \
            (".jpeg", ".jpg", ".png", ".gif", ".bmp") else False

def load(path):
    global archive
    archive = { hashlib.md5(fn).hexdigest(): fn \
            for fn in filter(is_archive, glob.glob("%s/*" % (path))) }

" 从mcomix抄来 "
def to_unicode(string):
    """Convert <string> to unicode. First try the default filesystem
    encoding, and then fall back on some common encodings.
    """
    if isinstance(string, unicode):
        return string

    # Try chardet heuristic
    if chardet:
        " 尝试猜测编码 "
        probable_encoding = chardet.detect(string)['encoding'] or \
            locale.getpreferredencoding() # Fallback if chardet detection fails
    else:
        probable_encoding = locale.getpreferredencoding()

    " 尝试常见编码 "
    for encoding in (
        probable_encoding,
        sys.getfilesystemencoding(),
        'utf-8',
        'gbk',
        'latin-1'):

        try:
            ustring = unicode(string, encoding)
            return ustring

        except (UnicodeError, LookupError):
            pass

    " 实在转化不了，就用utf8，出错字符一律替换为U+FFFD (REPLACEMENT CHARACTER) "
    return string.decode('utf-8', 'replace')

class Archive(object):
    def __init__(self, path):
        self.path = path

        if rarfile and is_rar(self.path):
            with rarfile.RarFile(self.path, "r") as f:
                self.fnlist = filter(is_image, f.namelist())
		tools.alphanumeric_sort(self.fnlist)
            return

        if is_zip(self.path):
            with zipfile.ZipFile(self.path, "r") as f:
                self.fnlist = filter(is_image, f.namelist())
		tools.alphanumeric_sort(self.fnlist)
            return

        raise RuntimeError("Cannot open rar: please install python2-rarfile")

    def read(self, pid):
        if rarfile and is_rar(self.path):
            with rarfile.RarFile(self.path, "r") as f:
                return f.read(self.fnlist[pid])

        with zipfile.ZipFile(self.path, "r") as f:
            return f.read(self.fnlist[pid])

        raise RuntimeError("Cannot open rar: please install python2-rarfile")

if __name__ == "__main__":
    load_archive(".")
    print (archive)
