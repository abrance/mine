#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import codecs

from logging import FileHandler
import logging.config

basedir = os.path.abspath(os.path.dirname(__file__))
logdir = os.path.join(basedir, 'logs')
logini_path = os.path.join(basedir, 'log.ini')

if not os.path.exists(logdir):
    os.mkdir(logdir)

class SafeFileHandler(FileHandler):

    def __init__(self, filename, mode, encoding=None, delay=0):
        """
        Use the specified filename for streamed logging
        """
        if codecs is None:
            encoding = None
        FileHandler.__init__(self, filename, mode, encoding, delay)
        self.mode = mode
        self.encoding = encoding
        self.suffix = "%Y-%m-%d"
        self.suffix_time = ""
        self.delay = delay

    def emit(self, record):
        """
        Emit a record.

        Always check time
        """
        try:
            if self.check_baseFilename(record):
                self.build_baseFilename()
            FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def check_baseFilename(self, record):
        """
        Determine if builder should occur.

        record is not used, as we are just comparing times,
        but it is needed so the method signatures are the same
        """
        timeTuple = time.localtime()

        if (self.suffix_time != time.strftime(self.suffix, timeTuple) or not
            os.path.exists(self.baseFilename+'.'+self.suffix_time)):
            return 1
        else:
            return 0

    def build_baseFilename(self):
        """
        do builder; in this case,
        old time stamp is removed from filename and
        a new time stamp is append to the filename
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        # remove old suffix
        if self.suffix_time != "":
            index = self.baseFilename.find("."+self.suffix_time)
            if index == -1:
                index = self.baseFilename.rfind(".")
            self.baseFilename = self.baseFilename[:index]

        # add new suffix
        currentTimeTuple = time.localtime()
        self.suffix_time = time.strftime(self.suffix, currentTimeTuple)
        self.baseFilename  = self.baseFilename + "." + self.suffix_time

        self.mode = 'a'
        if not self.delay:
            self.stream = self._open()

logging.config.fileConfig(logini_path)
logger = logging.getLogger('metadataserver')

# taken from https://stackoverflow.com/questions/6234405/logging-uncaught-exceptions-in-python

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    else:
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception
