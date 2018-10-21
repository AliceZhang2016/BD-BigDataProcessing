from socketserver import BaseRequestHandler, UDPServer
import time
import _thread

#current_version = 0

class TimeHandler(BaseRequestHandler):
#    global current_version
    current_version = 0

    def sayhi():
        while (1):
            TimeHandler.current_version+=1
            time.sleep(3)

#    def setup(self):
#        TimeHandler.current_version+=1

    def handle(self):
        print('Got connection from', self.client_address)
        # Get message and client socket
        msg, sock = self.request
        resp = time.ctime()
        sock.sendto((resp+' '+str(TimeHandler.current_version)).encode('ascii'), self.client_address)

if __name__ == '__main__':
    try:
        _thread.start_new_thread(TimeHandler.sayhi, ())
    except:
        print("Fail")


    serv = UDPServer(('', 20000), TimeHandler)
    serv.timeout = 5
    print(serv.timeout)
    serv.serve_forever()