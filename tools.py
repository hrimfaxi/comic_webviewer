#!/usr/bin/python3
# coding: utf-8

import os, re, sys, gc

" 正则表达式: 搜索所有大于等于1个的数字或非数字 "
NUMERIC_REGEXP = re.compile(r"\d+|\D+")

"""Do an in-place alphanumeric sort of the strings in <filenames>,
such that for an example "1.jpg", "2.jpg", "10.jpg" is a sorted
ordering.
"""
def _format_substring(s):
    " 是数字 "
    if s.isdigit():
        " 转化为数字 "
        return int(s)

    " 返回UTF-8编码后16进制数字形式 "
    return int(s.encode("utf-8").hex(), 16)

" 基于数字排序 "
def alphanumeric_sort(filenames, reverse=False):
    " 排序: 使用lambda函数 "
    " NUMERIC_REGEXP.findall返回数字和非数字 "
    " map对所有返回值调用_format_substring "
    filenames.sort(key=lambda s: [ _format_substring(e) for e in NUMERIC_REGEXP.findall(s)], reverse=reverse)

def sorted_by_config(archive_list):
    return sorted_by_time(archive_list)

def sorted_by_time(archive_list):
    mtime = lambda f: os.stat(archive_list[f]).st_mtime
    return sorted(archive_list, key=mtime, reverse=True)

""" 运行垃圾回收 """
def garbage_collect():
    """ Runs the garbage collector. """
    if sys.version_info[:3] >= (2, 5, 0):
        gc.collect(0)
    else:
        gc.collect()

# vim: expandtab sw=4 ts=4:
