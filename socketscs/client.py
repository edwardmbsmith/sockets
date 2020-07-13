import socket
import threading
import pickle
from time import sleep

class Client:
    """This is a simple TCP/IP client class, to be run with a paired
    server

    :param address: IP address of where the server should listen
    :type address: str, optional
    :param port: port for server to listen on
    :type port: int, optional
    """

    def __init__(self,address=socket.gethostname(),port=1234):
        self.address=address
        self.port=port
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connected=False
        self._t1=threading.Thread(target = self._waitForDataThread)
        self._t2=threading.Thread(target = self._checkHeartbeatThread)
        self._listen=False
        self._last_message=""
        self._server_healthy=False

    def connect(self):
        """starts client connection to server, returns true on success, false
        on failure

        :rtype: boolean
        """
        try:
            print("Trying to connect client")
            self._s.connect((self.address, self.port))
            self._connected=True
            self._listen=True
            self._t1.start()
        except:
            print("Client connection error")
            return False
        return True

    def _waitForDataThread(self):
        HEADERSIZE = 10
        while self._listen:
            full_msg = b''
            new_msg = True
            while self._listen:
                try:
                    msg = self._s.recv(1024)
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
                        self._last_message=pickle.loads(full_msg[HEADERSIZE:])
                        print(self._last_message)
                        new_msg = True
                        full_msg = b""
                    #else:
                    #    print("client havent received full message yet")
                except Exception as e:
                    print("Client connection closed error ", e)
                    return
        print("client Exiting _waitForDataThread")

    def stop(self):
        """Stops the socket listening
        """
        self._listen=False
        sleep(1)
        self._s.close()

    def read_buffer(self):
        """returns the last message read by the client

        :rtype: str
        """
        response=self._last_message
        print("Received Message: ", response)
        return response

    def _checkHeartbeatThread(self):
        previous_heartbeat=1
        current_heartbeat=1
        while self._listen:
            try:
                current_heartbeat=self._last_message['heartbeat']
                if (current_heartbeat!=previous_heartbeat):
                    self._server_healthy=True
                    previous_heartbeat=current_heartbeat
                else:
                    self._server_healthy=False
            except:
                self._server_healthy=False
            print("server health ",self._server_healthy)
            sleep(1)

    def check_heartbeat(self):
        """returns whether the server is healthy or not, by checking that the
        heartbeat value is different to the previous read value (check every second)
        uses an internally accessible thread to check the status

        :rtype: boolean
        """
        if (not self._t2.is_alive()):
            print("client heartbeat thread not started, starting")
            self._t2.start()
        else:
            print("client thread already started")
        print("heartbeat is ", self._server_healthy)
        return self._server_healthy

    def is_connected(self):
        """returns whether the client is connected or not

        :rtype: boolean
        """
        return self._connected
