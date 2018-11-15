import numpy as np
import os
import threading
import hashlib

class NameServer:


	def __init__(self, dataServers, fileTree, numReplicate=3, idCnt=0):
		self.dataServers = dataServers
		self.fileTree = fileTree
		self.meta = {}
		self.numReplicate = numReplicate
		self.idCnt= idCnt
		self.cv = threading.Condition()

	def add(self, server):
		self.dataServers.append(server)


	def parse_cmd(self):
		cmd = raw_input("MiniDFS> ")
		parameters = cmd.split(' ')
		return parameters


	def operator(self):
		while True:
			param = self.parse_cmd()
			l = len(param)
			if l == 0:
				print("input a blank line")
				continue

			if param[0] == "quit":
				print("quit")
				break
			# list all the files in name server.
			elif param[0] == "list" or param[0] == "ls":
				if l != 1:
					print("useage: list (list all the files in name server)")
				else:
					print("file\tFileID\tChunkNumber")
					self.fileTree.list(self.meta)
				continue
			# upload file to miniDFS
			elif param[0] == "put":
				if l != 3:
					print("useage: put source_file_path des_file_path")
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
					totalSize = os.path.getsize(param[2])
					f.seek(0, whence=1) # whence 0: current, 1: head, 2: tail
					buf = f.read(totalSize)
					serverSize = np.array([s.size for s in self.dataServers])
					idx = np.argsort(serverSize)
					self.idCnt += 1
					for i in range(numReplicate):
						self.meta[param[2]] = (self.idCnt, totalSize)
						self.dataServers[idx[i]].cmd = "put"
						self.dataServers[idx[i]].fid = idCnt
						self.dataServers[idx[i]].bufSize = totalSize
						self.dataServers[idx[i]].buf = buf
						self.dataServers[idx[i]].finish = False
						self.dataServers[idx[i]].cv.notify_all()
				f.close()
			# fetch file from miniDFS
			elif param[0] == "read" or param[0] == "fetch":
				if l != 3 and l != 4:
					print("useage: read source_file_path dest_file_path")
					print("useage: fetch FileID Offset dest_file_path")
					continue
				else:
					if param[0] == "read" and param[1] not in self.meta:
						print("error: no such file in miniDFS.")
						continue
					for i in range(4):
						self.dataServers.cmd = param[0]
						if param[0] == "read":
							self.dataServers[i].fid, self.dataServers[i].bufSize = meta[param[1]]
						else:
							self.dataServers[i].fid, self.dataServers[i].bufSize = int(param[1]), int(param[2])

						self.dataServers[i].finish = False
						self.dataServers[i].cv.notify_all()
			# locate the data server given file ID and Offset.
			elif param == "locate":
				if l != 3:
					print("useage: locate fileID Offset")
					continue
				else:
					for i in range(4):
						self.dataServers[i].cmd = "locate"
						self.dataServers[i].fid = int(param[1])
						self.dataServers[i].offset = int(param[2])
						self.dataServers[i].finish = False
						self.dataServers.cv.notify_all()
			else:
				print("wrong command.")


			# waiting for the finish of data server.
			for server in self.dataServers:
				while True:
					while not server.finish:
						server.cv.wait()
					server.cv.notify_all()


			# work after processing of data server
			if param[0] == "read" or param == "fetch":
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
							rasie ValueError, "error: unequal checksum for files from different dataServers. File got may be wrong."
						pre_checksum = md5_checksum
						self.dataServers[i].buf = ""
			elif param[0] = "put":
				print("Upload success. The file ID is %d." % self.idCnt)
			elif param[0] == "locate" or param[0] == "ls":
				notFound = True
				for i in range(4):
					if self.dataServers[i].bufSize:
						notFound = False
						print("found FileID %s offset %s at %s." % (param[1], param[2], self.dataServers[i].get_name()))
				if notFound:
					print("not found FileID %s offset %s." % (param[1], param[2]))




















