#!/usr/bin/env python3

import socket, threading, json, sys, datetime, pickle
from comunication_enums import *

class Client:
    def __init__(self, addr, port):
        self.addr, self.port = addr, port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_name = ""
        self.user_id = ""
        self.password = ""
        self.setup()
        try:
            self.s.connect((self.addr, self.port))
        except Exception as e:
            print(f"ERROR in connection to server -> {e}")

    def setup(self):
        with open("user_config.json", 'r') as f:
            data = json.load(f)
            self.user_name = data["user_name"]
            self.user_id = data["user_id"]
            self.password = data["user_password"]



    def register_client(self):
        while True:
            n = self.s.recv(512).decode()
            point(m)
            self.s.send(input("Enter Username: "))
            if self.s.recv(512) == Aproval_Message.APROV_DISAPROVED:
                print(self.s.recv(1024))
            elif self.s.recv(512) == Aproval_Message.APROV_APROVED:
                break
        while True:
            p = self.s.recv(512).decode()
            print(p)
            self.s.send(input("Enter Username: "))
            if self.s.recv(512) == Aproval_Message.APROV_DISAPROVED:
                print(self.s.recv(1024))
            elif self.s.recv(512) == Aproval_Message.APROV_APROVED:
                break




    def client_authentication(self):
        try:
            authentication_data = {"user_name": self.user_name, "user_id": self.user_id, "passeord": self.password}
            self.s.send(json.dumps(authentication_data).encode())
            verdict = self.s.recv(1024)
            print(f"Received authentication verdict {verdict}")
            if verdict != Auth_Enums.AUTH_OK:
                print("ERROR -> Authentication failed:")
                match (verdict):
                    case Auth_Enums.AUTH_WRONG_PASSWORD: print("Wrong Password")
                    case Auth_Enums.AUTH_NO_SUCH_USER: print("No such user")
                return False
            else:
                print("authentication successfull")
                return True
        except Exception as e:
            print(f"ERROR in client authentication -> {e}")
            return False
            
    def run(self):
        self.register_client()
        if self.client_authentication():
            print("Running")
        else:
            print("Failed authentication")

    def __del__(self):
        self.s.close()

if __name__ == '__main__':
    c = Client('localhost', 42069)
    c.run()
