# Claptrap chatting protocol

## Client

## Login
LOGIN
User: $Username
Pass: $Password

### Create a room
CREATE_ROOM
Room-Name: ...

### List all rooms
LIST_ROOMS

### List all members of the current room
LIST_MEMBERS

### Enter a room
JOIN_ROOM
Room-Name: ...

### Exit a room
Exit_ROOM

### Send
SEND_MSG
Content-Length: ...

...

### Receive
RECV_MSG

## Server

## Response to successful login
RESP_LOGIN
Status: OK / AUTH_FAILED

## Response to logout
RESP_LOGOUT
Status: OK

## Response to room creation
RESP_CREATE_ROOM
Status: OK / ROOM_NAME_EXISTED

## Response to room listing
RESP_LIST_ROOM
Status: OK
Name    members
...
...

## Response to room entry
RESP_JOIN_ROOM
Status: OK / NO_SUCH_ROOM / (NO_PRIVILEGE)

## Response to room exit
RESP_EXIT_ROOM
Status: OK

## Response to message sending
RESP_SEND_MSG
Status: OK

## Response to message receiving
NO_NEW_MSG
Status: NOT_IN_ROOM / NO_NEW_MSG

or

NEW_MSG

$From\t$Time\t$Content-Length\t\t
