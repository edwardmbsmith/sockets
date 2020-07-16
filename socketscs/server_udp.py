import socket
import threading
import pickle
from time import sleep
import pandas as pd
import os

class ServerUDP:
    """This is a simple UDP server class, to be run
    with a paired client. Mimics OBS

    :param address: IP address of where the server should listen
    :type address: str, optional
    :param type: whether the server should act as an OBS or a DS
    :type type: str, optional
    """
    def __init__(self,address=socket.gethostname(),type="OBS"):
        """Constructor method
        """
        self.address=address
        self._listenToPort=1234
        self.type=type
        self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._running = False
        self._t1=threading.Thread(target = self._listenForDataThread)
        self._listen=False
        self._messageToSend=""
        self._message=""
        self._sendToPort=1235

        #port now chosen based on type, OBS or DS
        if type=="OBS":

            self._listenToPort=1234
            self._sendToPort=1235

        elif type=="DS":
            self._listenToPort=1235
            self._sendToPort=1234

        print(type,self._listenToPort,self._sendToPort)

    def start(self):
        """Triggers the server to start listening, returns success or failure.
        Starts two new threads, t1 to listen for new connections and t3 to
        queue new messages to be sent

        :rtype: boolean
        """
        try:
            print("Trying to start server")
            self._s.bind((self.address, self._listenToPort))
            #self._s.listen(5) #not required for UDP
            self._running = True
            print("Running")

        except Exception as e:
            print("Server Failed ",e)
            self.stop()
            return False

        self._listen=True
        self._t1.start() #_listenForDataThread
        return True

    def _listenForDataThread(self):
        print("Server: Ready to receive data")
        while self._listen and self.is_alive():
            try:

                receivedMessage = self._s.recvfrom(32)

                if receivedMessage != "":
                    try:
                        self._message = receivedMessage[0].decode()
                    except:
                        try:
                            self._message=receivedMessage[0]
                            print('decoding hex')
                        except Exception as e:
                            self._error_handling(e,"_listenForDataThread")
                    print(self.type , " received message '",self._message,"'")
                    print("length",len(receivedMessage[0]))

                    ip_addr = receivedMessage[1]
                #print(self._message)
            except socket.error as e:

                self._error_handling(e,"_listenForDataThread")
                self.stop()
            #print("Heard one connection")
        #print("Finished Listening for connections")


    def set_message(self,message):
        """Queues a message to be sent to the client from the server

        :param message: the message to be sent by the client
        :type message: str,bytes
        """
        if isinstance(message,str):
            message=message.encode()
            self._messageToSend=message
        elif isinstance(message,bytes):
            pass

        #    print(self.type, " sending ", message)
        else:
            print ("set_message not string or bytes error type(message):",type(message))
            message=""

        if len(message)>0:
            self._s.sendto(message,(self.address,self._sendToPort))


    def stop(self):
        """Stops the server
        """
        self._listen=False
        self._running=False
        sleep(1)
        try:
            self._s.close()

        except Exception as e:
            self._error_handling(e,"stop")




    def is_alive(self):
        """Returns whether the server is running or not

        :rtype: boolean
        """
        if (self._s.fileno()>0 and self._running):
            return True
        else:
            return False



    def read_buffer(self):
        """Returns the latest message received by the socket

        :rtype: string
        """
        message=self._message
        return message

    def _error_handling(self,e,func):
        """prints a standard error message provided by exceptions

        :param e: the error message
        :type e: string
        :param func: the function raising the error
        :type func: string
        """
        print(self.type, " sufferred exception in " , func , ":" , e)

class datagram:
    """This is a class to hold a datagram message.
    The different datagram structures used in the project are stored
    in a separate csv to allow for simple changes. The structure is as follows:

    type: type of datagram (string)

    No: a sequential number of how many data there are (int)

    Data: where in the array the data will exist (int)

    Description: description of data (string)

    Variable: a proposed variable name for the data	(string)

    Format: bytes, string, etc.

    Bytes: how many bytes the data will take in tha array/list (int)

    Min: min value for data (* for any) (int or hex)

    Max: max value for data (* for any) (int or hex)

    :param input_type: an agreed term for each type of datagram (see data_types.csv)
    :type input_type: string
    :param data_list: a list containing all the data to populate the datagram
    :type data_list: list

    :raises ValidationError: when the specified input_type does not exist in data_types.csv
    :raises AnotherError: a different error
    """
    def __init__(self,input_type,data_list):
        """Constructor method
        """
        path=os.path.dirname(__file__)
        self.data_type=input_type
        self.data_lookup=pd.read_csv(path+"/data/data_types.csv").dropna()


        try:
            self.data_lookup=self.data_lookup[self.data_lookup['type']==self.data_type]
            self.data=[0x00]*int(self.data_lookup['Bytes'].sum())
        except:
            pass

        if(len(self.data_lookup)<1):
            raise TypeError("input_type '",self.data_type,"' not found in data_types.csv")

        #print("preparing data with ",int(self.data_lookup['Bytes'].sum()),len(self.data))
        if self._prepare_and_validate_data(data_list):
            return None
        else:
            raise ValidationError("data not valid to create object")


    def _prepare_and_validate_data(self,data_list):
        """prepares the datagram and validates it against the data_types.csv file

        :param data_list: contains all the data to populate the datagram
        :type data_list: list
        :raises NumItemsError: When the wrong number of items exist in the data_list
        :raises ValueError: When the given data in data_list is out of limits
        :raises TypeError: When the given data in data_list is of the wrong type

        """
        pos=0
        list_pos=0
        format=""
        length=0
        value=""

        #check number of items in data_list is as expected
        if(self.data_lookup.count()['type']!=len(data_list)):
            raise NumItemsError("Wrong number of items for the data type")

        #loop over data from data_types.csv and populate
        for index,row in self.data_lookup.iterrows():
            length=int(row['Bytes'])

            #obtain format type
            if (row['Format']=='byte'):
                format=int
            elif (row['Format']=='string'):
                format=str

            #obtain limits
            try:
                min=int(row['Min'],16)
                max=int(row['Max'],16)
            except:
                min='*'
                max='*'

            #check format type
            if (isinstance(data_list[list_pos],format)):
                #correct format type
                if format==str:
                    value=data_list[list_pos].encode()
                elif format==int:
                    value=data_list[list_pos].to_bytes(length,'little')

                    #check limits if int type
                    if min=='*' or max == '*':
                        pass
                    elif int(data_list[list_pos]) >= min and int(data_list[list_pos]) <= max:
                        pass
                    else:
                        raise ValueError("value",int(value),"is out of range, min:",min,"max:",max)
                else:
                    raise TypeError("Unknown type, can currently only handle string or integer types")
                #populate data
                for n in range(0,length):
                    self.data[pos+n]=value[n]
                pos=pos+length
                list_pos=list_pos+1
            else:
                raise TypeError("expected",format,"got",type(data_list[list_pos]),"at position",list_pos)
        return True

    def to_bytes(self):
        """returns a bytes representation of the datagram, ready to send
        over a socket

        :rtype: bytes
        """
        return bytes(self.data)
