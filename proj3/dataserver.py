import threading
import time
import os

chunkSize = 2*1024*1024

class DataServer():
    def __init__(self, name_):
        self.name_ = name_
        # buf is of type "bytes"
        self.buf = ""
        self.finish = True
        self.cv = threading.Condition()

        self.cmd = "mkdir -p" + self.name
        self.size_ = 0
        os.system(cmd)

        self.fid = None
        self.bufSize = None
        self.offset = None


    def operator(self):
        while True:
            while (not self.finish):
                self.cv.wait()
            if (self.cmd == "put"):
                self.size_ += bufSize / 1024.0 / 1024.0
                put()
            elif (self.cmd == "read"):
                read()
            elif (self.cmd == "fetch"):
                fetch()
            self.finish = True
            cv.notify_all()


    def put(self):
        global chunkSize

        start = 0
        while (start < bufSize):
            offset = start / chunkSize
            filePath = self.name_ + "/" + str(self.fid) + " " + str(self.offset)
            if not os.path.exists(filePath):
                print("create file error in dataserver: (file name) "+filePath)
                break
            else:
                f = open(filePath, 'w')
                f.write(buf[start : min(chunkSize, self.bufSize-start)])
                start += chunkSize
                f.close()


    def read(self):
        global chunkSize
        self.bufSize = []

        start = 0

        buf = ""
        while (start < self.bufSize):
            offset = start / chunkSize
            filePath = self.name_ + "/" + str(self.fid) + " " + str(self.offset)

            if not os.path.exists(filePath):
                self.buf = ""
                self.bufSize = 0
                break
            else:
                f = open(filePath, 'r')
                buf += f.read(min(chunkSize, self.bufSize-start))
                start += chunkSize


    def fetch(self):
        global chunkSize
        filePath = self.name_ + "/" + str(self.fid) + " " + str(self.offset)

        if not os.path.exists(filePath):
            self.buf = ""
            self.bufSize = 0
        else:
            f = open(filePath, 'r')
            buf += f.read(min(chunkSize, self.bufSize - chunkSize*self.offset))
            self.bufSize = f.tell()


    def locate(self):
        filePath = selfname_ + "/" + str(self.fid) + " " + str(self.offset)
        if not os.path.exists(filePath):
            self.bufSize = 1
        else:
            self.bufSize = 0


    def get_name(self):
        return self.name_
