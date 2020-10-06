# -*- coding: utf-8 -*-

import serial
import time

class nucleo:
    def __init__(self, **parameters):
        self.load_key_cmd = b'C 0\r'
        self.load_plaintext_cmd = b'C 1\r'
        self.start_AES = b'C 2\r'
        self.read_cmd=b'R 0\r'
        self.ser = serial.Serial()
        #debug parameter
        self.print_mode = parameters['debug']
        
    def connect(self, **parameters):
        self.ser.baudrate = parameters['baudrate']
        self.ser.port = parameters['com port']
        self.ser.parity = parameters['parity']
        self.ser.bytesize = parameters['bytesize']
        self.ser.stopbits = parameters['stopbits']
        if self.ser.is_open:
            self.ser.close()
        self.ser.open()
        
    def disconnect(self):
        self.ser.close()
        
    def read(self):
        c=1
        while c:
            data = self.ser.readline()
            self.ser.read()
            if self.print_mode:
                print(data[0:len(data)-1])
            if self.ser.in_waiting==0:
                c=0
    
    def load_key(self, s):
        self.ser.write(self.load_key_cmd)
        self.clean_buffer()
        time.sleep(0.1)
        self.ser.write(s)
        self.clean_buffer()
        time.sleep(0.1)
        
    def load_plaintext(self, s):
        self.ser.write(self.load_plaintext_cmd)
        self.clean_buffer()
        time.sleep(0.1)
        self.ser.write(s)
        self.clean_buffer()
        time.sleep(0.1)
        
    def start_aes(self):
        self.ser.write(self.start_AES)
        time.sleep(0.1)
        self.clean_buffer()
        time.sleep(0.1)
        
    def read_cipher(self):
        self.ser.write(self.read_cmd)
        self.read()
        
    def clean_buffer(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()