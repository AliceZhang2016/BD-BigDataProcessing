from filetree import FileTree
import numpy as np
import os
import threading
import hashlib

class NameServer:


    def __init__(self, numReplicate=3, idCnt=0):
        self.dataServers = []
        self.fileTree = FileTree()
        self.meta = {}
        self.numReplicate = numReplicate
        self.idCnt= idCnt
        self.cv = threading.Condition()

    def add(self, server):
        self.dataServers.append(server)


    def parse_cmd(self):
        cmd = input("MiniDFS> ")
        parameters = cmd.split(' ')
        return parameters


    def operator(self):
        while True:
            param = self.parse_cmd()
            l = len(param)
            if l == 0:
                print("input a blank line")
                continue

            if param[0] == "quit" or param[0] == "exit":
                print("quit")
                break
            # list all the files in name server.
            elif param[0] == "list":
                if l != 1:
                    print("usage: list (list all the files in name server)")
                else:
                    print("file\tFileID\tChunkNumber")
                    self.fileTree.list_(self.meta)
                continue
            # make new directory
            elif param[0] == "mkdir":
                if l != 1:
                    print("usage: mkdir (make new directory)")
                if self.fileTree.insert_node(param[2], False):
                    print("create directory error \n. maybe the directory : %s exists" % param[2])
                continue
            # list all the files in current folder.
            elif param[0] == "ls":
                if l != 1:
                    print("usage: ls")
                else:
                    self.fileTree.ls_()
                continue
            # enter a folder.
            elif param[0] == "cd":
                if l != 2:
                    print("usage: cd foldername")
                else:
                    self.fileTree.cd_(param[1])
                continue
            # remove a file.
            elif param[0] == "rm":
                if l != 2:
                    print("usage: rm filename")
                else:
                    self.fileTree.rm_(param[1])
                    whole_path = self.fileTree.get_whole_path_(param[1])
                    for i in range(4):
                        self.dataServers[i].cv.acquire()
                        self.dataServers[i].cmd = param[0]
                        self.dataServers[i].fid, self.dataServers[i].bufSize = self.meta[whole_path]
                        self.dataServers[i].finish = False
                        self.dataServers[i].cv.notify_all()
                        self.dataServers[i].cv.release()
                    del self.meta[whole_path]
                continue
            # upload file to miniDFS
            elif param[0] == "put":
                if l != 3:
                    print("usage: put source_file_path des_file_path")
                    continue
                try:
                    f = open(param[1], 'rb')
                except IOError:
                    print("open file error: file %s" % param[1])
                    continue
                if self.fileTree.insert_node(param[2], True):
                    print("create file error \n. maybe the file : %s exists" % param[2])
                    continue
                else:
                    whole_path = self.fileTree.get_whole_path_(param[2])
                    totalSize = os.path.getsize(param[1])
                    f.seek(0, 1) # whence 0: current, 1: head, 2: tail
                    buf = f.read(totalSize)
                    serverSize = np.array([s.size for s in self.dataServers])
                    idx = np.argsort(serverSize)
                    self.idCnt += 1
                    for i in range(self.numReplicate):
                        self.dataServers[idx[i]].cv.acquire()
                        self.meta[whole_path] = (self.idCnt, totalSize)
                        self.dataServers[idx[i]].cmd = "put"
                        self.dataServers[idx[i]].fid = self.idCnt
                        self.dataServers[idx[i]].bufSize = totalSize
                        self.dataServers[idx[i]].buf = buf
                        self.dataServers[idx[i]].finish = False
                        self.dataServers[idx[i]].cv.notify_all()
                        self.dataServers[idx[i]].cv.release()
                f.close()
            # fetch file from miniDFS
            elif param[0] == "read" or param[0] == "fetch":
                if l != 3 and l != 4:
                    print("usage: read source_file_path dest_file_path")
                    print("usage: fetch FileID Offset dest_file_path")
                    continue
                else:
                    if param[0] == "read":
                        whole_path = self.fileTree.get_whole_path_(param[1])
                        if whole_path not in self.meta:
                            print("error: no such file in miniDFS.")
                            continue
                    for i in range(4):
                        self.dataServers[i].cv.acquire()
                        self.dataServers[i].cmd = param[0]
                        if param[0] == "read":
                            self.dataServers[i].fid, self.dataServers[i].bufSize = self.meta[whole_path]
                        else:
                            self.dataServers[i].fid, self.dataServers[i].offset = int(param[1]), int(param[2])
                        self.dataServers[i].finish = False
                        self.dataServers[i].cv.notify_all()
                        self.dataServers[i].cv.release()
            # locate the data server given file ID and Offset.
            elif param == "locate":
                if l != 3:
                    print("usage: locate fileID Offset")
                    continue
                else:
                    for i in range(4):
                        self.dataServers[i].cv.acquire()
                        self.dataServers[i].cmd = "locate"
                        self.dataServers[i].fid = int(param[1])
                        self.dataServers[i].offset = int(param[2])
                        self.dataServers[i].finish = False
                        self.dataServers[i].cv.release()
                        self.dataServers[i].cv.notify_all()
            else:
                print("wrong command.")


            # waiting for the finish of data server.
            for server in self.dataServers:
                server.cv.acquire()
                while not server.finish:
                    server.cv.wait()
                server.cv.notify_all()
                server.cv.release()


            # work after processing of data server
            if param[0] == "read" or param[0] == "fetch":
                md5 = hashlib.md5()
                pre_checksum = ""
                for i in range(4):
                    if self.dataServers[i].bufSize:
                        if param[0] == "read":
                            try:
                                f = open(param[2], 'wb')
                            except IOError:
                                print("create file failed. maybe wrong directory.")
                        elif param[0] == "fetch":
                            try:
                                f = open(param[3], 'wb')
                            except IOError:
                                print("create file failed. maybe wrong directory.")
                        f.write(self.dataServers[i].buf)
                        f.close()
                        md5.update(self.dataServers[i].buf)
                        md5_checksum = md5.digest()
                        if pre_checksum and pre_checksum != md5_checksum:
                            raise ValueError("error: unequal checksum for files from different dataServers. File got may be wrong.")
                        pre_checksum = md5_checksum
                        self.dataServers[i].buf = ""
            elif param[0] == "put":
                print("Upload success. The file ID is %d." % self.idCnt)
            elif param[0] == "locate" or param[0] == "list":
                notFound = True
                for i in range(4):
                    if self.dataServers[i].bufSize:
                        notFound = False
                        print("found FileID %s offset %s at %s." % (param[1], param[2], self.dataServers[i].get_name()))
                if notFound:
                    print("not found FileID %s offset %s." % (param[1], param[2]))

