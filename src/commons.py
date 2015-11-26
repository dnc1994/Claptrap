# -*- encoding:utf-8 -*-
REQUEST = 0
RESPONSE = 1
REQUEST_PARAMS = {
    'LOGIN': ['Username', 'Password'],
    'LOGOUT': [],
    'CREATE_ROOM': ['Room-Name'],
    'LIST_ROOMS': [],
    'LIST_MEMBERS': [],
    'JOIN_ROOM': ['Room-Name'],
    'EXIT_ROOM': [],
    'SEND_MSG': ['Content', 'Content-Length'],
    'RECV_MSG': []
}
REQUEST_METHODS = REQUEST_PARAMS.keys()
RESPONSE_PARAMS = {
    'RESP_LOGIN': ['Status'],
    'RESP_LOGOUT': ['Status'],
    'RESP_CREATE_ROOM': ['Status'],
    'RESP_LIST_ROOMS': ['Status', 'Content', 'Content-Length'],
    'RESP_LIST_MEMBERS': ['Status', 'Content', 'Content-Length'],
    'RESP_JOIN_ROOM': ['Status'],
    'RESP_EXIT_ROOM': ['Status'],
    'RESP_SEND_MSG': ['Status'],
    'NO_NEW_MSG': ['Status'],
    'NEW_MSG': ['Status', 'Content', 'Content-Length']
}
RESPONSE_METHODS = RESPONSE_PARAMS.keys()
PARSE_EXCEPTIONS = ['UNSUPPORTED_TYPE', 'BAD_METHOD', 'INCOMPLETE_PARAMS', 'CONTENT_LENGTH_MISMATCH']
CONSTANTS = [(REQUEST_METHODS, REQUEST_PARAMS), (RESPONSE_METHODS, RESPONSE_PARAMS)]


class BadProtocolException(Exception):
    pass

class BadMethodException(Exception):
    pass

class BadStatusException(Exception):
    pass