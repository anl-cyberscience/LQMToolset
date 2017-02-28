import os
import logging


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
        # _pdir is the directory that will be created as a child directory in the directory that contains the
        # processed file.
        self._processed_dir = "processed"
        self._curdir = None
        self._logger = logging.getLogger("LQMT.PostProcess.Move")

    def processed(self, fpath):
        # move the processed file to _pdir
        file_dir, file_name = os.path.split(fpath)
        os.rename(os.path.join(file_dir, file_name), os.path.join(self._curdir, file_name))
        os.rename(os.path.join(file_dir, "." + file_name), os.path.join(self._curdir, "." + file_name))
        self._logger.debug("File '{0}' was processed and moved to the processed directory located at '{1}''".format(
            file_name,
            file_dir+"/"+self._processed_dir
        ))

    def isProcessed(self, fpath):
        return False

    def enteringDirectory(self, path):
        # if the _pdir doesn't ewxist for this path, create it
        self._curdir = os.path.join(path, self._processed_dir)
        if not os.path.exists(self._curdir):
            os.mkdir(self._curdir)

    def skipDirectory(self, path):
        # skip this directory if it is the _pdir directory
        return os.path.basename(path) == self._processed_dir


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
        self._logger = logging.getLogger("LQMT.PostProcess.Track")

    def processed(self, fpath):
        self._pfile.write(os.path.basename(fpath) + '\n')
        self._pfile.flush()
        self._logger.debug("File '{0}' written to track file at location '{1}'".format(
            os.path.basename(fpath),
            self._trackFile
        ))
        os.fsync(self._pfile.fileno())

    def isProcessed(self, fpath):
        """
        Method that checks to see if a file has been tracked or not. If it's in the tracking file, then it has already
        been processed and will not be processed again.
        :param fpath: The file path to the file about to be processed.
        :return: Boolean True or False
        """
        if os.path.basename(fpath) in self._processed:
            self._logger.debug("File {} was previously processed and tracked. It will not be processed again.".format(
                os.path.basename(fpath)
            ))
            return True
        else:
            return False

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
