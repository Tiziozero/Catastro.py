class Action:
    ACT_LOG_IN = b'LOG_IN'
    ACT_REGISTER_USER = b'REGISTER_USER'
    ACT_REQUEST_ROOM = b'REQUEST_ROOM'
    ACT_CREATE_ROOM = b'CREATE_ROOM'
    ACT_JOIN_ROOM = b'JOIN_ROOM'
    ACT_BLANK = b''


class Aproval_Messages:
    APROV_APROVED = b'OK'
    APROV_DISAPROVED = b'NO'

class Auth_Enums:
    AUTH_NO_LOGIN_DETAILS = b'NO_LOGIN_DETAILS'
    AUTH_OK = b'OK'
    AUTH_NO_SUCH_USER = b'NO_SUCH_USER'
    AUTH_WRONG_PASSWORD = b'WRONG_PASSWORD'
    AUTH_WRONG_USER_ID = b'WRONG_USER_ID'

class Password:
    PASS_NEEDED = b'PASS_NEEDED'
    PASS_NOT_NEEDED = b'PASS_NOT_NEEDED'
    PASS_GUESSED = b'PASS_GUESSED'
    PASS_NOT_GUESSED = b'PASS_NOT_GUESSED'

class Room_Enum:
    ROOM_FOUND = b'ROOM_FOUND'
    ROOM_NOT_FOUND = b'ROOM_NOT_FOUND'
    REQUEST_ROOM = b'REQUEST_ROOM'
    WRONG_PASSWORD = b'WRONG_PASSWORD'

class Room_Action:
    ROOM_ACT_QUIT = b'ROOM_ACT_QUIT'
