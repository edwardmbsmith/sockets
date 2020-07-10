from server import Server
from client import Client
from time import sleep
import sys
import threading
import random
import string


def main():
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
        random_message(server)
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
    print("starting messaging thread")
    while server.is_alive():
        random_message(server)
        sleep(0.2)
    print("server is dead")

def random_message(server):
    message=''.join(random.choice(string.ascii_lowercase) for _ in range(20))
    #print("sending ",message)
    server.set_message(message)

if __name__ == "__main__":
    main()
