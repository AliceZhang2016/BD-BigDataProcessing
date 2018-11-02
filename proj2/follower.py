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
        self.addr_listen_server = ""
        self.port_listen_server = 12303

        self.server_addr = (_serverAddr, 12341)  # send to the port 1234 on server
        self.s_leader = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s_leader.bind((self.addr_listen_server, self.port_listen_server))
        #self.s_leader.close()
        #self.s_leader = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.s_leader.bind((self.addr_listen_server, self.port_listen_server))
        #self.s_leader.settimeout(30)
        #self.s_leader.connect((_serverAddr, 80))
        self.version = 0
        self.lockmap = {"k1":None, "k2":None, "k3":None}

        self.addr_listen_client = ""
        self.port_listen_client = 12305

        # analyze message from server
        # message type identifier: <addr_client + step>
        # msg_head have  value:
        #   - UPDATEMAP + addr_client + step
        #   - PREEMPT + addr_client + step
        #   - RELEASE + addr_client + step

        #self.msg_head = "" # head of msg received from server
        self.timeout_update = 50
        self.success_update = False
        # do not need this variable, 
        # cause the follower should always send update msg 
        # to server to get the newest version
        #self.update_times = 3 

        self.timeout_preept = 50
        self.success_preept = False
        self.preept_status = 0  # preept fail
        self.preept_times = 3 # if timeout, resend for <update_times>-1

        self.timeout_release = 50
        self.success_release = False
        self.release_status = 0 # release fail
        self.release_times = 3
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
        print("Begin to listen from leader server")
        while (1):
            recvData, temp_addr = self.s_leader.recvfrom(1024)
            recvData = recvData.decode('utf-8')
            #print("?????")
            print("data received from server: ", recvData)
            print("ip address of server: ", temp_addr)
            #all_msg = recvData.split(' ')
            #l = len(all_msg)
            #print(l)
            
            action = recvData.split()[0]
            print(action)

            if action == "UPDATEMAP": # daily update or update command from server
                all_msg = recvData.split(' ',2)
                l = len(all_msg)
                if l != 3:
                    print("ERROR: Not matched UPDATEMAP msg from server")
                    exit(1)
                leader_version = all_msg[1]
                details = all_msg[2]
                if int(leader_version) != self.version: # not synchronous
                    self.version = int(leader_version)
                    self.lockmap = eval(details)

                print("===== update from server =====")
                print(self.lockmap)
                print(self.version)
                #print("==============================")
                
            elif action == "PREEMPT":  
                # all_msg: PREEMPT <key_name> <UUID> 1  (success preept)
                # all_msg: PREEMPT <key_name> <UUID> 0  (fail preept)
                all_msg = recvData.split(' ')
                l = len(all_msg)

                if l != 4:
                    print("ERROR: Not matched PREEMPT msg from server")
                    exit(2)
                
                key_name = all_msg[1]
                client_UUID = all_msg[2]
                self.lockmap[key_name] = client_UUID
                self.preept_status = int(all_msg[-1])
                if self.preept_status == 1:
                    self.version += 1
                self.success_preept = True

                print("===== preempt from server =====")
                print(self.lockmap)
                #print("==============================")

            elif action == "RELEASE":
                all_msg = recvData.split(' ')
                l = len(all_msg)
                
                if l != 4:
                    print("ERROR: Not matched RELEASE msg from server")
                    exit(2)
                key_name = all_msg[1]
                client_UUID = all_msg[2]
                self.lockmap[key_name] = None
                self.release_status = int(all_msg[-1])
                if self.preept_status == 1:
                    self.version += 1
                self.success_release = True

                print("===== release from server =====")
                print(self.lockmap)
                #print("==============================")

            else:
                print("===== ACTION ERROR =====")
                print(recvData)
                exit(2)
                #print("==============================")

            time.sleep(1)



    def update_version(self):
        print("Begin the update process")
        while (1): 
            send_msg = "UPDATEMAP " + str(self.version)
            print(self.server_addr)
            sendDataLen = self.s_leader.sendto(bytes(send_msg+'\n',"utf-8"), self.server_addr)
            print(sendDataLen)
            print("send to server: ", send_msg)
            current_time = time.time()
            send_times = 1
            while not self.success_update:
                if current_time-time.time()>self.timeout_update:
                    sendDataLen = self.s_leader.sendto(bytes(send_msg, "utf-8"), self.server_addr)
                    print("send to server: ", send_msg)
                    current_time = time.time()

            # reset value of success_update for the next update session
            success_update = False
            # update the lock map according to the server every 60 seconds
            time.sleep(600) 


    def recv_from_client(self):
        print("Begin to listen from client")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.addr_listen_client, self.port_listen_client))

        while (1):
            data, addr_temp = s.recvfrom(1024)
            data = data.decode('utf-8')
            #addr = ("192.168.1.108", 12306)
            print("data received from client: ", data)
            print("ip address of client: ", addr_temp)

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
            
            print(action)
            if action == "CHECKSTATUS":
                print("a1")
                if self.lockmap[key_name] == UUID: # own the key
                    s.sendto(bytes("1","utf-8"), addr) 
                    print("send to client: ", "1")
                else: # not own the key
                    s.sendto(bytes("0","utf-8"), addr)
                    print("send to client: ", "0")
            
            elif action == "PREEMPT":
                # msg sent to server: PREEMPT key_name UUID
                send_msg = "PREEMPT"+' '+str(key_name) + ' ' + UUID
                self.s_leader.sendto(bytes(send_msg,"utf-8"), self.server_addr)
                print("send to server: ", send_msg)
                current_time = time.time()
                send_times = 1

                # exit the circulation when 1. get response 2.arrive the resend times
                while (not self.success_preept) and send_times<self.preept_times:
                    if current_time-time.time()>self.timeout_preept:
                        sendDataLen = self.s_leader.sendto(bytes(send_msg,"utf-8"), self.server_addr)
                        print("send to server: ", send_msg)
                        send_timems += 1
                        current_time = time.time()

                print("success_preept: ", self.success_preept)
                if self.success_preept: # get msg from server successfully
                    s.sendto(bytes(str(int(self.preept_status)),"utf-8"), addr)
                    print("send to client: ", str(int(self.preept_status)))
                    self.success_preept = False
                else: # not get response msg from server, just timeout and after resending several msgs
                    s.sendto(bytes("0","utf-8"), addr) 
                    print("send to client: ", "0")

            elif action == "RELEASE":
                send_msg = "RELEASE"+' '+str(key_name) + ' ' + UUID
                self.s_leader.sendto(bytes(send_msg,"utf-8"), self.server_addr)
                print("send to server: ", send_msg)
                current_time = time.time()
                send_times = 1

                # exit the circulation when 1. get response 2.arrive the resend times
                while (not self.success_release) and send_times<self.release_times:
                    if current_time-time.time()>self.timeout_release:
                        sendDataLen = self.s_leader.sendto(bytes(send_msg,"utf-8"), self.server_addr)
                        print("send to server: ", send_msg)
                        send_times += 1
                        current_time = time.time()

                print("success_release: ", self.success_release)
                if self.success_release:
                    s.sendto(bytes(str(int(self.release_status)),"utf-8"), addr)
                    print("send to client: ", str(int(self.release_status)))
                    self.success_release = False
                else:
                    print("timeout of RELEASE")
                    s.sendto(bytes("0","utf-8"), addr)
                    print("send to client: ", "0")

            time.sleep(1)


if __name__ == '__main__':
    server_addr = '192.168.1.100'
    follower = Follower(server_addr)

    # define addr and port of client
    # addr could be a scope of ip address
    # wrong two lines
    #addr_client = '192.168.1.255' # could receive all packets sent from this subnet
    #port_client = 12301

    try:
        _thread.start_new_thread(follower.update_version, ())
    except:
        print("Fail of creating thread update")
    try:
        _thread.start_new_thread(follower.recv_from_server, ())
    except:
        print("Fail of creating thread recv_server")
    try:
        _thread.start_new_thread(follower.recv_from_client, ())
    except Exception as e:
        print("Fail of creating thread recv_client")
        #print(Exception)
        print(e)

    while (1):
        pass
