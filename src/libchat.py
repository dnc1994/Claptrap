import socket
import struct
import logging


REQUEST = 0
RESPONSE = 1
REQUEST_PARAMS = {
    'LOGIN': ['Username', 'Password'],
    'LOGOUT': [],
    'CREATE_ROOM': ['Room-Name'],
    'LIST_ROOMS': [],
    'LIST_MEMBERS': [],
    'JOIN_ROOM': ['Room-Name'],
    'LEAVE_ROOM': ['Room-Name'],
    'SEND_MSG': ['Content-Length', 'Content'],
    'RECV_MSG': []
}
REQUEST_METHODS = REQUEST_PARAMS.keys()
RESPONSE_PARAMS = {
    'RESP_LOGIN': ['Status'],
    'BYEBYE': [],
    'RESP_CREATE_ROOM': ['Status'],
    'RESP_LIST_ROOMS': [],
    'RESP_LIST_MEMBERS': [],
    'RESP_JOIN_ROOM': [],
    'SEE_YOU': [],
    'RESP_SEND_MSG': ['Status'],
    'NO_NEW_MSG': [],
    'NEW_MSG': ['From', 'Time', 'Content-Length', 'Content']
}
RESPONSE_METHODS = RESPONSE_PARAMS.keys()
PARSE_EXCEPTIONS = ['UNSUPPORTED_TYPE', 'BAD_METHOD', 'INCOMPLETE_PARAMS', 'CONTENT_LENGTH_MISMATCH']
CONSTANTS = [(REQUEST_METHODS, REQUEST_PARAMS), (RESPONSE_METHODS, RESPONSE_PARAMS)]


class ProtocolException(Exception):
    pass


logger = logging.getLogger('chat')


# Receive $length bytes data from buffer
def recv_all(sock, length):
    length = int(length)
    data = ''
    received = 0
    while received < length:
        part = sock.recv(length - received)
        if len(part) == 0:
            # packet length not matched
            logger.debug('Socket recv EOF')
            raise socket.error('Socket recv EOF')
        data += part
        received += len(part)
    return data


# Receive a whole packet from buffer
def recv_packet(sock):
    try:
        buff = recv_all(sock, 8)
        try:
            assert buff == 'CLAPTRAP'
        except:
            raise ProtocolException
        buff = recv_all(sock, 4)
        packet_length = struct.unpack('!I', buff)[0]
        packet_data = recv_all(sock, packet_length)
    except socket.error as e:
        raise
    return unpacketify(packet_data)


# Pack data string into packet string
def packetify(data):
    length = len(data) + 12
    protocol = 'CLAPTRAP'
    length = struct.pack('!I', length)
    packet_data = protocol + length + data
    return packet_data


# Unpack packet string into data string
def unpacketify(data):
    return data[12:]


# Parse data string into (methods, params)
def parse(data, type):
    try:
        METHODS, PARAMS = CONSTANTS[type]
    except:
        return 'UNSUPPORTED_TYPE', None

    lines = data.split('\n')
    method = lines[0].strip()
    if method not in METHODS:
        return 'BAD_METHOD', None

    required_params = PARAMS[method]
    params = {}
    content = None

    for (index, line) in enumerate(lines[1:]):
        if line == '\n':
            if 'Content' in required_params:
                content = ''.join(lines[index+1:])
            break
        (k, v) = line.strip().split(': ')
        params[k] = v
    params['Content'] = 'Placeholder'

    if required_params and (not all([params.has_key(rp) for rp in required_params])):
        return 'INCOMPLETE_PARAMS', None

    if 'Content' in required_params:
        if not content or len(content) != params['Content-Length']:
            return 'CONTENT_LENGTH_MISMATCH', None
        else:
            params['Content'] = content
    else:
        del params['Content']

    return method, params
