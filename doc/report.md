# Computer Networks Project Report

## Overview

���� Project �� Python 2.7 ������

���粿��ʹ���� socket + select������������ʹ���� threading��GUI ʹ���� PyQt4��

## Protocol Design

### Overview

Claptrap ��Ӧ�ò���ַ���Э�飬ÿ������ 12 �ֽڵ� Header �Ͳ������ȵ� Payload ��ɡ�

�����ַ��� UTF-8 ���롣

### Header

Header �� 8 ���ֽڵ� CLAPTRAP ��Э���ʶ���� 4 ���ֽڵ� `Packet-Length` ����ɡ�

### Payload

Payload ������ʽ���£�

    Method
    Parameter0: Value 0
    Parameter1: Value 1
    ...
    /n
    Content

Ҳ���ǵ�һ��ָ�������������������и���һϵ�в������ټ��һ�����к���������

���д���������İ����� `Content-Length` ��������֤���ȡ�

�����г������������Ӧ�ĸ�ʽ��ÿ���������ǲ����ĺ������������Ӧ���Ǻ���ȷ�ġ�

#### Client

| Request Method | Description | Parameters | Content | Possible Response Methods |
| -------------- | ----------- | ---------- | ------- | --------------- |
| LOGIN | �û���½ | {Username, Password} | None | RESP_LOGIN |
| LOGOUT | �û�ע�� | None | None | RESP_LOGOUT |
| LIST_ROOMS | ��ȡ�����б� | {Room-Name} | None | RESP_LIST_ROOMS |
| LIST_MEMBERS | ��ȡ��ǰ�����û��б� | None | None | RESP_LIST_MEMBERS |
| JOIN_ROOM | ���뷿�� | {Room-Name} | None | RESP_JOIN_ROOM |
| EXIT_ROOM | �˳����� | None | None | RESP_EXIT_ROOM |
| SEND_MSG | ������Ϣ | {Content-Length} | Message | RESP_SEND_MSG |
| RECV_MSG | ������Ϣ | None | None | NO_NEW_MSG / NEW_MSG |

#### Server

| Response Method | Possible Status | Parameters | Content |
| --------------- | --------------- | ---------- | ------- |
| RESP_LOGIN | OK / AUTH_FAILED | {Status} | None |
| RESP_LOGOUT | OK / NOT_LOGIN | {Status} | None |
| RESP_LIST_ROOMS | OK / NOT_LOGIN | {Status, Content-Length} | Rooms |
| RESP_LIST_MEMBERS | OK / NOT_IN_ROOM / NOT_LOGIN | {Status, Content-Length} | Members |
| RESP_JOIN_ROOM | OK / NO_SUCH_ROOM / NOT_LOGIN | {Status} | None |
| RESP_EXIT_ROOM | OK / NOT_IN_ROOM / NOT_LOGIN | {Status} | None |
| RESP_SEND_MSG | OK / NOT_IN_ROOM / NOT_LOGIN | {Status} | None |
| NO_NEW_MSG | NOT_IN_ROOM / NO_NEW_MSG / NOT_LOGIN | None |
| NEW_MSG | OK / NOT_LOGIN | {Status, Content-Length} | Messages |

#### Content Formats

�����г�����������ĸ�ʽ��

##### SEND_MSG > Message

    Message

##### RESP_LIST_ROOMS > Rooms

�� `\n` �ָ������ɷ�������

    Room0\n
    Room1\n
    ...

##### RESP_LIST_MEMBERS > Members

�� `\n` �ָ��������û�����

    Member0\n
    Member1\n
    ...

##### NEW_MSG > Messages

�� `\n` �ָ�����������Ϣ��ÿ����Ϣ�����ͷ�������ʱ�䡢��Ϣ���ݣ���`\t`�ָ���

    From\tTime\tContent\n
    From\tTime\tContent\n
    ...

## Implementation Details

��һ������Ҫ���۴���ʵ���ϵ�ϸ�ڣ�����ȥ������ҵ���߼���صĲ��ֲ�̸��

### Network

#### Why select?

���� Project ʹ���� socket + select ��������ͨѶ������ select ��һ�� Python �Դ������ڼ��Ӷ���ļ���������ģ�飬�����ڹ��� socket �� IO �¼���ʹ�� select ������������

1. ʹ�� Python ���� socket ����ʱ select �������Ǳ��䡣
2. Python �� socket ����ʹ�������ʹ�� select ������ socket �¼�����ֻ���� blocking socket �� non-blocking socket ֮���ѡһ�����ѡ�� blocking socket����ô server ֻ��ͬʱ����һ�� client���µ� client ����������ᱻһֱ���������ѡ�� non-blocking socket����ô��һ��������������ɵ�����¾ͻᴥ���쳣��Ҳ���޷����ֳ����ӡ�һ�����з����ǲ��� non-blocking socket + timeout����ÿ�� socket ����ܳ��ĳ�ʱ����������������Ȼ���Һܳ�ª��
3. select �����������ֻ�Ǽ������е� socket IO��ʹ�ö��û�ͬʱ���߳�Ϊ���ܣ�ʵ�ʵ�����ͨѶ������ socket ���С�

#### Socket tricks

Ϊ�˸��õط���������Ҫ�� Python �� socket ����һЩ��װ��

���ȣ����� `socket.recv` ������ȡ����󻺳�����������ϵͳ���Ƶģ����Ǿ�Ҫ���ð��е� `Packet-Length` ����ȷ��ÿ�δӻ������ж�ȡһ�������İ���

���粿�ֵĺ�����������������հ��йصĺ�����

    # �ӻ�������ȡ����Ϊ length ������
    def recv_all(sock, length):
        length = int(length)
        data = ''
        received = 0
        while received < length:
            part = sock.recv(length - received)
            if len(part) == 0:
                # ���Ȳ�ƥ��
                raise socket.error('Socket recv EOF')
            data += part
            received += len(part)
        return data
        
    # �ӻ�������ȡһ������
    def recv_packet(sock):
        try:
            # ����ȡ 8 �ֽ�Э���ʶ
            buff = recv_all(sock, 8)
            try:
                assert buff == 'CLAPTRAP'
            except:
                raise BadProtocolException
            # ����ȡ 4 �ֽ� Packet-Length
            buff = recv_all(sock, 4)
            # struct ���ڽ��������ݱ���Ϊ�ַ���
            packet_length = struct.unpack('!I', buff)[0] - 12
            # ��ȡʣ�µ�����
            packet_data = recv_all(sock, packet_length)
        except socket.error as e:
            raise
        return packet_data

���Ͱ����������������࣬��Ҫͨ�����º�����װ���ݣ�

    def packetify(data):
        length = len(data) + 12
        protocol = 'CLAPTRAP'
        length = struct.pack('!I', length)
        packet_data = protocol + length + data
        return packet_data

��ʹ�� `socket.sendall(packetify(data))' ���ͼ��ɡ�

### Server Class

Server ��� `threading.Thread` �̳ж�����ͨ�����´���ʵ�ֶ�ÿһ�� client ����һ���µ��߳�ά����������ӣ�

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    CONNECTION_LIST = []
    CONNECTION_LIST.append(server_socket)

    while True:
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST,[],[])
        for sock in read_sockets:
            # ����һ���� client
            if sock == server_socket:
                conn, addr = server_socket.accept()
                CONNECTION_LIST.append(conn)
                # ����һ���� Server ʵ�����̣߳�
                server = ChatServer(conn, addr)
                server.start()
   
�� Server �ڲ�ͨ�����´����������� client ֮���ͨ�ţ�
            
    try:
        read_sockets, write_sockets, error_sockets = select.select([self.conn],[],[])
        if len(read_sockets) > 0:
            # ��ȡһ����
            packet_data = libchat.recv_packet(self.conn)
            # �����������Ӧ�� request handler
            self.dispatch(libchat.parse(packet_data, libchat.REQUEST))
    except:
        # client �Ͽ����ӣ������˳�
        print 'client disconnected.'
        self.logout(None)
        return                

### Client Class

Client ��û��̫��ɽ��ģ���һ�����Ҫע�⴦���ַ����롣

Э�������������� UTF-8 ���룬���ڷ������Ϳͻ����ڲ������� unicode ��ʽ���棨Ϊ�˷����ַ��������� GUI ���֣�����ô��ÿ�� request handler �Ŀ�ͷ�ͽ�β����Ҫ���ñ���ת��������

### User Interface

GUI ʹ�� PyQt4 ʵ�֣�Ҳû��̫��ɽ��ġ�

Ĭ��ÿ 1 ������ȡһ������Ϣ��ÿ 5 ����ˢ�·����б���û��б�

## Demo Notes

�ύ�ļ��е� `chat_server.exe` �� `chat_client_gui.exe` ���� 32 λ pyinstaller �����Ŀ�ִ���ļ������������Ӧ�����ڸ���ƽ̨�����С�

Ҳ���Դ�Դ�����У�����Ϊ Python 2.7 �� PyQt4��

������Ĭ�϶˿�Ϊ 6666�����֧�� 5 ���ͻ���ͬʱ���ߡ�����ͨ�� `chat_server.exe PORT MAX_ONLINE` ������ָ���˿ں����ͬʱ������Ŀ��

������������ʱ��� `globals.txt` �ж�ȡһЩԤ����˺źͷ����б�Ϊ�˲��Գ������ͨ���޸ĸ��ļ�����µ��˺źͷ��䣬Ҫ���ʽ��ԭ����ͬ���ļ�����Ϊ UTF-8������ᱨ��

�����ͻ���ʱ����ʹ��Ԥ����û����������¼���ڽ������Ͻǿ��Կ��������б�˫�����Խ��뷿�䣬���½ǿ��Կ�����ǰ����������û������뷿�����Է�����Ϣ��CTRL+ENTER��������ҵ���߼�������� Project ���ص㣬ҲΪ��ʵ�ֵı�����ֻ���յ�ǰ�������Ϣ����������ʷ��Ϣ��
