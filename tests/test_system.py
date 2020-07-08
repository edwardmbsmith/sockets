import pytest
from time import sleep

from server import Server
from client import Client

def test_message_format_received_by_client():
    server,client=server_client_start()
    server.sendHeartbeat()
    response_hb=0
    response_mess=""
    sleep(1)
    try:
        response_hb = client.read_buffer()['heartbeat']
    except:
        pass
    server.set_message("test")
    sleep(1)
    try:
        response_mess = client.read_buffer()['message']
    except:
        pass
    server_client_stop(server,client)
    assert isinstance(response_hb,int)
    assert isinstance(response_mess,str)
    assert response_hb>0
    assert response_mess=="test"

def test_server_start():
    server = Server('127.0.0.1',1234)
    server.start()
    run=server.running
    server.stop()
    assert run == True


def test_server_accept_connection():
    server,client=server_client_start()
    conn=client.connected
    server_client_stop(server,client)
    assert conn==True




def test_receive_data_on_client():
    server,client=server_client_start()
    sleep(0.2)
    response = client.read_buffer()

    server_client_stop(server,client)
    assert response != ""


def test_heartbeat_sent_by_server_and_received_on_client():
    server,client=server_client_start()
    print("sending heartbeat")
    server.sendHeartbeat()
    print("sent heartbeat")
    sleep(1)
    response1 = client.read_buffer()['heartbeat']
    print(response1)
    sleep (3)
    response2 = client.read_buffer()['heartbeat']
    server_client_stop(server,client)
    assert response2!=response1

def test_heartbeat_every_second_on_client():
    server,client=server_client_start()

    server.sendHeartbeat()
    client.check_heartbeat()
    sleep(5)
    hb=client.check_heartbeat()
    server_client_stop(server,client)
    assert hb == True


def test_heartbeat_every_second_on_client_no_hearbeat():
    server,client=server_client_start()


    client.check_heartbeat()
    sleep(5)
    hb=client.check_heartbeat()
    server_client_stop(server,client)
    assert hb == False





def server_client_start():
    server = Server('127.0.0.1',1234)
    client = Client('127.0.0.1',1234)
    assert server.start() == True
    sleep(0.2)
    assert client.connect() == True
    return server,client

def server_client_stop(server,client):
    sleep(0.2)
    client.stop()
    server.stop()
    sleep(0.2)
