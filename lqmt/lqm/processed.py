import os


class ProcessedHandler(object):
    """The ProcessedHandler is the superclass for various implementations
    of what to do with a file once it has been processed"""

    def processed(self, fpath):
        """Called after the file (fpath) has been processed"""
        NotImplemented

    def isProcessed(self, fpath):
        """Called to determine if the file (fpath) has been processed"""
        NotImplemented

    def enteringDirectory(self, path):
        """Called when the directory (fpath) is about to be entered by the DirectorySource"""
        pass

    def leavingDirectory(self, path):
        """Called when the directory (fpath) is about to be left by the DirectorySource"""
        pass

    def skipDirectory(self, path):
        """Called to determine if the file (fpath) should be skipped.
        Return True if the directory should be skipped"""
        pass


class ProcessHandlerMove(ProcessedHandler):
    """This class implements moving the processed file to another directory after processing"""

    def __init__(self):
        # _pdir is the directory that will be created as a child directory in the directory that contains the processed file.
        self._pdir = "processed"
        self._curdir = None

    def processed(self, fpath):
        # move the processed file to _pdir
        fdir, fn = os.path.split(fpath)
        os.rename(os.path.join(fdir, fn), os.path.join(self._curdir, fn))
        os.rename(os.path.join(fdir, "." + fn), os.path.join(self._curdir, "." + fn))

    def isProcessed(self, fpath):
        return False

    def enteringDirectory(self, path):
        # if the _pdir doesn't ewxist for this path, create it
        self._curdir = os.path.join(path, self._pdir)
        if (not os.path.exists(self._curdir)):
            os.mkdir(self._curdir)

    def skipDirectory(self, path):
        # skip this directory if it is the _pdir directory
        return os.path.basename(path) == self._pdir


class ProcessHandlerDelete(ProcessedHandler):
    """This ProcessedHandler class implements deleting the processed file after processing"""

    def processed(self, fpath):
        # delete the file
        fdir, fn = os.path.split(fpath)
        os.unlink(os.path.join(fdir, fn))
        os.unlink(os.path.join(fdir, "." + fn))

    def isProcessed(self, fpath):
        return False


class ProcessHandlerDoNothing(ProcessedHandler):
    """This ProcessedHandler class implements doing nothing after processing.
    This should only be used for debugging"""

    def processed(self, fpath):
        pass

    def isProcessed(self, fpath):
        return False


class ProcessHandlerTrackFile(ProcessedHandler):
    """This ProcessedHandler class implements adding the file's name to a list of files processed that is stored in the
    directory. This is not a terribly efficient method, as the file fill grow and so will the directory size"""

    def __init__(self, trackFile):
        self._processed = None
        self._pfile = None
        self._trackFile = trackFile

    def processed(self, fpath):
        self._pfile.write(os.path.basename(fpath) + '\n')
        self._pfile.flush()
        os.fsync(self._pfile.fileno())

    def isProcessed(self, fpath):
        return os.path.basename(fpath) in self._processed

    def enteringDirectory(self, path):
        pfile = os.path.join(path, self._trackFile)
        try:
            self._processed = {}
            open(pfile, 'a').close()  # ensures file is writable
            f = open(pfile, 'r')
            for line in f:
                self._processed[line.rstrip()] = 1
            f.close()
            self._pfile = open(pfile, 'a')
        except IOError as e:
            raise ValueError('procfile (%s) generated an IO Error: %s\n' % (pfile, e.strerror))

    def leavingDirectory(self, path):
        self._pfile.close()
        self._processed = None
