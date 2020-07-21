import pytest

import socket
from time import sleep
#from socketscs.server_udp import ServerUDP
#from socketscs.server_udp import datagram
import socketscs as sock
import test_udp


def test_multicast():
    server=sock.ServerUDP('192.168.0.39',"OBS")
    assert server._s.type==socket.SOCK_RAW
    server.stop()

def test_tms_server():
    server=sock.ServerUDP('192.168.0.39',"TCMS")
    server.stop()

def tms_on_broadcast_ip():
    server=sock.ServerUDP('192.168.0.255',"TCMS")
    assert self.address=="192.168.0.255"
    server.stop()

def send_broadcast_data_from_tms_to_obs():
    tcms=sock.ServerUDP('239',"TCMS")
    obs=sock.ServerUDP('192.168.0.39',"OBS")
    tcms.set_message("test123")
    sleep(0.5)
    message=obs.read_buffer()
    assert message=="test123"

def check_tms_send_port_for_obs():
    tcms=sock.ServerUDP('192.168.0.39',"TCMS")
    obs=sock.ServerUDP('192.168.0.39',"OBS")
    to="192.168.0.255"
    send_message="test123"
    tcms.set_message(to,send_message)
    sleep(0.5)
    recv_message=obs.read_buffer()
