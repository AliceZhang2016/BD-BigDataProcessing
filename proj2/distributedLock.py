import uuid
import time
import socket
import random

class DistributedLock():
    def __init__(self, host, port, serverAddr, serverPort):
        self.host = host
        self.port = port
        self.serverAddr = serverAddr
        self.serverPort = serverPort
        self.clientId = uuid.uuid1()

    def TryLock(self, key, timeout = 10):
        max_size = 1024
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.bind((self.host, self.port))
        flag = 0
        while flag<3:
            flag = flag + 1
            msg = "CHECKSTATUS " + key + " " + str(self.clientId)
            client.sendto(bytes(msg,"utf-8"), (self.serverAddr, self.serverPort))
            print("checkstatus sent")
            while True:
                lock_status, _ = client.recvfrom(max_size)
                if _ == (self.serverAddr, self.serverPort):
                    break
            lock_status = lock_status.decode('utf-8')
            print('lock_status =', lock_status)
            if lock_status == '0':
                msg = "PREEMPT " + key + " " + str(self.clientId)
                client.sendto(bytes(msg,"utf-8"), (self.serverAddr, self.serverPort))
                print("preempt sent")
                while True:
                    get_lock, _ = client.recvfrom(max_size)
                    if _ == (self.serverAddr, self.serverPort):
                        break
                get_lock = get_lock.decode('utf-8')
                print('get_lock =', get_lock)
                if get_lock == '1':
                    print("get the lock")
                    client.close()
                    return 1
            time.sleep(5)
        print("get lock failed")
        client.close()
        return 0


    def TryUnlock(self, key, timeout = 10):
        max_size = 1024
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.bind((self.host, self.port))
        flag = 0
        while flag<3:
            flag = flag + 1
            msg = "CHECKSTATUS " + key + " " + str(self.clientId)
            client.sendto(bytes(msg,"utf-8"), (self.serverAddr, self.serverPort))
            while True:
                lock_status, _ = client.recvfrom(max_size)
                if _ == (self.serverAddr, self.serverPort):
                    break
            lock_status = lock_status.decode('utf-8')
            print("lock_status=", lock_status)
            if lock_status == '1':
                msg = "RELEASE " + key + " " + str(self.clientId)
                client.sendto(bytes(msg,"utf-8"), (self.serverAddr, self.serverPort))
                while True:
                    release_lock, _ = client.recvfrom(max_size)
                    if _ == (self.serverAddr, self.serverPort):
                        break
                release_lock = release_lock.decode('utf-8')
                print('release_lock=', release_lock)
                if release_lock == '1':
                    print("release the lock")
                    client.close()
                    return 1
            time.sleep(5)
        print("release lock failed")
        client.close()
        return 0


    def CheckTheLock(self, key, timeout = 10):
        max_size = 1024
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.bind((self.host, self.port))
        msg = "CHECKSTATUS " + key + " " + str(self.clientId)
        client.sendto(bytes(msg,"utf-8"), (self.serverAddr, self.serverPort))
        while True:
            lock_status, _ = client.recvfrom(max_size)
            if _ == (self.serverAddr, self.serverPort):
                break
        lock_status = lock_status.decode('utf-8')
        return lock_status

    def __del__(self):
        DistributedLock = self.__class__.__name__


if __name__ == '__main__':
    host = '192.168.1.108'
    port = 12306
    serverAddr = '192.168.1.187'
    serverPort = 12306
    distributed_lock = DistributedLock(host, port, serverAddr, serverPort)
    while True:
        print()
        key = 'k' + str(random.randint(1,3))
        print("key =", key)
        instruct = random.randint(0,2)
        if instruct == 0:
            print("instruction: Try Lock")
            distributed_lock.TryLock(key,timeout=10 )
            time.sleep(8)
        elif instruct == 1:
            print("instruction: Try Unlock")
            distributed_lock.TryUnlock(key, timeout=10)
            time.sleep(8)
        else:
            print("instruction: Check Lock")
            lockstatus = distributed_lock.CheckTheLock(key, timeout=10)
            print(lockstatus)
            time.sleep(8)
        print(">>>end")


