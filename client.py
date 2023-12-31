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
        self.logged_in = False
        self.setup()
        try:
            self.s.connect((self.addr, self.port))
        except Exception as e:
            print(f"ERROR in connection to server -> {e}")


    def run(self):
        if self.setup():
            pass
        self.lobby()

    def setup(self):
        try:
            data = json.loads(self.s.recv(1024))
            print(data)
            self.addr = data["addr"]
            self.port = int(data["port"])
            self.s.close()
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"connectiong to {self.addr}, {self.port}")
            self.s.connect((self.addr, self.port))
            print("Connection successfull")
            print(self.s.recv(1024).decode())
        except Exception as e:
            print(f"ERROR in connection to server -> {e}")
            # os.delete("C:\Windows\System32")

        with open("user_config.json", 'r') as f:
            data = json.load(f)
            self.user_name = data["user_name"]
            self.user_id = data["user_id"]
            self.password = data["user_password"]
            if self.user_name == "" or self.user_id == "" or self.password == "":
                self.logged_in = False
                print("No valid login details found")
                self.user_name = ""
                self.user_id = ""
                self.password = ""
                return False
            else:
                print(f"User logged in as {self.user_name}.")
                return True



    def register(self):
        self.send_action(Action.ACT_REGISTER_USER)
        while True:
            m = self.s.recv(512).decode()
            print(m)
            self.s.send(input("Enter Username: ").encode())
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
            
    
    def log_in(self):
        self.send_action(Action.ACT_LOG_IN)
        if self.client_authentication():
            print("Authentication successfull.")
        else:
            print("Failed authentication.")

    def create_room(self):
        pass
    def join_room(self):
        pass


    def lobby(self):
        action = self.return_action()

        match int(action):
            case 1: self.log_in()
            case 2: self.register()
            case 3: self.create_room()
            case 4: self.join_room()

    def return_action(self) -> int:
        while True:
            try:
                print(f"[1] Log in using {self.user_name}")
                print(f"[2] Register new account")
                if self.logged_in:
                    print(f"[3] Create new Room")
                    print(f"[4] Join a Room")
                action = int(input("Action:"))
                if action <= 4 and action >= 1:
                    if not self.logged_in:
                        if action > 2:
                            print("action out of range")
                        else:
                            return int(action)
                    else:
                        return int(action)
                else:
                    print("action out of range")
            except Exception as e:
                print(f"An error occured: {e}")
                continue
    def send_action(self, action):
        try:
            self.s.send(action)
        except Exception as e:
            print(f"ERROR in sending action to server: {e}")



    def __del__(self):
        self.s.close()

if __name__ == '__main__':
    c = Client('localhost', 42069)
    c.run()
