import pytest

import socket
from time import sleep
#from socketscs.server_udp import ServerUDP
#from socketscs.server_udp import datagram
import socketscs as sock
import psutil


#check interface between OBS and DS section 2.2, item no 1
def test_check_server_udp():
    server = sock.ServerUDP('127.0.0.1',"OBS")
    assert server._s.type == socket.SOCK_DGRAM
    server.stop()

#check interface between OBS and DS section 2.2, item no 2
def test_check_client_udp():
    client = sock.ServerUDP('127.0.0.1',"DS")
    assert client._s.type == socket.SOCK_DGRAM
    client.stop()

#generic tests

def test_data_received_by_server():
    server = sock.ServerUDP('127.0.0.1',"OBS")
    client = sock.ServerUDP('127.0.0.1',"DS")
    server.start()
    client.start()
    client.set_message("fafatksruzzdxdcgszhg")
    client.set_message("fafatksruzzdxdcgszhg")
    client.set_message("fafatksruzzdxdcgszhg")
    sleep(2)
    message=server.read_buffer()

    stop_servers((client,server))
    assert message == "fafatksruzzdxdcgszhg"

def test_header_data():
    client,server=start_servers()

    #header=client.prepare_header(command0=0xFF,command1=0xAA,command2=0xFA,command3=0xFF,sd_period=0x02,sd_id=0x32,store_sd_period=0x01,filter_pattern_number=0xff,length=0xFFAA,data_type=0x00,row_on_sdrs=0x32,col_on_sdrs=0x31,size_on_sdrs=0xffab,vehicle_id="abcdefgh",target_id=0x02)
    header=sock.datagram('header',[0xff,0xFF,0xAA,0xFA,0xFF,0x02,0x32,0x01,0xff,0xFFAA,0x00,0x32,0x31,0xffab,"abcdefgh",0x02])
    header=header.to_bytes()
    client.set_message(header)
    client.set_message(header)
    client.set_message(header)
    sleep(2)
    message=server.read_buffer()
    stop_servers((client,server))
    sleep(0.5)
    assert len(message)>0
    assert message[0]==0xFF
    assert message[1]==0xFF
    assert message[2]==0xAA
    assert message[3]==0xFA
    assert message[4]==0xFF
    assert message[5]==0x02
    assert message[6]==0x32
    assert message[7]==0x01
    assert message[8]==0xff
    assert message[9]==0xaa
    assert message[10]==0xff
    assert message[11]==0x00
    assert message[12]==0x32
    assert message[13]==0x31
    assert message[14]==0xab
    assert message[15]==0xff
    assert chr(message[16])=='a'
    assert chr(message[17])=='b'
    assert chr(message[18])=='c'
    assert chr(message[19])=='d'
    assert chr(message[20])=='e'
    assert chr(message[21])=='f'
    assert chr(message[22])=='g'
    assert chr(message[23])=='h'
    assert message[24]==0x02

def test_bad_header_valueerror():
    client,server=start_servers()
    with pytest.raises(ValueError):
        header=sock.datagram('header',[0xfa,0xFF,0xAA,0xFA,0xFF,0x02,0x32,0x01,0xff,0xFFAA,0x00,0x32,0x31,0xffab,"abcdefgh",0x02])

    stop_servers((client,server))

def test_bad_header_typeerror():
    client,server=start_servers()
    with pytest.raises(TypeError):
        header=sock.datagram('header',["a",0xFF,0xAA,0xFA,0xFF,0x02,0x32,0x01,0xff,0xFFAA,0x00,0x32,0x31,0xffab,"abcdefgh",0x02])

    stop_servers((client,server))

def test_bad_datagram_typeerror():
    client,server=start_servers()
    with pytest.raises(TypeError):
        header=sock.datagram('header_notpresent',[0xFF,0xFF,0xAA,0xFA,0xFF,0x02,0x32,0x01,0xff,0xFFAA,0x00,0x32,0x31,0xffab,"abcdefgh",0x02])

    stop_servers((client,server))

def test_cpu_usage_for_client_and_server():
    client,server=start_servers()
    header=sock.datagram('header',[0xff,0xFF,0xAA,0xFA,0xFF,0x02,0x32,0x01,0xff,0xFFAA,0x00,0x32,0x31,0xffab,"abcdefgh",0x02])
    header=header.to_bytes()
    client.set_message(header)
    sleep(1)
    usage=check_cpu_usage()
    message=server.read_buffer()
    stop_servers((client,server))
    sleep(0.5)

    stop_servers((client,server))
    assert usage<20



def start_servers():
    server = sock.ServerUDP('127.0.0.1',"OBS")
    client = sock.ServerUDP('127.0.0.1',"DS")
    server.start()
    client.start()
    return client,server

def stop_servers(servers):
    for server in range(len(servers)):
        servers[server].stop()

def check_cpu_usage():
    current_process=psutil.Process()
    usage=current_process.cpu_percent(1)
    return usage
