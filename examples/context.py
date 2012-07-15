#!/usr/bin/env python

from errno import ENOENT
from stat import S_IFDIR, S_IFREG
from sys import argv, exit
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn, fuse_get_context


class Context(LoggingMixIn, Operations):
    'Example filesystem to demonstrate fuse_get_context()'

    def getattr(self, path, fh=None):
        uid, gid, pid = fuse_get_context()
        if path == b'/':
            st = dict(st_mode=(S_IFDIR | 0755), st_nlink=2)
        elif path == b'/uid':
            size = len('%s\n' % uid)
            st = dict(st_mode=(S_IFREG | 0444), st_size=size)
        elif path == b'/gid':
            size = len('%s\n' % gid)
            st = dict(st_mode=(S_IFREG | 0444), st_size=size)
        elif path == b'/pid':
            size = len('%s\n' % pid)
            st = dict(st_mode=(S_IFREG | 0444), st_size=size)
        else:
            raise FuseOSError(ENOENT)
        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time()
        return st

    def read(self, path, size, offset, fh):
        uid, gid, pid = fuse_get_context()
        encoded = lambda x: ('%s\n' % x).encode('utf-8')

        if path == b'/uid':
            return encoded(uid)
        elif path == b'/gid':
            return encoded(gid)
        elif path == b'/pid':
            return encoded(pid)

        raise RuntimeError('unexpected path: %r' % path)

    def readdir(self, path, fh):
        return [b'.', b'..', b'uid', b'gid', b'pid']

    # Disable unused operations:
    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
    opendir = None
    release = None
    releasedir = None
    statfs = None


if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    fuse = FUSE(Context(), argv[1], foreground=True, ro=True)
