# Claptrap Protocol

## Overview

Claptrap 是应用层的字符串协议，每个包由 12 字节的 Header 和不定长度的 Payload 组成。

所有字符以 UTF-8 编码。

## Header

Header 由 8 个字节的 CLAPTRAP （协议标识）和 4 个字节的 `Packet-Length` 域组成。

## Payload

Payload 基本格式如下：

    Method
    Parameter0: Value 0
    Parameter1: Value 1
    ...
    /n
    Content

也就是第一行指定方法，接下来若干行给出一系列参数，再间隔一个空行后是内容域。

所有带有内容域的包均有 Content-Length 参数来验证长度。

下面列出所有请求和响应的格式，每个方法或是参数的含义根据其名字应该是很明确的。

### Client

| Request Method | Description | Parameters | Content | Possible Response Methods |
| -------------- | ----------- | ---------- | ------- | --------------- |
| LOGIN | 用户登陆 | {Username, Password} | None | RESP_LOGIN |
| LOGOUT | 用户注销 | None | None | RESP_LOGOUT |
| LIST_ROOMS | 获取房间列表 | {Room-Name} | None | RESP_LIST_ROOMS |
| LIST_MEMBERS | 获取当前房间用户列表 | None | None | RESP_LIST_MEMBERS |
| JOIN_ROOM | 进入房间 | {Room-Name} | None | RESP_JOIN_ROOM |
| EXIT_ROOM | 退出房间 | None | None | RESP_EXIT_ROOM |
| SEND_MSG | 发送消息 | {Content-Length} | Message | RESP_SEND_MSG |
| RECV_MSG | 接收消息 | None | None | NO_NEW_MSG / NEW_MSG |

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

下面列出所有内容域的格式：

#### SEND_MSG > Message

    Message

#### RESP_LIST_ROOMS > Rooms

由 `\n` 分隔的若干房间名。

    Room0\n
    Room1\n
    ...

#### RESP_LIST_MEMBERS > Members

由 `\n` 分隔的若干用户名。

    Member0\n
    Member1\n
    ...

#### NEW_MSG > Messages

由 `\n` 分隔的若干行消息，每行消息含发送方、发送时间、消息内容，由`\t`分隔。

    From\tTime\tContent\n
    From\tTime\tContent\n
    ...
