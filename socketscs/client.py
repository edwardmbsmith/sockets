import socket
import threading
import pickle
from time import sleep

class Client:


    def __init__(self,address=socket.gethostname(),port=1234):
        self.address=address
        self.port=port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected=False
        self.t1=threading.Thread(target = self._waitForDataThread)
        self.t2=threading.Thread(target = self._checkHeartbeatThread)
        self.listen=False
        self.last_message=""
        self.server_healthy=False

    def connect(self):
        try:
            print("Trying to connect client")
            self.s.connect((self.address, self.port))
            self.connected=True
            self.listen=True
            self.t1.start()
        except:
            print("Client connection error")
            return False
        return True

    def _waitForDataThread(self):
        HEADERSIZE = 10
        while self.listen:
            full_msg = b''
            new_msg = True
            while self.listen:
                try:
                    msg = self.s.recv(1024)
                    #print("client msg received:",msg)
                    if new_msg:

                        msglen = int(msg[:HEADERSIZE])
                        new_msg = False

                    #print(f"full message length: {msglen}")

                    full_msg += msg

                    #print(len(full_msg))

                    if len(full_msg)-HEADERSIZE == msglen:
                        #print("full msg recvd")
                        #print(full_msg[HEADERSIZE:])
                        self.last_message=pickle.loads(full_msg[HEADERSIZE:])
                        print(self.last_message)
                        new_msg = True
                        full_msg = b""
                    #else:
                    #    print("client havent received full message yet")
                except Exception as e:
                    print("Client connection closed error ", e)
                    return
        print("client Exiting _waitForDataThread")

    def stop(self):
        self.listen=False
        sleep(1)
        self.s.close()

    def read_buffer(self):
        response=self.last_message
        print("Received Message: ", response)
        return response

    def _checkHeartbeatThread(self):
        previous_heartbeat=1
        current_heartbeat=1
        while self.listen:
            try:
                current_heartbeat=self.last_message['heartbeat']
                if (current_heartbeat!=previous_heartbeat):
                    self.server_healthy=True
                    previous_heartbeat=current_heartbeat
                else:
                    self.server_healthy=False
            except:
                self.server_healthy=False
            print("server health ",self.server_healthy)
            sleep(1)

    def check_heartbeat(self):
        if (not self.t2.is_alive()):
            print("client heartbeat thread not started, starting")
            self.t2.start()
        else:
            print("client thread already started")
        print("heartbeat is ", self.server_healthy)
        return self.server_healthy
