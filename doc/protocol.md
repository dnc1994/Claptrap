# Claptrap chatting protocol

## Enter a chatroom
Method: JOIN_ROOM
From: $Username
To: $Room
Time: $Time

## Leave a chatroom
Method: LEAVE_ROOM
From: $Username
To: $Room
Time: $Time

## Send
Method: SEND_MSG
From: $Username
To: $Username / $Root
Time: $Time
Content-Length: $Length

Text

## Receive
Method: RECV_MSG
From: $Username