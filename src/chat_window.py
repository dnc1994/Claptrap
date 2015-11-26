# -*- encoding:utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
from chat_client import ChatClient


class ChatWindow(QtGui.QMainWindow):
    def __init__(self, client):
        super(ChatWindow, self).__init__()
        self.client = client
        self.init_ui()

    def init_ui(self):
        if self.client.current_room:
            title = 'Room: ' + self.client.current_room
        else:
            title = 'Claptrap'
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon('img\\claptrap.ico'))
        self.resize(550, 500)

        self.textBrowser = QtGui.QTextBrowser(self)
        self.textBrowser.setGeometry(QtCore.QRect(25, 25, 425, 425))

        self.textEditor = QtGui.QTextEdit(self)
        self.textEditor.setGeometry(QtCore.QRect(25, 450, 425, 475))

        self.roomList = QtGui.QListView(self)
        self.roomList.setGeometry(QtCore.QRect(450, 25, 525, 475))

        # layout = QtGui.QVBoxLayout(self)
        # layout.addWidget(self.textBrowser)
        # layout.addWidget(self.textEditor)
        # layout.addWidget(self.send_btn)

    def send_msg(self):
        if not self.client.current_room:
            self.textEditor.clear()
            return
        # codec trick
        codec = QtCore.QTextCodec.codecForName('UTF-16')
        msg = unicode(codec.fromUnicode(self.textEditor.toPlainText()), 'UTF-16').encode('utf-8')
        if not msg:
            return
        self.client.send_msg(msg)
        self.textEditor.clear()
        self.update_display()

    def update_display(self):
        if not self.client.current_room:
            self.textBrowser.append('Enter a room and start chatting.')

        room_list = self.client.list_rooms()
        if not room_list:
            return

        roomListModel = QtGui.QStandardItemModel(self.roomList)
        for room in room_list:
            item = QtGui.QStandardItem()
            item.setText(room)
            roomListModel.appendRow(item)
        self.roomList.setModel(roomListModel)

        msg_list = self.client.recv_msg()
        if not msg_list:
            return
        for msg in msg_list:
            msg_from, msg_time, msg_content = msg.split('\t')
            self.textBrowser.append(msg_content.decode('utf-8'))

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Return:
            self.send_msg()


if __name__ == '__main__':
    client = ChatClient()
    client.login('xiaoming', '123')
    client.join_room('test1')
    app = QtGui.QApplication(sys.argv)
    chat_window = ChatWindow(client)
    client.send_msg('caoniba')
    chat_window.show()
    sys.exit(app.exec_())
