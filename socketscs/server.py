import socket
import threading
import pickle
from time import sleep

class Server:

    def __init__(self,address=socket.gethostname(),port=1234):
        self.address=address
        self.port=port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.t1=threading.Thread(target = self._listenForConnectionsThread)
        self.t2=threading.Thread(target = self._sendHeartbeatThread,args = ())
        self.t3=threading.Thread(target = self._messageQueuerThread,args = ())
        self.listen=False
        self.heartbeat=True
        self.sendMessages=True
        self.heartbeatMessage=1
        self.messageToSend=""
        self.message=""

    def start(self):
        try:
            print("Trying to start server")
            self.s.bind((self.address, self.port))
            self.s.listen(5)
            self.running = True
            print("Running")

        except Exception as e:
            print("Server Failed ",e)
            self.stop()
            return False

        self.listen=True
        self.t1.start()
        self.sendMessages=True
        self.t3.start()
        return True

    def _listenForConnectionsThread(self):

        while self.listen:
            try:
                # now our endpoint knows about the OTHER endpoint.
                print("Waiting for connections")
                client, address = self.s.accept()
                print(f"Connection from {address} has been established.")


                msg = pickle.dumps({1:"hi", 2: "there"})
                msg = bytes(f"{len(msg):<10}", 'utf-8')+msg

                client.send(msg)

                threading.Thread(target = self._listenToClientThread,args = (client,address)).start()

                print("listenToClient Thread started")
            except socket.error as e:
                pass
                #print("listenForConnections exception ", str(e))
                #self.stop()
            #print("Heard one connection")
        #print("Finished Listening for connections")


    def _listenToClientThread(self, client, address):
        print("listening to client")
        while self.listen:
            try:
                #data = client.recv(size)
                #if data:
                #    # Set the response to echo back the recieved data
                #    response = data
                #    client.send(response)
                #else:
                #    raise error('Client disconnected')
                if self.messageToSend !="":
                    #print("received a message to send")
                    msg = pickle.dumps(self.messageToSend)
                    msg = bytes(f"{len(msg):<10}", 'utf-8')+msg

                    client.send(msg)
                    #print("server sent ",msg)
                    self.messageToSend=""
            except Exception as e:
                print("ListenToClient error ",e)
                client.close()
                return False
        print("Finished listening to client")
        #client.close()

    def sendHeartbeat(self):
        self.heartbeat=True
        if (not self.t2.is_alive()):
            print("server: heartbeat not alive, starting")
            self.t2.start()
        else:
            print("heartbeat already Running")

    def _sendHeartbeatThread(self):
        d=1
        while self.heartbeat:
            try:
                self.heartbeatMessage=d
                d=d+1
                if d>1024:
                    d=1
                sleep(0.05)

            except Exception as e:
                print("Server heartbeat error ",e)

    def _messageQueuerThread(self):
        print("_messageQueuerThread starting")
        while self.sendMessages:
            self.messageToSend={'heartbeat':self.heartbeatMessage,'message':self.message}
            sleep(0.1)
        print("_messageQueuerThread exiting")

    def set_message(self,message):
        if isinstance(message,str):
            self.message=message
        else:
            print ("set_message not string error")

    def stop(self):
        self.listen=False
        self.heartbeat=False
        self.sendMessages=False
        self.s.shutdown(socket.SHUT_RDWR)

        self.s.close()
        self.running=False

    def is_alive(self):
        if (self.s.fileno()>0):
            return True
        else:
            return False
