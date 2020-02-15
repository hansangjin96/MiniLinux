import time
import threading
import logging


logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-9s) %(message)s',)

class ThreadPool(object):
    def __init__(self,mode):
        super(ThreadPool, self).__init__()
        self.active = []
        self.lock = threading.Lock()
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
                logging.debug('Running: %s', self.active)
