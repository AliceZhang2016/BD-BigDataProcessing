import socket
import select
# import commands
import time

class Leader():

	# followerAddr: a list of [HOST, PORT]; lockMap: a dict <str lock_name, str client_id>
	def __init__(self, follower_addr):
		self.follower_addr = follower_addr
		self.self_addr = ('', 12341)
		self.broad_dest = ('<broadcast>', 7788) # broad socket fd
		self.lock_map = {"k1":None, "k2":None, "k3":None}
		self.map_ver = 0

	def listenFollower(self):
		# self.sk = [] # all sockets where each corresponds to a follower leader
		# for i in range(len(follower_addr)):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# s.bind(*follower_addr[i])
		self.s.bind(self.self_addr)
		# s.listen(1) # backlog(here 1) is the maximum number of queued connections
		# self.sk.append(s)
		# self.broad_sk = socket.socket(socket.AF_INET, socket.SO_BROADCAST)
		# self.sk.append(broad_sk)

	def dealRequest(self):

		while True:
			# r_list, w_list, e_list = select(self.sk, [], [], 1)
			# for s in r_list:
				# conn, addr = s.accept()
				# data = conn.recv(1024) # data is of type "action lock_name client_id" (e.g. "PREEMPT/RELEASE lock1 23", "UPDATEMAP 2")
			data, address = self.s.recvfrom(1024)
			data = data.decode('utf-8')
			print("data", data)
			print("address", address)
			request = data.split(' ')
			print("request", request)
			if len(request) == 3:
				action = request[0]
				lock_name = request[1]
				client_id = request[2]

				flag = self.checkLock(action, lock_name, client_id)

				# "action lock_name client_id status"
				if flag == 0:
					# The lock exists but doesn't belong to the client, please wait and try again.
					# The lock exists and already belongs to the client.
					print("Failure")
					self.s.sendto(bytes(request[0] + " " + request[1] + " " + request[2] + " 0", 'utf-8'), address)
					print("[send data]", request[0] + " " + request[1] + " " + request[2] + " 0")
					# conn.sendall(bytes(request[0] + " " + request[1] + " " request[2] + " 0"))
				elif flag == 1:
					print("Success")
					self.updateMap(action, lock_name, client_id)
					# "PREEMPT": The lock has changed and now belongs to the client.
					# "RELEASE": The lock has released.
					self.sendUpdateCommand(request) # send a broadcast to all followers
			elif len(request) == 2 and request[0] == "UPDATEMAP":
				request_ver = int(request[1])
				if self.map_ver != request_ver:
					self.s.sendto(bytes(request[0] + " " + str(self.map_ver) + " " + str(self.lock_map), 'utf-8'), address)
					print("[send data]", request[0] + " " + str(self.map_ver) + " " + str(self.lock_map))
					# conn.sendall(bytes(request[0] + " " + str(self.map_ver) + " " + str(self.lock_map)))
				else:
					# Your lock map is already up-to-date.
					self.s.sendto(bytes(request[0] + " " + str(self.map_ver) + " Yes", 'utf-8'), address)
					print("[send data]", request[0] + " " + str(self.map_ver) + " Yes")
					# conn.sendall(bytes(request[0] + " " + str(self.map_ver) + " Yes"))
			else:
				raise ValueError

			time.sleep(5)

			# conn.close()

	def checkLock(self, action, lock_name, client_id):
		if action == "PREEMPT":
			if self.lock_map[lock_name] == None:
				return 1
			else:
				return 0
		elif action == "RELEASE":
			if self.lock_map[lock_name] == client_id:
				return 1
			else:
				return 0

	def updateMap(self, action, lock_name, client_id):
		if action == "PREEMPT":
			self.lock_map[lock_name] = client_id
		elif action == "RELEASE":
			self.lock_map[lock_name] = None
		self.map_ver += 1
		print("[update map] lock_name: ", lock_name, "; value: ", self.lock_map[lock_name])

	def sendUpdateCommand(self, request):
		# self.broad_sk.sendto(bytes(request[0] + " " + request[1] + " " + request[2] + " 1"), self.broad_dest)
		for addr in self.follower_addr:
			self.s.sendto(bytes(request[0] + " " + request[1] + " " + request[2] + " 1", 'utf-8'), addr)
		print("[broadcast data]", request[0] + " " + request[1] + " " + request[2] + " 1")


if __name__ == '__main__':

	follower_addr = [('192.168.1.187', 12303), ('192.168.1.159', 12303)]
	server = Leader(follower_addr)
	server.listenFollower()
	server.dealRequest()




