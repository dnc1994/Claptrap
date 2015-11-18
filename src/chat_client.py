import socket
import struct
import logging
import libchat


logger = logging.getLogger('chat.client')

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
            'LEAVE_ROOM': self.leave_room,
            'SEND_MSG': self.send_msg,
            'RECV_MSG': self.recv_msg
        }
        if gui:
            self.loop()

    def send_req(self, method, params=None, content=None):
        req = [method]
        req += ['{0}: {1}'.format(k, v) for (k, v) in params.iteritems()] if params else []
        req += '\n' + content if content else []
        req = '\n'.join(req)
        try:
            self.sock.sendall(libchat.packetify(req))
        except socket.error as e:
            raise
        resp = libchat.recv_packet(self.sock)
        return libchat.parse(resp, libchat.RESPONSE)

    def login(self, username, password):
        resp = self.send_req(method='LOGIN', params={'Username': username, 'Password': password})
        if resp[0] == 'WELCOME':
            self.logined = True
        elif resp[0] == 'GO_AWAY':
            pass
        else:
            raise

    def logout(self):
        resp = self.send_req(method='LOGOUT')
        assert resp[0] == 'OK'

    def create_room(self, room_name):
        resp = self.send_req(method='CREATE_ROOM', params={'Root-Name': room_name})
        assert resp[1]['Status'] == 'OK'

    def list_rooms(self):
        resp = self.send_req(method='LIST_ROOMS')
        room_list = resp[1]['Content'].split('\n')

    def list_members(self):
        resp = self.send_req(method='LIST_MEMBERS')
        room_list = resp[1]['Content'].split('\n')

    def join_room(self, room_name):
        resp = self.send_req(method='JOIN_ROOM', params={'Root-Name': room_name})
        assert resp[0] == 'RESP_JOIN_ROOM'
        assert resp[1]['Status'] == 'OK'

    def leave_room(self, room_name):
        resp = self.send_req(method='LEAVE_ROOM')
        assert resp[0] == 'SEE_YOU'

    def send_msg(self, message):
        # escape \t because later will use \t to split message attributes
        message = message.replace('\t', '    ')
        resp = self.send_req(method='SEND_MSG', params={'Message': message})
        assert resp[1]['Status'] == 'OK'

    def recv_msg(self):
        resp = self.send_req(method='RECV_MSG')
        if resp[0] == 'NO_NEW_MSG':
            pass
        else:
            messages = resp[1]['Content'].split('\t\t')

    def dispatch(self, event):
        self.handlers[event]()

    def loop(self):
        while True:
            # Wait for user event
            event = ''
            self.dispatch(event)

def main():
    client = ChatClient()
    client.login('xiaoming', '123')

if __name__ == '__main__':
    main()