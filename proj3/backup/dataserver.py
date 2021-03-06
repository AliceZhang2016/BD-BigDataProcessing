import threading
import time
import os
from threading import Thread

chunkSize = 2*1024*1024

class DataServer(Thread):
    def __init__(self, name_):
        Thread.__init__(self)
        
        self.name_ = name_
        # buf is of type "bytes"
        self.buf = ""
        self.finish = True
        self.cv = threading.Condition()

        self.cmd = "mkdir " + self.name
        self.size = 0
        os.system(self.cmd)

        self.fid = None
        self.bufSize = None
        self.offset = None


    def run(self):
        # print("----")
        while True:
            self.cv.acquire()
            if (self.finish):
                self.cv.wait()

            if (self.cmd == "put"):
                self.size += self.bufSize / 1024.0 / 1024.0
                self.put()
            elif (self.cmd == "read"):
                self.read()
            elif (self.cmd == "fetch"):
                self.fetch()
            self.finish = True
            
            #time.sleep(1)
            self.cv.notify_all()
            self.cv.release()
            

    def put(self):
        global chunkSize

        start = 0
        while (start < self.bufSize):
            offset = start / chunkSize
            filePath = self.name_ + "/" + str(self.fid) + " " + str(self.offset)
            if not os.path.exists(filePath):
                print("create file error in dataserver: (file name) "+filePath)
                break
            else:
                f = open(filePath, 'wb')
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
                f = open(filePath, 'rb')
                buf += f.read(min(chunkSize, self.bufSize-start))
                start += chunkSize


    def fetch(self):
        global chunkSize
        filePath = self.name_ + "/" + str(self.fid) + " " + str(self.offset)

        if not os.path.exists(filePath):
            self.buf = ""
            self.bufSize = 0
        else:
            f = open(filePath, 'rb')
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
