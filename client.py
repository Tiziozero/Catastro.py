#!/usr/bin/env python3

import socket, threading, json, sys, datetime, pickle
from comunication_enums import *

class Client:
    def __init__(self, addr, port):
        try:
            self.addr, self.port = addr, port
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.addr, self.port))
        except Exception as e:
            print(f"ERROR in setting up connection with server -> {e}")

    def run(self):
        print(self.server.recv(1024).decode())
    
    def __del__(self):
        self.server.close()
        print("Closed connection to server")

if __name__ == '__main__':
    c = Client('localhost', 42069)
    c.run()
