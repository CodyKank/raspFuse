#!/usr/bin/env python

from __future__ import with_statement
from time import time, localtime, strftime

import os
import sys
import errno
import stat

from fuse import FUSE, FuseOSError, Operations


class RandomFileSystem(Operations):
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
        print "-- access called on " + path
        if path == "/geiger":
            return

        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        print "-- chmod called on " + path
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        print "-- chown called on " + path
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        print "-- getattr called on " + path
        full_path = self._full_path(path)
        # full_path is../mountSource/current path within mount point
        # path is current path within mount point, eg "/myfile"
        if path == "/geiger":
            folderUser = os.getegid()
            folderGroup = os.getuid()
            curtime = time()
            st = dict(
                st_mode = (stat.S_IFREG | 0o777),
                st_size = 16384,
                st_gid = folderGroup,
                st_uid = folderUser,
                st_nlink = 1,
                st_ctime = curtime,
                st_mtime = curtime,
                st_atime = curtime,
            )
            return st
        else:
            st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        print "-- readdir called on " + path
        full_path = self._full_path(path)

        dirents = ['.', '..', 'geiger']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        print "-- readlink called on " + path
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        print "-- mknod called on " + path
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        print "-- rmdir called on " + path
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        print "-- mkdir called on " + path
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        print "-- statfs called on " + path
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        print "-- unlink called on " + path
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        print "-- symlink called on " + path
        return os.symlink(target, self._full_path(name))

    def rename(self, old, new):
        print "-- rename called on " + path
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        print "-- link called on " + path
        return os.link(self._full_path(name), self._full_path(target))

    def utimens(self, path, times=None):
        print "-- utimens called on " + path
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        print "-- open called on " + path
        if path == '/geiger':
            print "Geiger open attempted"
            return 5
        full_path = self._full_path(path)
        f = os.open(full_path, flags)
        return f
    
    def create(self, path, mode, fi=None):
        print "-- create called on " + path
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        print "-- read called on " + path
        if path == "/geiger":
            print "tried to read geiger"
            
            randCacheFh = os.open("geigerRandCache", os.O_RDONLY)
            
            size = os.lstat("geigerRandCache").st_size
            print ("cache size:", size)
            print ("length:", length, "type:", type(length))
            print ("size - length:", size - length)
            if length < size:
                os.lseek(randCacheFh, size - length, os.SEEK_END)
            bytes = os.read(randCacheFh, length).strip()
            os.close(randCacheFh)
            
            # truncate the bytes read from the end of the file
            randCacheFh = os.open("geigerRandCache", os.O_WRONLY | os.O_TRUNC)
            if length < size:
                os.ftruncate(randCacheFh, size - length)            
            os.close(randCacheFh)


            lengthRead = len(bytes)
            lengthExtra = length - lengthRead
            if lengthExtra > 0:
                print ("tried to read more bytes than cached")
                print ("supplementing with system random")
                extra = os.urandom(lengthExtra)
                bytes += extra
            return (bytes)
        
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        print "-- write called on " + path
        geigercpmStr = "Counts per minute at " + strftime("%H:%M:%S", localtime(time())) + " was "
        if path == "/geiger":
            with open("geigercpm") as geigercpmFile:
                geigercpmStr += "{0:.2f}".format(float(geigercpmFile.readline())) + "\n"

            print geigercpmStr
        with open('geigerOut.txt', 'w') as dmpFile:
            dmpFile.write(geigercpmStr)
        
        return os.path.getsize("geigercpm") 

    def truncate(self, path, length, fh=None):
        print "-- truncate called on " + path
        #full_path = self._full_path(path)
        #with open(full_path, 'r+') as f:
        #    f.truncate(length)
        
        #Do nothing, we do not want to truncate since this is our FS
        # This function must be here to allow redirection of output
        # to the FUSE file system.
        return

    def flush(self, path, fh):
        print "-- flush called on " + path
        if path == '/geiger':
            return None
        return os.fsync(fh)

    def release(self, path, fh):
        print "-- release called on " + path
        if path == '/geiger':
            return None
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        print "-- fsync called on " + path
        return self.flush(path, fh)


def main(mountpoint, root):
    FUSE(RandomFileSystem(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
