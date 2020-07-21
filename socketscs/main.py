#from socketscs.server import Server
#from socketscs.client import Client
from time import sleep
import sys
import threading
import random
import string
import socketscs as sock

def main():
    """This is an example of how to start the server and client, and send
    messages to the client
    """
    try:
        server= sock.ServerUDP('127.0.0.1',"OBS")
        if not server.start():
            return
        sleep(0.2)
        client=sock.ServerUDP('127.0.0.1',"DS")
        if not client.start():
            return
        #client.connect()
        print("server and client started")
        #server.sendHeartbeat()
        #client.check_heartbeat()
        #sleep(1)
        #server.set_message("test2")
        threading.Thread(target = random_message_thread,args = (client,)).start()
        #threading.Thread(target = read_message,args = (server,)).start()

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
        #client.stop()
        server.stop()
    sys.exit(0)


def read_message(server):
    while server.is_alive():
        print("\nmost recent from",server.type,":",server.read_buffer(),"(alive:",server.is_alive(),")")
        sleep(1)

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
    print("sending from",server.type,":",message)
    server.set_message(message)

if __name__ == "__main__":
    main()
