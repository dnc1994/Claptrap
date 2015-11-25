import socket
import threading
import hashlib
import datetime
import logging
import libchat
from commons import *


def get_server_time_obj():
    return datetime.datetime.now()


logger = logging.getLogger('chat.server')

HOST = ''
PORT = 6666
BUFF_SIZE = 1024


server_count = 0


class ChatServer(threading.Thread):
    def __init__(self, conn, addr):
        super(ChatServer, self).__init__()

        global  server_count
        server_count += 1
        print 'server #%d started' % (server_count)

        self.conn = conn
        self.addr = addr
        self.ip = self.addr[0]
        self.username = ''
        self.current_room = ''
        self.last_recv_msg = None
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

    def send_resp(self, method, params=None, content=None):
        # print 'prepare to send response'
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
            logger.critical('Send response error: %s', e)
            raise

    # todo: sign up
    def login(self, params):
        global accounts
        global clients
        username = params['Username']
        pass_digest = hashlib.sha1(params['Password']).hexdigest()
        if not accounts.has_key(username) or accounts[username]['password'] != pass_digest:
            self.send_resp(method='RESP_LOGIN', params={'Status': 'AUTH_FAILED'})
        else:
            self.send_resp(method='RESP_LOGIN', params={'Status': 'OK'})
            self.username = username
            clients[username] = self.conn

    # todo: CLEAN UP
    def logout(self, params):
        global clients
        # remember to clean up
        clients.remove(self.username)
        rooms[self.current_room]['members'].remove(self.username)
        self.send_resp(method='RESP_LOGOUT', params={'Status': 'OK'})
        # self.conn.close()
        # exit()

    def create_room(self, params):
        global rooms
        room_name = params['Room-Name']
        print 'creating room' + room_name
        if rooms.has_key(room_name):
            self.send_resp(method='RESP_CREATE_ROOM', params={'Status': 'ROOM_NAME_EXISTED'})
        else:
            print 'room created'
            rooms[room_name] = {'members': [], 'messages': []}
            self.send_resp(method='RESP_CREATE_ROOM', params={'Status': 'OK'})

    def list_rooms(self, params):
        print 'listing rooms'
        global rooms
        room_list = rooms.keys()
        content = '\n'.join([r + '\t' + str(len(rooms[r]['members'])) for r in room_list])
        print content
        self.send_resp(method='RESP_LIST_ROOMS', params={'Status': 'OK'}, content=content)

    def list_members(self, params):
        global rooms
        member_list = rooms[self.current_room]['members']
        content = '\n'.join(member_list)
        self.send_resp(method='RESP_LIST_MEMBERS', params={'Status': 'OK'}, content=content)

    def join_room(self, params):
        # print 'joining rooms'
        global rooms
        # print params
        room_name = params['Room-Name']
        # print room_name
        if not rooms.has_key(room_name):
            self.send_resp(method='RESP_JOIN_ROOM', params={'Status': 'NO_SUCH_ROOM'})
        else:
            print 'adding to member list'
            rooms[room_name]['members'].append(self.username)
            self.current_room = room_name
            self.last_recv_msg = get_server_time_obj()
            self.send_resp(method='RESP_JOIN_ROOM', params={'Status': 'OK'})

    def exit_room(self, params):
        global rooms
        if self.current_room == '':
            self.send_resp(method='RESP_EXIT_ROOM', params={'Status': 'NOT_IN_ROOM'})
        else:
            rooms[self.current_room]['members'].remove(self.username)
            self.current_room = ''
            self.send_resp(method='RESP_EXIT_ROOM', params={'Status': 'OK'})

    def send_msg(self, params):
        print 'sending message'
        global rooms
        room_name = self.current_room
        assert room_name
        print room_name
        message = params['Content']
        print message
        rooms[room_name]['messages'].append({'From': self.username, 'Time': get_server_time_obj(), 'Message': message})
        self.send_resp(method='RESP_SEND_MSG', params={'Status': 'OK'})

    def recv_msg(self, params):
        global rooms
        if self.current_room == '':
            self.send_resp(method='NO_NEW_MSG', params={'Status': 'NOT_IN_ROOM'})
        room_name = self.current_room
        print 'room name = {0}'.format(room_name)
        print '#messages = {0}'.format(len(rooms[room_name]['messages']))
        messages = []
        for index in reversed(range(len(rooms[room_name]['messages']))):
            msg = rooms[room_name]['messages'][index]
            print 'message time: {0}'.format(msg['Time'])
            print 'last recv time: {0}'.format(self.last_recv_msg)
            if msg['Time'] < self.last_recv_msg:
                print 'scrolling message break'
                break
            messages = [msg] + messages
        print '{0} new message'.format(len(messages))
        print messages
        if not messages:
            self.send_resp(method='NO_NEW_MSG', params={'Status': 'NO_NEW_MSG'})
        content = '\t\t'.join(['{0}\t{1}\t{2}'.format(m['From'], m['Time'].ctime(), m['Message']) for m in messages])
        print content
        self.last_recv_msg = get_server_time_obj()
        self.send_resp(method='NEW_MSG', params={'Status': 'OK'}, content=content)

    def dispatch(self, req):
        method, params = req
        print 'dispatching request: {0}'.format(method)
        if method in PARSE_EXCEPTIONS:
            raise
        self.handlers[method](params)
        # todo: write to db

    def start(self):
        while True:
            packet_data = libchat.recv_packet(self.conn)
            self.dispatch(libchat.parse(packet_data, libchat.REQUEST))


def init_globals():
    global accounts
    global rooms
    _accounts = {'root': 'claptrap', 'xiaoming': '123', 'xiaohong': '123', 'xiaowang': '123'}
    for (u, p) in _accounts.iteritems():
        accounts[u] = {}
        accounts[u]['password'] = hashlib.sha1(p).hexdigest()

    _rooms = ['test1', 'test2', 'test3']
    for r in _rooms:
        rooms[r] = {}
        rooms[r]['members'] = ['root']
        rooms[r]['messages'] = []


def main():
    global accounts
    global clients
    global rooms
    accounts = {}
    clients = {}
    rooms = {}

    # todo: load from db
    init_globals()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    # sock.setblocking(0)
    sock.listen(5)
    while True:
        try:
            conn, addr = sock.accept()
            print 'incoming client'
            print conn, addr
            server = ChatServer(conn, addr)
            server.start()
        except Exception as e:
            try:
                server.logout(None)
                raise e
            except:
                pass


if __name__ == '__main__':
    try:
        print 'Server started'
        main()
    except KeyboardInterrupt:
        print 'Server terminating...'
    except Exception:
        raise Exception
