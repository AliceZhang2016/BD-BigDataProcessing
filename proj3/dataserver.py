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
        self.buf = bytes("",encoding='utf-8')
        self.finish = True
        self.cv = threading.Condition()

        self.cmd = "mkdir -p " + self.name_
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
            print("cmd",self.cmd)
            if (self.cmd == "put"):
                self.size += self.bufSize / 1024.0 / 1024.0
                self.put()
            elif (self.cmd == "read"):
                self.read()
            elif (self.cmd == "fetch"):
                self.fetch()
            elif (self.cmd == "rm"):
                self.rm()
            self.finish = True
            
            #time.sleep(1)
            self.cv.notify_all()
            self.cv.release()
            

    def put(self):
        global chunkSize
        print("enter node", self.name_)
        start = 0
        total = 0
        while (start < self.bufSize):
            total+=1
            offset = int(start / chunkSize)
            filePath = self.name_ + "/" + str(self.fid) + "_" + str(offset)
            if not filePath:
                print("create file error in dataserver: (file name) "+filePath)
                break
            else:
                f = open(filePath, 'wb')
                print(self.name_+" dataserver buf: "+str(total)+' ',self.buf)
                f.write(self.buf[start : min(chunkSize, self.bufSize-start)])
                start += chunkSize
                f.close()
        self.buf = bytes("",encoding='utf-8')


    def read(self):
        global chunkSize

        start = 0

        self.buf = bytes("",encoding='utf-8')
        while (start < self.bufSize):
            self.offset = int(start / chunkSize)
            filePath = self.name_ + "/" + str(self.fid) + "_" + str(self.offset)

            if not os.path.exists(filePath):
                self.buf = bytes("",encoding='utf-8')
                self.bufSize = 0
                break
            else:
                f = open(filePath, 'rb')
                self.buf += f.read(min(chunkSize, self.bufSize-start))
                start += chunkSize
        #print(self.name_ + " buf before: ", self.buf)
        #self.buf = bytes(self.buf, encoding='utf-8')
        #print(self.name_ + " buf after: ",self.buf)


    def fetch(self):
        global chunkSize
        filePath = self.name_ + "/" + str(self.fid) + "_" + str(self.offset)
        #print(filePath)
        self.buf = bytes("",encoding='utf-8')

        if not os.path.exists(filePath):
            print(self.name_ + "not exists")
            self.buf = bytes("",encoding='utf-8')
            self.bufSize = 0
        else:
            #print(self.name_ + "exits")
            f = open(filePath, 'rb')
            print("filepath", filePath)
            self.buf = f.read(min(chunkSize, self.bufSize - chunkSize*self.offset))
            print("dataserver fetch", self.buf, self.bufSize, self.offset)
            self.bufSize = f.tell()
        #self.buf = bytes(self.buf, encoding='utf-8')


    def locate(self):
        filePath = self.name_ + "/" + str(self.fid) + "_" + str(self.offset)
        if not os.path.exists(filePath):
            self.bufSize = 1
        else:
            self.bufSize = 0


    def rm(self):
        global chunkSize
        start = 0
        self.buf = bytes("",encoding='utf-8')
        while (start < self.bufSize):
            self.offset = int(start / chunkSize)
            filePath = self.name_ + "/" + str(self.fid) + "_" + str(self.offset)
            #print(filePath)
            if not os.path.exists(filePath):
                #print("NOT EXIST: "+filePath)
                break
            else:
                #print(filePath)
                self.cmd = "rm " + filePath
                os.system(self.cmd)



    def get_name(self):
        return self.name_
