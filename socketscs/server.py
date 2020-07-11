import socket
import threading
import pickle
from time import sleep

class Server:
    """This is a simple tcp/ip server class, to be run
    with a paired client

    :param address: IP address of where the server should listen
    :type address: str, optional
    :param port: port for server to listen on
    :type port: int, optional
    """
    def __init__(self,address=socket.gethostname(),port=1234):
        """Constructor method
        """
        self.address=address
        self.port=port
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._running = False
        self._t1=threading.Thread(target = self._listenForConnectionsThread)
        self._t2=threading.Thread(target = self._sendHeartbeatThread,args = ())
        self._t3=threading.Thread(target = self._messageQueuerThread,args = ())
        self._listen=False
        self._heartbeat=True
        self._sendMessages=True
        self._heartbeatMessage=1
        self._messageToSend=""
        self._message=""

    def start(self):
        """Triggers the server to start listening, returns success or failure.
        Starts two new threads, t1 to listen for new connections and t3 to
        queue new messages to be sent

        :rtype: boolean
        """
        try:
            print("Trying to start server")
            self._s.bind((self.address, self.port))
            self._s.listen(5)
            self._running = True
            print("Running")

        except Exception as e:
            print("Server Failed ",e)
            self.stop()
            return False

        self._listen=True
        self._t1.start()
        self._sendMessages=True
        self._t3.start()
        return True

    def _listenForConnectionsThread(self):

        while self._listen:
            try:
                # now our endpoint knows about the OTHER endpoint.
                print("Waiting for connections")
                client, address = self._s.accept()
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
        while self._listen:
            try:
                #data = client.recv(size)
                #if data:
                #    # Set the response to echo back the recieved data
                #    response = data
                #    client.send(response)
                #else:
                #    raise error('Client disconnected')
                if self._messageToSend !="":
                    #print("received a message to send")
                    msg = pickle.dumps(self._messageToSend)
                    msg = bytes(f"{len(msg):<10}", 'utf-8')+msg

                    client.send(msg)
                    #print("server sent ",msg)
                    self._messageToSend=""
            except Exception as e:
                print("ListenToClient error ",e)
                client.close()
                return False
        print("Finished listening to client")
        #client.close()

    def sendHeartbeat(self):
        """triggers the heartbeat to be sent from the server
        """
        self._heartbeat=True
        if (not self._t2.is_alive()):
            print("server: heartbeat not alive, starting")
            self._t2.start()
        else:
            print("heartbeat already Running")

    def _sendHeartbeatThread(self):
        d=1
        while self._heartbeat:
            try:
                self._heartbeatMessage=d
                d=d+1
                if d>1024:
                    d=1
                sleep(0.05)

            except Exception as e:
                print("Server heartbeat error ",e)

    def _messageQueuerThread(self):
        print("_messageQueuerThread starting")
        while self._sendMessages:
            self._messageToSend={'heartbeat':self._heartbeatMessage,'message':self._message}
            sleep(0.1)
        print("_messageQueuerThread exiting")

    def set_message(self,message):
        """Queues a message to be sent to the client from the server

        :param message: the message to be sent by the client
        :type message: str
        """
        if isinstance(message,str):
            self._message=message
        else:
            print ("set_message not string error")

    def stop(self):
        """Stops the server
        """
        self._listen=False
        self._heartbeat=False
        self._sendMessages=False
        try:
            self._s.shutdown(socket.SHUT_RDWR)


        except:
            pass
        self._s.close()
        self._running=False

    def is_alive(self):
        """Returns whether the server is running or not

        :rtype: boolean
        """
        if (self._s.fileno()>0):
            return True
        else:
            return False
