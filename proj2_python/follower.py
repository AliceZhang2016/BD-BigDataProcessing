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

        self.timeout_preept = 5
        self.success_preept = False
        self.preept_status = 0  # preept fail

        self.timeout_release = 5
        self.success_release = False
        self.release_status = 0 # release fail
        #self.success_map = {} # map received from server

        self.current_addr_client = None
        self.current_action = None
        self.current_key = None
        self.current_step = 0 # depends on current_addr_client, current_action, current_key
        self.current_identifier = None


    def recv_from_server(self):
        while (1):
            recvData, temp_addr = self.s_leader.recvfrom(1024)
            all_msg = recvData.split(recvData)
            l = len(all_msg)
            
            action = all_msg[0]
            addr_client = all_msg[1]
            addr_current_step = all_msg[2]


            if addr_current_step == self.current_step:
                if action == "UPDATEMAP": # daily update or update command from server
                    self.lockmap = eval(action[2])
                    if current_action == 'PREEMPT':
                        self.success_preept = True
                    elif current_action == 'RELEASE':
                        self.success_release = True
                    else:
                        self.success_update = True
                    
                elif action == "PREEMPT":  
                    # all_msg: PREEMPT <addr_client> <addr_current_step> 1  (success preept)
                    # all_msg: PREEMPT <addr_client> <addr_current_step> 0  (fail preept)
                    self.preept_status = int(all_msg[-1])
                    self.success_preept = True

                elif action == "RELEASE":
                    self.release_status = int(all_msg[-1])
                    self.success_release = True

            sleep(1)



    def update_version(self):
        while (1): 
            send_msg = "UPDATEMAP" + str(self.version) + ' ' + str(self.current_identifier)
            sendDataLen = self.s_leader.sendto(send_msg, self.server_addr)
            current_time = time.timer()
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
            # 3.
            all_msgs = data.split()
            action = all_msgs[0]
            key_name = all_msgs[1]

            # update current variables and associated identifier
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


            if action == "CHECKSTATUS":
                if self.lockmap(key_name): # own the key
                    s.sendto("1", addr) 
                else: # not own the key
                    s.sendto("0", addr)
            
            elif action == "PREEMPT":
                send_msg = "PREEMPT"+' '+str(self.key_name) + ' ' + str(self.current_identifier)
                self.s_leader.sendto(send_msg, self.server_addr)
                current_time = time.timer()
                while not self.success_preept:
                    if current_time-time.timer()>timeout_preept:
                        sendDataLen = self.s_leader.sendto(send_msg, self.server_addr)
                        current_time = time.timer()
                self.success_preept = False
                s.sendto(str(preept_status), addr)


            elif action == "RELEASE":
                ssend_msg = "RELEASE"+' '+str(self.key_name) + ' ' + str(self.current_identifier)
                self.s_leader.sendto(send_msg, self.server_addr)
                current_time = time.timer()
                while not self.success_release:
                    if current_time-time.timer()>timeout_release:
                        sendDataLen = self.s_leader.sendto(send_msg, self.server_addr)
                        current_time = time.timer()
                self.success_release = False
                s.sendto(str(release_status), addr)

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
