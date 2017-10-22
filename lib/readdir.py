#!/usr/bin/env python
# Copyright Genome Research Ltd 2014
# Author Guy Coates <gmpc@sanger.ac.uk>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
This module provides a python interface to the readdir
system call.
"""
import ctypes
import platform
import os



# Ctypes boilerplate for readdir/opendir/closedir
if platform.system() == 'Darwin':
  mylibc = "/usr/lib/libc.dylib"
else:
  mylibc = "libc.so.6"

_clib = ctypes.CDLL(mylibc, use_errno=True)

class _cdirent(ctypes.Structure):
    _fields_ = [
        ("ino_t", ctypes.c_ulong),
        ("off_t", ctypes.c_ulong),
        ("d_reclen", ctypes.c_short),
        ("d_type",  ctypes.c_ubyte),
        ("d_name", ctypes.c_char * 4000)
]

class _c_dir(ctypes.Structure):
    pass

_dirent_p = ctypes.POINTER(_cdirent)
_c_dir_p = ctypes.POINTER(_c_dir)
_opendir = _clib.opendir
_opendir.argtypes = [ctypes.c_char_p]
_opendir.restype = _c_dir_p
_closedir = _clib.closedir
_closedir.argtypes = [_c_dir_p]
_closedir.restype = ctypes.c_int
_readdir = _clib.readdir
_readdir.argtypes = [_c_dir_p]
_readdir.restype = _dirent_p


class dirent(ctypes.Structure):
    """This is a python version of the C dirent structure returned by readdir.
    See the readdir manpage for details of the structure.
    """
    def __init__(self, cdirent=None):
        attributes = ["ino_t", "off_t", "d_reclen",
                      "d_type", "d_name"]

        for a in attributes:
            if cdirent:
                setattr(self, a, getattr(cdirent, a))
            else:
                setattr(self, a, None)

def readdir(directory):
    """Calls readdir on a directory and returns a list of dirent objects.
    """
    entries = []
    dirp = _opendir(directory)
    if not bool(dirp):
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))
    else:
        while True:
            p = _readdir(dirp)
            if not p:
                break
            d = dirent(p.contents)
            entries.append(d)
    _closedir(dirp)
    return (entries)
