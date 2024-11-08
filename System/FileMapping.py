import mmap

class FileMapping:
    def __init__(self, filename, size):
        self.filename = filename
        self.size = size
        self.create_file()

    def create_file(self):
        with open(self.filename, 'wb') as f:
            f.write(b'\x00' * self.size)

    def get_mmap(self):
        file = open(self.filename, 'r+b')
        return mmap.mmap(file.fileno(), self.size)

    def write(self, data, offset=0):
        with self.get_mmap() as m:
            m.seek(offset)
            m.write(data)

    def read(self, size, offset=0):
        with self.get_mmap() as m:
            m.seek(offset)
            return m.read(size)
