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
        self.setWindowIcon(QtGui.QIcon('img\\claptrap.ico'))
        self.resize(550, 500)

        self.message_browser = QtGui.QTextBrowser(self)
        self.message_browser.setGeometry(QtCore.QRect(25, 25, 425, 425))
        self.message_editor = QtGui.QTextEdit(self)
        self.message_editor.setGeometry(QtCore.QRect(25, 450, 425, 475))
        self.room_list = QtGui.QListView(self)
        self.room_list.setGeometry(QtCore.QRect(450, 25, 525, 475))

        self.update_title()
        self.update_roomlist()
        self.update_messages()

        self.roomlist_timer = QtCore.QTimer(self)
        self.roomlist_timer.setInterval(5000)
        self.roomlist_timer.timeout.connect(self.update_messages)
        self.roomlist_timer.start()

        self.messages_timer = QtCore.QTimer(self)
        self.messages_timer.setInterval(1000)
        self.messages_timer.timeout.connect(self.update_messages)
        self.messages_timer.start()

        # layout = QtGui.QVBoxLayout(self)
        # layout.addWidget(self.textBrowser)
        # layout.addWidget(self.textEditor)
        # layout.addWidget(self.send_btn)

    def send_msg(self):
        if not self.client.current_room:
            self.message_editor.clear()
            return
        # codec trick
        codec = QtCore.QTextCodec.codecForName('UTF-16')
        msg = unicode(codec.fromUnicode(self.message_editor.toPlainText()), 'UTF-16').encode('utf-8')
        if not msg:
            return
        self.client.send_msg(msg)
        self.message_editor.clear()

    def update_title(self):
        if self.client.current_room:
            # only need decoding here
            title = 'Room: ' + self.client.current_room.decode('utf-8')
        else:
            title = 'Claptrap'
        self.setWindowTitle(title)

    @QtCore.pyqtSlot()
    def update_roomlist(self):
        if not self.client.current_room:
            self.message_browser.append('Enter a room and start chatting.')

        room_list = self.client.list_rooms()
        if not room_list:
            return

        roomListModel = QtGui.QStandardItemModel(self.room_list)
        for room in room_list:
            item = QtGui.QStandardItem()
            item.setText(room)
            roomListModel.appendRow(item)
        self.room_list.setModel(roomListModel)

    @QtCore.pyqtSlot()
    def update_messages(self):
        msg_list = self.client.recv_msg()
        if not msg_list:
            print 'No New Message'
            return
        for msg in msg_list:
            msg_from, msg_time, msg_content = msg.split('\t')
            message = u'{0}({1}):\n{2}\n'.format(msg_from, msg_time, msg_content)
            self.message_browser.append(message)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Return:
            self.send_msg()


if __name__ == '__main__':
    client = ChatClient()
    client.login(u'张宝华', '123')
    client.join_room(u'香港记者招待会')
    app = QtGui.QApplication(sys.argv)
    chat_window = ChatWindow(client)
    chat_window.show()
    sys.exit(app.exec_())
