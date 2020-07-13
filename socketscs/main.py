#from socketscs.server import Server
#from socketscs.client import Client
from time import sleep
import sys
import threading
import random
import string
from socketscs.client import Client
from socketscs.server import Server

def main():
    """This is an example of how to start the server and client, and send
    messages to the client
    """
    try:
        server= Server('127.0.0.1',1234)
        if not server.start():
            return
        sleep(0.2)
        client=Client('127.0.0.1',1234)
        client.connect()
        print("server and client started")
        server.sendHeartbeat()
        client.check_heartbeat()
        sleep(1)
        #server.set_message("test2")
        threading.Thread(target = random_message_thread,args = (server,)).start()
        #random_message(server)
        input("press any key to exit")
        client.stop()
        server.stop()
    except KeyboardInterrupt:
        print("exiting")
        client.stop()
        server.stop()
    except Exception as e:
        print ("error ",e)
        client.stop()
        server.stop()
    sys.exit(0)




def random_message_thread(server):
    """a thread to send a random message to the client every 0.2s

    :param server: a Server object
    :type server: Server
    """
    print("starting messaging thread")
    while server.is_alive():
        _random_message(server)
        sleep(0.2)
    print("server is dead")

def _random_message(server):
    """command to send random message to client

    :param server:a Server object to issue the message
    :type server: Server
    """
    message=''.join(random.choice(string.ascii_lowercase) for _ in range(20))
    #print("sending ",message)
    server.set_message(message)

if __name__ == "__main__":
    main()
