from serial import Serial
from time import sleep
from threading import Thread
from requests import post, get

class BSerial(Serial):
    """
    This class have some methods to ease the use of pyserial
    Args:
        Serial (of module pyserial): extends from Serial
    """
    def __init__(self,**kargs):
        """
        **kargs: init from Serial, more information in https://pyserial.readthedocs.io/en/latest/pyserial_api.html
        example:
            port: Device name
            baudrate(int): baud rate such as 9600 or 115200 
        """
        super().__init__(**kargs)

        self.separator="-"

    def write_string_port(self,value):
        """
        method to send some value to serial port
        Args:
            value (anytype): this value will convert to string to send it to serial port
        """
        self.write((str(value)+'\n').encode())

    def start_read_string_port(self,command):
        """
        method to start to receive values
        Args:
            command (function): create in this "function" the actions to the value received
        """
        self.start_thread = True
        self.thread = Thread(target=self.__Thread_read_port,args=(command,))
        self.thread.start()

    def stop_read_string_port(self):
        """
        method to stop receiving values
        """
        self.start_thread = False
        self.thread.join()
        del(self.start_thread)
        del(self.thread)

    def __Thread_read_port(self,command):
        """
        private method
        Args:
            command (function): this method read values from serial port
        """
        while self.start_thread:
            if self.in_waiting > 0:
                value = self.readline().decode().replace("\n","")
                print("[READ DATA FROM SERIAL]:", value)
                command(value.split(self.separator))

class Ubidot_Client:

    def __init__(self,token,device):
        """ Constructor for client 
            token([str]): CREDENTIALS UBIDOT
            device([str]): Device Label
        """
        self.token = token
        self.label_device = device
        self.HEADERS = {'X-Auth-Token':token}
        
    def __send_value(self, data):
        
        link = f"https://things.ubidots.com/api/v1.6/devices/{self.label_device}"
        try:

            self.r = post(link,headers=self.HEADERS,json=data)
            print("[SENDED]: Data has been sended")
        except Exception as e:
             print(f"[ERROR]: {str(e)}")

    def send_value(self, thread=False , **data):
        """Send value to Ubidot
        Args:
            thread ([bool]): if  you want to send values in thread
            data ([dict]): data to send,example {label_variable:value,label_variable2:value2,...}
        """
        
        if thread:
            Thread(target=self.__send_value, args=(data,)).start()
        else:
            self.__send_value()

    def send_value_user(self): # you can edit this method, 
        pass

    def __receive_from_value(self, variable_label, command):
        self.receive = True
        while self.receive:
            link = f"https://things.ubidots.com/api/v1.6/devices/{self.label_device}/{variable_label}/lv"
            api = get(url = link, headers = self.HEADERS)
            print(f"[RECEIVED FROM {variable_label}]:", api.text)
            command(api.text)

    def start_receive_from_value(self, variable_label, command):
        """
        this method exexute "command" in thread
        """
        Thread(target=self.__receive_from_value, args=(variable_label, command)).start()
    
    def stop_receive_from_value(self):
        self.receive = False

    def close(self):
        self.r.close()


