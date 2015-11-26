# -*- encoding:utf-8 -*-
import socket
import libchat
from commons import *


HOST = '127.0.0.1'
PORT = 6666
BUF_SIZE = 1024

class ChatClient(object):
    def __init__(self, host=HOST, port=PORT, gui=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.logined = False
        self.current_room = ''
        self.handlers = {
            'LOGIN': self.login,
            'LOGOUT': self.logout,
            'CREATE_ROOM': self.create_room,
            'LIST_ROOMS': self.list_rooms,
            'LIST_MEMBERS': self.list_members,
            'JOIN_ROOM': self.join_room,
            'EXIT_ROOM': self.exit_room,
            'SEND_MSG': self.send_msg,
            'RECV_MSG': self.recv_msg
        }
        if gui:
            self.loop()

    def send_req(self, method, params=None, content=None):
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
        print 'login: ' + username + ': ' + password
        method, params = self.send_req(method='LOGIN', params={'Username': username, 'Password': password})
        print 'response:', method, params
        assert method == 'RESP_LOGIN'
        if params['Status'] == 'OK':
            self.logined = True
            return True
        elif params['Status'] == 'AUTH_FAILED':
            return False
        else:
            raise BadStatusException

    def logout(self):
        method, params = self.send_req(method='LOGOUT')
        assert method == 'RESP_LOGOUT'
        assert params['Status'] == 'OK'

    def create_room(self, room_name):
        room_name = self.encode_string(room_name)
        method, params = self.send_req(method='CREATE_ROOM', params={'Room-Name': room_name})
        assert method == 'RESP_CREATE_ROOM'
        assert params['Status'] == 'OK'

    def list_rooms(self):
        method, params = self.send_req(method='LIST_ROOMS')
        print 'client -> list_rooms -> resp >>'
        print method, params
        assert method == 'RESP_LIST_ROOMS'
        assert params['Status'] == 'OK'
        room_list = map(self.decode_string, params['Content'].split('\n'))
        return room_list

    def list_members(self):
        method, params = self.send_req(method='LIST_MEMBERS')
        assert method == 'RESP_LIST_MEMBERS'
        assert params['Status'] == 'OK'
        member_list = map(self.decode_string, params['Content'].split('\n'))
        return member_list

    def join_room(self, room_name):
        room_name = self.encode_string(room_name)
        method, params = self.send_req(method='JOIN_ROOM', params={'Room-Name': room_name})
        assert method == 'RESP_JOIN_ROOM'
        assert params['Status'] == 'OK'
        self.current_room = room_name

    def exit_room(self):
        method, params = self.send_req(method='EXIT_ROOM')
        assert method == 'RESP_EXIT_ROOM'
        assert params['Status'] == 'OK'

    def send_msg(self, message):
        message = self.encode_string(message)
        # escape \t because later will use \t to split message attributes
        message = message.replace('\t', '    ')
        method, params = self.send_req(method='SEND_MSG', content=message)
        assert method == 'RESP_SEND_MSG'
        assert params['Status'] == 'OK'

    def recv_msg(self):
        method, params = self.send_req(method='RECV_MSG')
        print 'method = {0}'.format(method)
        if method == 'NO_NEW_MSG':
            return None
        elif method == 'NEW_MSG':
            messages = map(self.decode_string, params['Content'].split('\t\t'))
            return messages
        else:
            raise BadMethodException

    def dispatch(self, event):
        print 'dispatching event: {0}'.format(event)
        self.handlers[event]()

    def loop(self):
        while True:
            # Wait for user event
            event = ''
            self.dispatch(event)


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