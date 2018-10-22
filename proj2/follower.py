import _thread
import threading
import time
import random
import socket
import math

class Follower():
    # initialization of a follower server
    # connect to the lead server
    def __init__(self, _serverAddr):
        self.server_addr = (_serverAddr, 12300)
        self.s_leader = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s_leader.settimeout(3)
        #self.s_leader.connect((_serverAddr, 80))
        self.version = 0
        self.lockmap = {}

        # analyze message from server
        # message type identifier: <addr_client + step>
        # msg_head have  value:
        #   - UPDATEMAP + addr_client + step
        #   - PREEMPT + addr_client + step
        #   - RELEASE + addr_client + step

        #self.msg_head = "" # head of msg received from server
        self.timeout_update = 5
        self.success_update = False
        # do not need this variable, 
        # cause the follower should always send update msg 
        # to server to get the newest version
        #self.update_times = 3 

        self.timeout_preept = 5
        self.success_preept = False
        self.preept_status = 0  # preept fail
        self.preept_times = 3 # if timeout, resend for <update_times>-1

        self.timeout_release = 5
        self.success_release = False
        self.release_status = 0 # release fail
        self.release_times = 0
        #self.success_map = {} # map received from server

        '''
        self.current_addr_client = None
        self.UUID = None
        self.current_action = None
        self.current_key = None
        #self.current_step = 0 # depends on current_addr_client, current_action, current_key
        self.current_identifier = None
        '''


    def recv_from_server(self):
        while (1):
            recvData, temp_addr = self.s_leader.recvfrom(1024)
            all_msg = recvData.split(recvData)
            l = len(all_msg)
            
            action = all_msg[0]

            if action == "UPDATEMAP": # daily update or update command from server
                if l != 3:
                    print("ERROR: Not matched UPDATEMAP msg from server")
                    exit(1)
                leader_version = all_msg[1]
                details = all_msg[2]
                if int(leader_version) != self.version: # not synchronous
                    self.version = int(leader_version)
                    self.lockmap = eval(details)
                
            elif action == "PREEMPT":  
                # all_msg: PREEMPT <key_name> <UUID> 1  (success preept)
                # all_msg: PREEMPT <key_name> <UUID> 0  (fail preept)
                if l != 4:
                    print("ERROR: Not matched PREEMPT msg from server")
                    exit(2)
                key_name = all_msg[1]
                client_UUID = all_msg[2]
                self.lockmap[key_name] = client_UUID
                self.preept_status = int(all_msg[-1])
                if self.preept_status == 1:
                    version += 1
                self.success_preept = True

            elif action == "RELEASE":
                if l != 4:
                    print("ERROR: Not matched RELEASE msg from server")
                    exit(2)
                key_name = all_msg[1]
                client_UUID = all_msg[2]
                self.lockmap[key_name] = None
                self.release_status = int(all_msg[-1])
                if self.preept_status == 1:
                    version += 1
                self.success_release = True

            sleep(1)



    def update_version(self):
        while (1): 
            send_msg = "UPDATEMAP" + str(self.version)
            sendDataLen = self.s_leader.sendto(send_msg, self.server_addr)
            current_time = time.timer()
            send_times = 1
            while not self.success_update:
                if current_time-time.timer()>self.timeout_update:
                    sendDataLen = self.s_leader.sendto(send_msg, self.server_addr)
                    current_time = time.timer()

            # reset value of success_update for the next update session
            success_update = False
            # update the lock map according to the server every 60 seconds
            time.sleep(60) 


    def recv_from_client(self, addr_client, port_client):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((addr_client, port_client))

        while (1):
            data, addr = s.recvfrom(1024)
            print("data received from client: ", data)
            print("ip address of client: ", addr)

            # several parts in <all_msgs>:
            # 1. action: PREEMPT, RELEASE, CHECKSTATUS
            # 2. key_name
            # 3. UUID
            all_msgs = data.split()
            action = all_msgs[0]
            key_name = all_msgs[1]
            UUID = all_msgs[2]

            # update current variables and associated identifier
            '''
            if (self.identifier == str(action)+ ' ' + str(addr) + ' ' + str(key_name)):
                hi = 0
                # do nothing
                # request is the same as the previous one received from client
            else:
                self.current_step += 1
                self.current_addr_client == addr
                self.current_action = action
                self.current_key = key_name
                self.identifier = str(action)+ ' ' + str(addr) + ' ' + str(key_name)
            '''

            if action == "CHECKSTATUS":
                if self.lockmap(key_name) == UUID: # own the key
                    s.sendto("1", addr) 
                else: # not own the key
                    s.sendto("0", addr)
            
            elif action == "PREEMPT":
                # msg sent to server: PREEMPT key_name UUID
                send_msg = "PREEMPT"+' '+str(key_name) + ' ' + UUID
                self.s_leader.sendto(send_msg, self.server_addr)
                current_time = time.timer()
                send_times = 1

                # exit the circulation when 1. get response 2.arrive the resend times
                while (not self.success_preept) or send_times<self.preept_times:
                    if current_time-time.timer()>timeout_preept:
                        sendDataLen = self.s_leader.sendto(send_msg, self.server_addr)
                        send_timems += 1
                        current_time = time.timer()

                if self.success_preept: # get msg from server successfully
                    self.success_preept = False
                    s.sendto(str(preept_status), addr)
                else: # not get response msg from server, just timeout and after resending several msgs
                    s.sendto("0", addr) 

            elif action == "RELEASE":
                ssend_msg = "RELEASE"+' '+str(self.key_name) + ' ' + str(self.current_identifier)
                self.s_leader.sendto(send_msg, self.server_addr)
                current_time = time.timer()
                send_times = 1

                # exit the circulation when 1. get response 2.arrive the resend times
                while not self.success_release or send_times<self.release_times:
                    if current_time-time.timer()>timeout_release:
                        sendDataLen = self.s_leader.sendto(send_msg, self.server_addr)
                        send_times += 1
                        current_time = time.timer()

                if self.success_release:
                    self.success_release = False
                    s.sendto(str(release_status), addr)
                else:
                    s.sendto("0", addr)

            time.sleep(1)


if __name__ == '__main__':
    server_addr = '192.168.1.195'
    follower = Follower(server_addr)

    # define addr and port of client
    # addr could be a scope of ip address
    addr_client = '192.168.1.255' # could receive all packets sent from this subnet
    port_client = 12301

    try:
        _thread.start_new_thread(follower.update_version, ())
        _thread.start_new_thread(follower.recv_from_server, ())
        _thread.start_new_thread(follower.recv_from_client, (addr_client, port_client,))
    except:
        print("Fail of creating thread")

    while (1):
        pass
