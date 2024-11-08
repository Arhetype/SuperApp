from multiprocessing import Semaphore, Lock

from FileMapping import FileMapping


class SharedMemoryManager:
    def __init__(self, filename, size):
        self.file_mapping = FileMapping(filename, size)
        self.semaphore = Semaphore(1)
        self.lock = Lock()

    def write(self, data, offset=0):
        with self.lock:
            self.semaphore.acquire()
            try:
                self.file_mapping.write(data, offset)
            finally:
                self.semaphore.release()

    def read(self, size, offset=0):
        with self.lock:
            self.semaphore.acquire()
            try:
                return self.file_mapping.read(size, offset)
            finally:
                self.semaphore.release()