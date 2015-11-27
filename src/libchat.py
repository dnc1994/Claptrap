# -*- encoding:utf-8 -*-
import socket
import struct
from commons import *


# Receive $length bytes data from buffer
def recv_all(sock, length):
    length = int(length)
    print 'recv_all: expecting length = {0}'.format(length)
    data = ''
    received = 0
    while received < length:
        part = sock.recv(length - received)
        if len(part) == 0:
            # packet length not matched
            raise socket.error('Socket recv EOF')
        data += part
        received += len(part)
        print 'recv_all: part = {0}'.format(part.replace('\n', '#'))
        print 'recv_all: received = {0}'.format(received)
    return data


# Receive a whole packet from buffer
def recv_packet(sock):
    try:
        buff = recv_all(sock, 8)
        try:
            assert buff == 'CLAPTRAP'
        except:
            raise BadProtocolException
        buff = recv_all(sock, 4)
        packet_length = struct.unpack('!I', buff)[0] - 12
        packet_data = recv_all(sock, packet_length)
    except socket.error as e:
        raise
    return packet_data


# Pack data string into packet string
def packetify(data):
    # print 'packetifying data'
    # print data
    length = len(data) + 12
    protocol = 'CLAPTRAP'
    length = struct.pack('!I', length)
    packet_data = protocol + length + data
    # print packet_data
    return packet_data


# Parse data string into (methods, params)
def parse(data, type):
    'parsing data: {0}'.format(data.replace('\n', '#'))
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
        if line == '':
            if 'Content' in required_params:
                # remember content was splitted by \n
                # and remember we start enumerating from 1
                content = '\n'.join(lines[index+2:])
                # print 'content after re-joining >>'
                # print content.replace('\n', '#')
            break
        # print 'split line: {0}'.format(line.strip().split(': '))
        (k, v) = line.strip().split(': ')
        params[k] = v
    params['Content'] = 'Placeholder'

    # print 'checking params'
    # print 'required params >>'
    # print required_params
    # print 'received params >>'
    # print params.keys()
    if required_params and (not all([params.has_key(rp) for rp in required_params])):
        return 'INCOMPLETE_PARAMS', None

    if 'Content' in required_params:
        if not content or (len(content) != int(params['Content-Length'])):
            # print 'content length mismatch'
            # print 'content >>'
            # print content.replace('\n', '#')
            # print len(content), '<->', params['Content-Length']
            return 'CONTENT_LENGTH_MISMATCH', None
        else:
            params['Content'] = content
    else:
        del params['Content']

    return method, params
