#!/usr/bin/env python

from __future__ import with_statement
from time import time

import os
import sys
import errno
import stat

from fuse import FUSE, FuseOSError, Operations


class Passthrough(Operations):
    def __init__(self, root):
        self.root = root

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):        
        full_path = self._full_path(path)
        #print "*******Acess Path*******"
        #print full_path
        #print path
        #print self
        #print "***************************"
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        #print("*******Changing The Permissions*********")
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        #print("*******Change Owner*********")
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        outstr = "Tried to read geiger\n"
        #print "==========GetAttr=========="
        #print full_path
        #print path
        #print self
        #print "==========================="

        # full_path is../mountSource/current path within mount point
        # path is current path within mount point, eg "/myfile"
        if path == "/geiger":
            st = dict(st_mode=(stat.S_IFREG | 0o777 | stat.S_IWUSR),st_size=len(outstr), st_gid=os.getegid(), st_uid=os.getuid(),
                    st_nlink=1)
            st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time()
            return st
        else:
            st = os.lstat(full_path)
        #print "========st value========="
        #print st
        #print "========================="
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        #print("*******Reads Directory*********")
        full_path = self._full_path(path)

        dirents = ['.', '..', 'geiger']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        #print("*******Reads Link*********")
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        #print("*******Create Device Files*********")
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        #print("*******Remove Directory*********")
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        #print("*******Make Directory*********")
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        #print "statfs"
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        #print "unlink"
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        #print "symlink"
        return os.symlink(target, self._full_path(name))

    def rename(self, old, new):
        #print "rename"
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        #print "link"
        return os.link(self._full_path(name), self._full_path(target))

    def utimens(self, path, times=None):
        #print "utimens"
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        #print "Open Attempted"
        if path == '/geiger':
            #print "Geiger open attempted"
            return 5
        full_path = self._full_path(path)
        #return os.open(full_path, flags)
        f = os.open(full_path, flags)
        #print f
        return f
    
    def create(self, path, mode, fi=None):
        #print "create"
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        #print "read"
        if path == "/geiger":
            #print "tried to read geiger"
            outstr = "Tried to read geiger\n"
            #st = os.lstat(self._full_path("."))
            randCache = open("geigerRandCache")
            # To do: add check for the length of file.
            bytes = randCache.read(length)
            #print "bytes: " + bytes
            randCache.close()
            #return (outstr.encode('utf-8'))
            return (bytes)
        
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        geigercpmStr = ""
        if path == "/geiger":
            with open("geigercpm") as geigercpmFile:
                geigercpmStr = geigercpmStr + geigercpmFile.readline()
            print geigercpmStr
        with open('geigerOut.txt', 'w') as dmpFile:
            dmpFile.write(geigercpmStr)
        
        return os.path.getsize("geigercpm") 

    def truncate(self, path, length, fh=None):
        # Do nothing, we do not want to truncate since this is our FS
        # This function must be here to allow redirection of output
        # to the FUSE file system.
        return


    def flush(self, path, fh):
        #print "Flush"
        if path == '/geiger':
            return None
        return os.fsync(fh)

    def release(self, path, fh):
        #print "tried to release " + path
        if path == '/geiger':
            return None
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)


def main(mountpoint, root):
    FUSE(Passthrough(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
