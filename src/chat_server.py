# -*- encoding:utf-8 -*-
import sys
import socket
import threading
import select
import hashlib
import datetime
import libchat
from commons import *

HOST = ''
PORT = 6666
MAX_ONLINE = 5

server_count = 0


def get_server_time_obj():
    return datetime.datetime.now()


class ChatServer(threading.Thread):
    def __init__(self, conn, addr):
        super(ChatServer, self).__init__()
        global server_count
        server_count += 1
        print 'server #{0} started'.format(server_count)
        self.conn = conn
        self.addr = addr
        self.logined = False
        self.username = ''
        self.current_room = ''
        self.last_recv_msg = None
        self.handlers = {
            'LOGIN': self.login,
            'LOGOUT': self.logout,
            # 'CREATE_ROOM': self.create_room,
            'LIST_ROOMS': self.list_rooms,
            'LIST_MEMBERS': self.list_members,
            'JOIN_ROOM': self.join_room,
            'EXIT_ROOM': self.exit_room,
            'SEND_MSG': self.send_msg,
            'RECV_MSG': self.recv_msg
        }

    def send_resp(self, method, params=None, content=None):
        print 'prepare to send response {0}'.format(method)
        if 'Content' in RESPONSE_PARAMS[method]:
            try:
                assert params
            except:
                params = {}
            assert content
            params['Content-Length'] = len(content)

        resp = [method]
        resp += ['{0}: {1}'.format(k, v) for (k, v) in params.iteritems()] if params else []
        resp += (['\n{0}'.format(content)] if content else [])
        resp = '\n'.join(resp)
        print 'resp >>'
        print resp
        try:
            self.conn.sendall(libchat.packetify(resp))
        except socket.error as e:
            raise

    def login(self, params):
        global accounts
        global clients
        username = params['Username']
        pass_digest = hashlib.sha1(params['Password']).hexdigest()
        if not accounts.has_key(username) or clients.has_key(username) or accounts[username]['password'] != pass_digest:
            self.send_resp(method='RESP_LOGIN', params={'Status': 'AUTH_FAILED'})
        else:
            self.send_resp(method='RESP_LOGIN', params={'Status': 'OK'})
            self.logined = True
            self.username = username
            clients[username] = self.username

    # todo: CLEAN UP
    def logout(self, params):
        if not self.logined:
            self.send_resp(method='RESP_LOGOUT', params={'Status': 'NOT_LOGIN'})
            return
        global clients
        global rooms
        rooms[self.current_room]['members'].remove(self.username)
        del clients[self.username]
        self.send_resp(method='RESP_LOGOUT', params={'Status': 'OK'})

    # def create_room(self, params):
    #     global rooms
    #     room_name = params['Room-Name']
    #     if rooms.has_key(room_name):
    #         self.send_resp(method='RESP_CREATE_ROOM', params={'Status': 'ROOM_NAME_EXISTED'})
    #     else:
    #         rooms[room_name] = {'members': [], 'messages': []}
    #         self.send_resp(method='RESP_CREATE_ROOM', params={'Status': 'OK'})

    def list_rooms(self, params):
        if not self.logined:
            self.send_resp(method='RESP_LIST_ROOMS', params={'Status': 'NOT_LOGIN'})
            return
        global rooms
        room_list = rooms.keys()
        content = '\n'.join([r + '\t' + str(len(rooms[r]['members'])) for r in room_list])
        self.send_resp(method='RESP_LIST_ROOMS', params={'Status': 'OK'}, content=content)

    def list_members(self, params):
        if not self.logined:
            self.send_resp(method='RESP_LIST_ROOMS', params={'Status': 'NOT_LOGIN'})
            return
        global rooms
        member_list = rooms[self.current_room]['members']
        content = '\n'.join(member_list)
        self.send_resp(method='RESP_LIST_MEMBERS', params={'Status': 'OK'}, content=content)

    def join_room(self, params):
        if not self.logined:
            self.send_resp(method='RESP_JOIN_ROOM', params={'Status': 'NOT_LOGIN'})
            return
        global rooms
        room_name = params['Room-Name']
        if not rooms.has_key(room_name):
            self.send_resp(method='RESP_JOIN_ROOM', params={'Status': 'NO_SUCH_ROOM'})
        else:
            rooms[room_name]['members'].append(self.username)
            self.current_room = room_name
            self.last_recv_msg = get_server_time_obj()
            self.send_resp(method='RESP_JOIN_ROOM', params={'Status': 'OK'})

    def exit_room(self, params):
        if not self.logined:
            self.send_resp(method='RESP_EXIT_ROOM', params={'Status': 'NOT_LOGIN'})
            return
        global rooms
        if self.current_room == '':
            self.send_resp(method='RESP_EXIT_ROOM', params={'Status': 'NOT_IN_ROOM'})
        else:
            rooms[self.current_room]['members'].remove(self.username)
            self.current_room = ''
            self.send_resp(method='RESP_EXIT_ROOM', params={'Status': 'OK'})

    def send_msg(self, params):
        if not self.logined:
            self.send_resp(method='NO_NEW_MSG', params={'Status': 'NOT_LOGIN'})
            return
        global rooms
        room_name = self.current_room
        assert room_name
        message = params['Content']
        rooms[room_name]['messages'].append({'From': self.username, 'Time': get_server_time_obj(), 'Message': message})
        self.send_resp(method='RESP_SEND_MSG', params={'Status': 'OK'})

    def recv_msg(self, params):
        if not self.logined:
            self.send_resp(method='NO_NEW_MSG', params={'Status': 'NOT_LOGIN'})
            return
        global rooms
        if self.current_room == '':
            self.send_resp(method='NO_NEW_MSG', params={'Status': 'NOT_IN_ROOM'})
            return
        room_name = self.current_room
        messages = []
        for index in reversed(range(len(rooms[room_name]['messages']))):
            msg = rooms[room_name]['messages'][index]
            # print 'message time: {0}'.format(msg['Time'])
            # print 'last recv time: {0}'.format(self.last_recv_msg)
            if msg['Time'] < self.last_recv_msg:
                break
            messages = [msg] + messages
        print '{0} new message'.format(len(messages))
        if not messages:
            self.send_resp(method='NO_NEW_MSG', params={'Status': 'NO_NEW_MSG'})
            return
        content = '\t\t'.join(['{0}\t{1}\t{2}'.format(m['From'], m['Time'].ctime(), m['Message']) for m in messages])
        self.last_recv_msg = get_server_time_obj()
        self.send_resp(method='NEW_MSG', params={'Status': 'OK'}, content=content)

    def dispatch(self, req):
        method, params = req
        print '\ndispatching request: {0}'.format(method)
        if method in PARSE_EXCEPTIONS:
            raise Exception('ParseException: {0}'.format(method))
        self.handlers[method](params)

    def run(self):
        while True:
            try:
                try:
                    read_sockets, write_sockets, error_sockets = select.select([self.conn],[],[])
                    if len(read_sockets) > 0:
                        packet_data = libchat.recv_packet(self.conn)
                        self.dispatch(libchat.parse(packet_data, libchat.REQUEST))
                except:
                    print 'client disconnected, server exiting...'
                    self.logout(None)
                    return
            except:
                return


def _init_globals():
    global accounts
    global rooms

    _accounts = {'root': 'claptrap',
                 'xiaoming': '123',
                 'xiaohong': '123',
                 'xiaowang': '123',
                 u'江主席'.encode('utf-8'): '123',
                 u'张宝华'.encode('utf-8'): '123'
    }
    for (u, p) in _accounts.iteritems():
        accounts[u] = {}
        accounts[u]['password'] = hashlib.sha1(p).hexdigest()

    _rooms = ['test_room',
              u'香港记者招待会'.encode('utf-8')
    ]
    for r in _rooms:
        rooms[r] = {}
        rooms[r]['members'] = ['root']
        rooms[r]['messages'] = []


def init_globals():
    global accounts
    global rooms

    _accounts = {}
    _rooms = []

    with open('globals.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line == '':
                break
            u, p = line.split(' ')
            _accounts[u] = p

        for line in f:
            line = line.strip()
            if line == '':
                break
            r = line
            _rooms.append(r)

    for (u, p) in _accounts.iteritems():
        accounts[u] = {}
        accounts[u]['password'] = hashlib.sha1(p).hexdigest()

    for r in _rooms:
        rooms[r] = {}
        rooms[r]['members'] = ['root']
        rooms[r]['messages'] = []


def main(port=PORT, max_online=MAX_ONLINE):
    global accounts
    global clients
    global rooms
    accounts = {}
    clients = {}
    rooms = {}

    try:
        init_globals()
    except:
        print 'Error while loading globals. Please check globals.txt'
        exit()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, port))
    server_socket.listen(max_online)
    connection_list = []
    connection_list.append(server_socket)

    while True:
        read_sockets, write_sockets, error_sockets = select.select(connection_list,[],[])
        for sock in read_sockets:
            if sock == server_socket:
                conn, addr = server_socket.accept()
                connection_list.append(conn)
                server = ChatServer(conn, addr)
                server.start()


if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except:
        port = PORT
    try:
        max_online = int(sys.argv[2])
    except:
        max_online = MAX_ONLINE

    try:
        print 'Server started at port {1}'.format(HOST, port, max_online)
        main(port)
    except KeyboardInterrupt:
        print 'Server terminating...'
