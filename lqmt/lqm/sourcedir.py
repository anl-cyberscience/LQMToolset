from . import processed
import os
from .sources import Source
from lqmt.lqm.exceptions import ConfigurationError
import logging


class FilesToProcess(object):
    """Implements a directory traversal of each of the top-level dirs this object is initialized with"""

    def __init__(self, dirs, postProcess):
        self._iters = []
        self._dirs = dirs
        self._dirIter = iter(self._dirs)
        self._curFiles = None
        self._curDir = None
        self._postProcess = postProcess
        self._numFiles = 0
        self._numDirs = 0

        self._getNextTLD()

    def _getNextTLD(self):
        # get the next top-level directory
        self._currentTLD = next(self._dirIter)
        # and put the iterator for the list of files in the directory on the _iters list
        self._iters.append((self._currentTLD, iter(os.listdir(self._currentTLD))))

    def _advanceToNextFile(self):
        """Advance to the next file"""
        found = False
        while not found:
            # while a valid file pair (file/metadata file) has not been found
            # get the last dir & iter on the iters list
            dirName, cDirIter = self._iters[-1]
            try:
                # get the next entry from the dir
                entry = next(cDirIter)
                path = dirName + "/" + entry
                if os.path.isdir(path):
                    # if it is a path and it is not to be skipped,
                    # append an iterator of the directory's conents
                    if (not self._postProcess.skipDirectory(path)):
                        self._iters.append((path, iter(os.listdir(path))))
                elif (not entry.startswith(".")):
                    # otherwise, if the entry doesn't start with a '.'
                    if os.path.isfile(path):
                        # and it is a file, check to see if a metadata file exists
                        if os.path.exists(dirName + "/." + entry):
                            # if there is a matching metadata file
                            # check to see if we have left a directory
                            if (self._curDir != dirName):
                                # if we have, then tell the post processor
                                if (self._curDir != None):
                                    self._postProcess.leavingDirectory(self._curDir)
                                self._curDir = dirName
                                self._postProcess.enteringDirectory(self._curDir)
                                self._numDirs = self._numDirs + 1
                            self._curDir = dirName
                            # if the file hasn't laready been processed, then we found the next file
                            if (not self._postProcess.isProcessed(path)):
                                # so set the flag to exit the loop and save the file info for retrieval
                                found = True
                                self._curFiles = (path, dirName + "/." + entry)
            except StopIteration:
                # if the iteration of the current dir is done
                # get the next dir, if any, and continue
                self._iters.pop()
                if (len(self._iters) == 0):
                    self._getNextTLD()
        if not found:
            if (self._curDir != None):
                self._postProcess.leavingDirectory(self._curDir)
            raise StopIteration()

    def getNextFile(self):
        self._advanceToNextFile()
        self._numFiles = self._numFiles + 1
        return self._curFiles

    def __iter__(self):
        return self

    def __next__(self):
        return self.getNextFile()


class DirectorySource(Source):
    """ This source provides an iterator for all the file pairs (alert/metadata) contained in all of
    its children that haven't already been processed (as determined by the post-processor specified
    in its configuration)."""

    def __init__(self, config):
        self._logger = logging.getLogger("LQMT.Source.Directory")
        self.config = config

        if 'dirs' not in config:
            raise ConfigurationError("Missing required key: 'dirs' in section: 'Source.Directory'")
        self._dirs = self.config["dirs"]

        hasError = False

        for dirName in self._dirs:
            if not os.path.exists(dirName):
                self._logger.error('dir ({0}) is not a valid path'.format(dirName))
                hasError = True
        if (hasError):
            raise ConfigurationError()

        if 'post_process' not in self.config:
            post_process = "move"
            self._logger.info("post_process variable not set in user configurtion. Default of 'move' has been set. "
                              "Processed alerts will be moved.")
        else:
            post_process = self.config["post_process"]
            if post_process not in ["move", "delete", "track", "nothing"]:
                raise ConfigurationError(
                    "Invalid value for key: 'post_process' in section: 'Source.Directory': " + post_process)
        self._processedHandler = self._getProcessedHandler(post_process)

    def getFilesToProcess(self):
        self._ftp = FilesToProcess(self._dirs, self._processedHandler)
        return self._ftp

    def _getProcessedHandler(self, post_process):
        if post_process == "move":
            return processed.ProcessHandlerMove()
        elif post_process == "delete":
            return processed.ProcessHandlerDelete()
        elif post_process == "track":
            # Ground work placed for allowing user to defined where the track file is located/named. Replace string
            # below with a call to config to grab track file location
            return processed.ProcessHandlerTrackFile(".processed.txt")
        else:
            return processed.ProcessHandlerDoNothing()

    def processed(self, datafile):
        self._processedHandler.processed(datafile)

    def logStatistics(self, numAlerts):
        self._logger.info("dirs: {0} NumDirs: {1} NumFiles: {2}".format(",".join(self._dirs), self._ftp._numDirs,
                                                                        self._ftp._numFiles))
