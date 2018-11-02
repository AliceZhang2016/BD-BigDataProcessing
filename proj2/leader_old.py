import socket
import select
import commands

class Leader():

	# followerAddr: a list of [HOST, PORT]; lockMap: a dict <str lock_name, int client_id>
	def __init__(self, follower_addr):
		self.follower_addr = follower_addr
		self.broad_dest = ('<broadcast>', 7788) # broad socket fd
		self.lock_map = {}
		self.map_ver = 0

	def listenFollower(self):
		self.sk = [] # all sockets where each corresponds to a follower leader
		for i in range(len(follower_addr)):
			s = socket.socket(socket.AF_INET, socket.DGRAM)
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
				data = conn.recv(1024) # data is of type "action lock_name client_id" (e.g. "PREEMPT/RELEASE lock1 23", "UPDATEMAP 2")
				request = data.split(' ')
				if len(request) == 3:
					action = request[0]
					lock_name = request[1]
					client_id = int(request[2])

					flag = self.check(lock_name, client_id)
					# "action lock_name client_id status"
					if flag == 0 && flag == 1:
						# The lock exists but doesn't belong to the client, please wait and try again.
						# The lock exists and already belongs to the client.
						conn.sendall(bytes(request[0] + " " + request[1] + " " request[2] + " 0"))
					elif flag == 2:
						self.updateMap(action, lock_name, client_id)
						# "PREEMPT": The lock has changed and now belongs to the client.
						# "RELEASE": The lock has released.
						self.sendUpdateCommand(request) # send a broadcast to all followers
				elif len(request) == 2 && request[0] == "UPDATEMAP":
					request_ver = int(request[1])
					if self.map_ver != request_ver:
						conn.sendall(bytes(request[0] + " " + str(self.map_ver) + " " + str(self.lock_map)))
					else:
						# Your lock map is already up-to-date.
						conn.sendall(bytes(request[0] + " " + str(self.map_ver) + " Yes"))
				else:
					raise ValueError

				conn.close()

	def checkLock(self, lock_name, client_id):
	# return value: 0(lock exist && not belong to this client)
	#               1(lock exist && belong to this client)
	#               2(lock not exist -> lock and update map)
		if lock_name in self.lock_map.keys():
			return self.lock_map[lock_name] == client_id
		else:
			return 2

	def updateMap(self, action, lock_name, client_id):
		if action == "PREEMPT":
			self.lock_map[lock_name] = client_id
		elif action == "RELEASE":
			del self.lock_map[lock_name]
		self.map_ver += 1

	def sendUpdateCommand(self, request):
		self.broad_sk.sendto(bytes(request[0] + " " request[1] + " " request[2] + " 1"), self.broad_dest)


if __name__ == '__main__':

	follower_addr = [[192.168.1.187, 1000]]
	server = Leader(follower_addr)
	server.listenFollower()
	server.dealRequest()




