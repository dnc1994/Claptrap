# -*- encoding:utf-8 -*-
import socket
import libchat
from commons import *

HOST = '127.0.0.1'
PORT = '6666'


class ChatClient(object):
    def __init__(self, host=HOST, port=PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = str(host)
        port = int(port)
        print 'connecting to {0}:{1}'.format(host, port)
        self.sock.connect((host, port))
        self.logined = False
        self.username = ''
        self.current_room = ''

    def send_req(self, method, params=None, content=None):
        print 'prepare to send request {0}'.format(method)
        if 'Content' in REQUEST_PARAMS[method]:
            try:
                assert params
            except:
                params = {}
            assert content
            params['Content-Length'] = len(content)

        req = [method]
        req += ['{0}: {1}'.format(k, v) for (k, v) in params.iteritems()] if params else []
        req += ['\n{0}'.format(content)] if content else []
        req = '\n'.join(req)
        print 'req >>'
        print req
        try:
            self.sock.sendall(libchat.packetify(req))
        except socket.error as e:
            raise
        resp = libchat.recv_packet(self.sock)
        return libchat.parse(resp, libchat.RESPONSE)

    # all methods below must encoding string in utf-8 before transmission
    def encode_string(self, string):
        try:
            return string.encode('utf-8')
        except:
            return string

    def decode_string(self, string):
        try:
            return string.decode('utf-8')
        except:
            return string

    def login(self, username, password):
        username = self.encode_string(username)
        method, params = self.send_req(method='LOGIN', params={'Username': username, 'Password': password})
        print 'response:', method, params
        try:
            assert method == 'RESP_LOGIN'
        except:
            return
        if params['Status'] == 'OK':
            self.logined = True
            return True
        elif params['Status'] == 'AUTH_FAILED':
            return False
        else:
            raise BadStatusException

    def logout(self):
        method, params = self.send_req(method='LOGOUT')
        try:
            assert method == 'RESP_LOGOUT'
        except:
            return
        if params['Status'] == 'OK':
            return True
        elif params['Status'] == 'NOT_LOGIN':
            return False
        else:
            raise BadStatusException

    # def create_room(self, room_name):
    #     room_name = self.encode_string(room_name)
    #     method, params = self.send_req(method='CREATE_ROOM', params={'Room-Name': room_name})
    #     try:
    #         assert method == 'RESP_CREATE_ROOM'
    #     except:
    #         return
    #     if params['Status'] == 'OK':
    #         return True
    #     elif params['Status'] in ['NOT_IN_ROOM', 'NOT_LOGIN']:
    #         return False
    #     else:
    #         raise BadStatusException

    def list_rooms(self):
        method, params = self.send_req(method='LIST_ROOMS')
        # print 'client -> list_rooms -> resp >>'
        try:
            assert method == 'RESP_LIST_ROOMS'
        except:
            return
        if params['Status'] == 'OK':
            room_list = map(self.decode_string, params['Content'].split('\n'))
            return room_list
        elif params['Status'] == 'NOT_LOGIN':
            return None
        else:
            raise BadStatusException

    def list_members(self):
        method, params = self.send_req(method='LIST_MEMBERS')
        try:
            assert method == 'RESP_LIST_MEMBERS'
        except:
            return
        if params['Status'] == 'OK':
            member_list = map(self.decode_string, params['Content'].split('\n'))
            return member_list
        elif params['Status'] in ['NOT_IN_ROOM', 'NOT_LOGIN']:
            return None
        else:
            raise BadStatusException

    def join_room(self, room_name):
        room_name = self.encode_string(room_name)
        method, params = self.send_req(method='JOIN_ROOM', params={'Room-Name': room_name})
        try:
            assert method == 'RESP_JOIN_ROOM'
        except:
            return
        if params['Status'] == 'OK':
            self.current_room = room_name
            return True
        elif params['Status'] in ['NO_SUCH_ROOM', 'NOT_LOGIN']:
            return False
        else:
            raise BadStatusException

    def exit_room(self):
        method, params = self.send_req(method='EXIT_ROOM')
        try:
            assert method == 'RESP_EXIT_ROOM'
        except:
            return
        if params['Status'] == 'OK':
            return True
        elif params['Status'] in ['NOT_IN_ROOM', 'NOT_LOGIN']:
            return False
        else:
            raise BadStatusException

    def send_msg(self, message):
        message = self.encode_string(message)
        # escape \t because later will use \t to split message attributes
        message = message.replace('\t', '    ')
        method, params = self.send_req(method='SEND_MSG', content=message)
        try:
            assert method == 'RESP_SEND_MSG'
        except:
            return
        if params['Status'] == 'OK':
            return True
        elif params['Status'] in ['NOT_IN_ROOM', 'NOT_LOGIN']:
            return False
        else:
            raise BadStatusException

    def recv_msg(self):
        method, params = self.send_req(method='RECV_MSG')
        try:
            assert method in ['NO_NEW_MSG', 'NEW_MSG']
        except:
            return
        if method == 'NO_NEW_MSG':
            if params['Status'] in ['NOT_IN_ROOM', 'NO_NEW_MSG', 'NOT_LOGIN']:
                return None
            else:
                raise BadStatusException
        elif method == 'NEW_MSG':
            if params['Status'] == 'OK':
                messages = map(self.decode_string, params['Content'].split('\t\t'))
                return messages
            else:
                raise BadStatusException


# obsolete
def test():
    client = ChatClient()

    print 'test login'
    client.login('xiaoming', '123')
    print '======================='

    print 'test list_rooms'
    room_list = client.list_rooms()
    print '======================='

    print 'test join_room'
    room = room_list[0].split('\t')[0]
    client.join_room(room)
    print '======================='

    print 'test exit_room'
    client.exit_room()
    print '======================='

    # print 'test join wrong room'
    # client.join_room('excited')
    # print '======================='

    # print 'test double exit_room'
    # client.exit_room()
    # print '======================='

    # print 'test create_room'
    # client.create_room('excited')
    # print client.list_rooms()
    # print '======================='

    print 'test list_member'
    client.join_room('test1')
    member_list = client.list_members()
    print member_list
    print '======================='

    # print 'test double creatie_room'
    # client.create_room('excited')
    # print '======================='

    print 'test send messages'
    client.send_msg('Hello world!')
    print '======================='

    print 'test receiving messages'
    msg_list = client.recv_msg()
    print msg_list
    print '======================='


if __name__ == '__main__':
    test()