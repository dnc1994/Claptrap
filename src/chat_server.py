import socket
import threading
import hashlib
import datetime
import libchat


def get_server_time_obj():
    return datetime.datetime.now()


class ChatServer(threading.Thread):
    def __init__(self, conn, addr):
        super(ChatServer, self).__init__()
        self.conn = conn
        self.addr = addr
        self.ip = self.addr[0]
        self.username = ''
        self.current_room = ''
        self.last_recv_msg = ''
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

    def send_resp(self, method, params=None, content=None):
        resp = [method]
        resp += ['{0}: {1}'.format(k, v) for (k, v) in params.iteritems()] if params else []
        resp += '\n' + content if content else []
        resp = '\n'.join(resp)
        self.conn.send(resp)

    # todo: sign up
    def login(self, params):
        global accounts
        global clients
        username = params['Username']
        pass_digest = hashlib.sha1(params['Password']).hexdigest()
        if not accounts.has_key(username) or accounts[username]['password'] != pass_digest:
            self.send_resp(method='GO_AWAY')
        else:
            self.send_resp(method='WELCOME')
            self.username = username
            clients[username] = self.conn

    def logout(self, params):
        global clients
        self.send_resp(method='BYEBYE')
        clients.remove(self.username)
        self.conn.close()
        exit()

    def create_room(self, params):
        global rooms
        room_name = params['Room-Name']
        if rooms.has_key():
            self.send_resp(method='RESP_CREATE_ROOM', params={'Status': 'ROOM_NAME_EXISTED'})
            return
        else:
            rooms[room_name] = {'members': [], 'messages': []}

    def list_rooms(self):
        global rooms
        room_list = rooms.keys()
        content = '\n'.join([r + '\t' + str(len(rooms[r]['members'])) for r in room_list])
        self.send_resp(method='RESP_LIST_ROOM', content=content)

    def list_members(self):
        global rooms
        room_name = self.current_room
        member_list = rooms[room_name]['members']
        content = '\n'.join(member_list)
        self.send_resp(method='RESP_LIST_MEMBERS', content=content)

    def join_room(self, params):
        global rooms
        room_name = params['Root-Name']
        if not rooms.has_key(room_name):
            self.send_resp(method='RESP_JOIN_ROOM', params={'Status': 'NO_SUCH_ROOM'})
        rooms[room_name]['members'].append(self.username)
        self.current_room = room_name
        self.last_recv_msg = get_server_time_obj()

    def leave_room(self, params):
        global rooms
        room_name = self.current_room
        rooms[room_name]['members'].remove(self.username)
        self.current_room = ''
        self.send_resp(method='SEE_YOU')

    def send_msg(self, params):
        global rooms
        room_name = self.current_room
        message = params['Message']
        rooms[room_name]['messages'].append({'From': self.username, 'Time': get_server_time_obj(), 'Message': message})
        self.send_resp(method='RESP_SEND_MSG', params={'Status': 'OK'})

    def recv_msg(self, params):
        global rooms
        room_name = self.current_room
        messages = []
        for index in reversed(range(len(rooms[room_name]['messages']))):
            msg = rooms[room_name]['messages'][index]
            if msg['Time'] < self.last_recv_msg:
                break
            messages = msg + messages
        if not messages:
            self.send_resp(method='NO_NEW_MSG')
        for message in messages:
            content = message['Message']
            message.remove('Message')
            self.send_resp(method='NEW_MSG', params=message, content=content)

    def dispatch(self, request):
        (method, params) = libchat.parse(request, libchat.REQUEST)
        if method in libchat.PARSE_EXCEPTIONS:
            # todo: logging
            return
        self.handlers[method](params)
        # todo: write to db


HOST = ''
PORT = 6666


def init_accounts():
    global accounts
    users = {'root': 'claptrap', 'xiaoming': '123', 'xiaohong': '123', 'xiaowang': '123'}
    for (u, p) in users:
        accounts[u] = hashlib.sha1(p).hexdigest()


def main():
    global accounts
    global clients
    global rooms

    # todo: load from db
    init_accounts()
    clients = {}
    rooms = {}

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    while True:
        try:
            conn, addr = sock.accept()
            server = ChatServer(conn, addr)
            server.start()
        except Exception as e:
            print e

if __name__ == '__main__':
    try:
        print 'Server started'
        main()
    except KeyboardInterrupt:
        print 'Server terminating...'
