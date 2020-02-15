import multiprocessing
import time
import os
import logging



class ActivePool(object):
    def __init__(self,mode):
        super(ActivePool, self).__init__()
        self.mgr = multiprocessing.Manager()
        self.active = self.mgr.list()
        self.lock = multiprocessing.Lock()
        self.mode = mode
    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            if self.mode == 1:
                logging.debug('Running: %s', self.active)
    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            if self.mode ==1:
                logging.debug(name + ' Done')
                logging.debug('Running: %s', self.active)
    def __str__(self):
        with self.lock:
            return str(self.active)
