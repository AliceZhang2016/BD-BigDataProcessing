import socket
import select
import commands

class Leader():

	# followerAddr: a list of [HOST, PORT]; lockMap: a dict <str lock_name, int client_id>
	def __init__(self, follower_addr):
		self.follower_addr = follower_addr
		self.broad_dest = ('<broadcast>', 7788) # broad socket fd
		self.lock_map = {}
		self.listenFollower()
		self.dealRequest()

	def listenFollower(self):
		self.sk = [] # all sockets where each corresponds to a follower leader
		for i in range(len(follower_addr)):
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(*follower_addr[i])
			s.listen(1) # backlog(here 1) is the maximum number of queued connections
			self.sk.append(s)
		self.broad_sk = socket.socket(socket.AF_INET, socket.SO_BROADCAST)
		# self.sk.append(broad_sk)

	def dealRequest(self):
		while True:
			r_list, w_list, e_list = select(self.sk, [], [], 1)
			for s in r_list:
				conn, addr = s.accept()
				data = conn.recv(1024) # data is of type "lock_name client_id" (e.g. "lock1, 23")
				request = data.split(' ')
				if len(request) != 2:
					raise ValueError
				lock_name = request[0]
				client_id = int(request[1])

				flag = self.check(lock_name, client_id)
				if flag == 0:
					conn.sendall(bytes("The lock exists but doesn't belongs to the client, please wait and try again."))
				elif flag == 1:
					conn.sendall(bytes("The lock exists and already belongs to the client."))
				elif flag == 2:
					self.updateMap(lock_name, client_id)
					conn.sendall(bytes("The lock has changed and now belongs to the client."))
					self.sendUpdateCommand(data) # send a broadcast to all followers

				conn.close()

	def checkLock(self, lock_name, client_id):
	# return value: 0(lock exist && not belong to this client)
	#               1(lock exist && belong to this client)
	#               2(lock not exist -> lock and update map)
		if lock_name in self.lock_map[ ].keys():
			return self.lock_map[lock_name] == client_id
		else:
			return 2

	def updateMap(self, lock_name, client_id):
		self.lock_map[lock_name] = client_id

	def sendUpdateCommand(self, data):
		self.broad_sk.sendto(bytes(data), self.broad_dest)

