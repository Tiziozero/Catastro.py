logged_in = False
def return_action(self) -> int:
    while True:
        print("[1] Log in using {self.username}")
        print(f"[2] Register new account")
        if logged_in:
            print(f"[3] Create new Room")
            print(f"[4] Join a Room")
        action = int(input("Action:"))
        if action <= 4 and action >= 1:
            if not logged_in:
                if action > 2:
                    print("action out of range")
                else:
                    return int(action)
            else:
                return int(action)
        else:
            print("action out of range")

print(return_action(None))
