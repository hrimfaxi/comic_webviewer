#!/usr/bin/python2
# coding: utf-8

import os, re, sys, gc

" 正则表达式: 搜索所有大于等于1个的数字或非数字 "
NUMERIC_REGEXP = re.compile(r"\d+|\D+")

" 基于数字排序 "
def alphanumeric_sort(filenames):
    "格式化子字符串为数字"
    def _format_substring(s):
        if s.isdigit():
            return int(s)
        " 返回小写形式 "
        return s.lower()

    filenames.sort(key=lambda s: map(_format_substring, NUMERIC_REGEXP.findall(s)))

""" 运行垃圾回收 """
def garbage_collect():
    """ Runs the garbage collector. """
    if sys.version_info[:3] >= (2, 5, 0):
        gc.collect(0)
    else:
        gc.collect()

# vim: expandtab:sw=4:ts=4
