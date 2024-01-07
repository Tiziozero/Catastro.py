class User:
    def __init__(self, a, name="Anonynus"):
        self.a = a
        self.name = name
    def __del__(self):
        print("Closed user")
