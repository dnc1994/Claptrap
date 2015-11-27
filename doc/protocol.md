# Claptrap Protocol

## Overview

Claptrap ��Ӧ�ò���ַ���Э�飬ÿ������ 12 �ֽڵ� Header �Ͳ������ȵ� Payload ��ɡ�

�����ַ��� UTF-8 ���롣

## Header

Header �� 8 ���ֽڵ� CLAPTRAP ��Э���ʶ���� 4 ���ֽڵ� `Packet-Length` ����ɡ�

## Payload

Payload ������ʽ���£�

    Method
    Parameter0: Value 0
    Parameter1: Value 1
    ...
    /n
    Content

Ҳ���ǵ�һ��ָ�������������������и���һϵ�в������ټ��һ�����к���������

���д���������İ����� Content-Length ��������֤���ȡ�

�����г������������Ӧ�ĸ�ʽ��ÿ���������ǲ����ĺ������������Ӧ���Ǻ���ȷ�ġ�

### Client

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

### Server

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

### Content Formats

�����г�����������ĸ�ʽ��

#### SEND_MSG > Message

    Message

#### RESP_LIST_ROOMS > Rooms

�� `\n` �ָ������ɷ�������

    Room0\n
    Room1\n
    ...

#### RESP_LIST_MEMBERS > Members

�� `\n` �ָ��������û�����

    Member0\n
    Member1\n
    ...

#### NEW_MSG > Messages

�� `\n` �ָ�����������Ϣ��ÿ����Ϣ�����ͷ�������ʱ�䡢��Ϣ���ݣ���`\t`�ָ���

    From\tTime\tContent\n
    From\tTime\tContent\n
    ...
