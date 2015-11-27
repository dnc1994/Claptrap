# -*- encoding:utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
from chat_client import ChatClient


class ChatWindow(QtGui.QMainWindow):
    def __init__(self, client=None):
        super(ChatWindow, self).__init__()
        if client:
            print 'init on creation'
            self.client = client
            self.init_ui()

    def init_ui(self):
        print 'init later'
        self.setWindowIcon(QtGui.QIcon('img\\claptrap.ico'))
        self.resize(800, 850)

        # define widgets
        self.message_browser = QtGui.QTextBrowser(self)
        self.message_browser.setGeometry(QtCore.QRect(25, 25, 500, 600))
        self.message_editor = QtGui.QTextEdit(self)
        self.message_editor.setGeometry(QtCore.QRect(25, 650, 500, 175))
        self.room_list = QtGui.QListView(self)
        self.room_list.setGeometry(QtCore.QRect(550, 25, 225, 390))
        self.member_list = QtGui.QListView(self)
        self.member_list.setGeometry(QtCore.QRect(550, 435, 225, 390))

        # set widget attributes
        self.room_list.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        QtCore.QObject.connect(self.room_list, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self, QtCore.SLOT('switch_room(QModelIndex)'))
        self.member_list.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        # update display once
        self.update_title()
        self.update_roomlist()
        self.update_memberlist()
        self.update_messages()
        self.message_browser.append('[System] Enter a room and start chatting.\n')

        # set timers
        self.roomlist_timer = QtCore.QTimer(self)
        self.roomlist_timer.setInterval(5000)
        self.roomlist_timer.timeout.connect(self.update_roomlist)
        self.memberlist_timer = QtCore.QTimer(self)
        self.memberlist_timer.setInterval(5000)
        self.memberlist_timer.timeout.connect(self.update_memberlist)
        self.messages_timer = QtCore.QTimer(self)
        self.messages_timer.setInterval(1000)
        self.messages_timer.timeout.connect(self.update_messages)

        self.roomlist_timer.start()
        self.memberlist_timer.start()
        self.messages_timer.start()

    @QtCore.pyqtSlot("QModelIndex")
    def switch_room(self, index):
        room_name = unicode(index.data().toString().split('\t')[0])
        print u'switching room to {0}'.format(room_name)
        if self.client.current_room:
            self.message_browser.append(u'[System] leaving room {0}\n'.format(self.client.current_room.decode('utf-8')))
            self.client.exit_room()
        self.client.join_room(room_name)
        self.message_browser.append(u'[System] Welcome to room {0}\n'.format(room_name))

        self.update_title()
        self.update_roomlist()
        self.update_memberlist()

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
        room_list = self.client.list_rooms()
        room_list_model = QtGui.QStandardItemModel(self.room_list)

        if not room_list:
            self.room_list.setModel(room_list_model)
            return
        for room in room_list:
            room_name, online_number = room.split('\t')
            item = QtGui.QStandardItem()
            item.setText(u'{0}\t({1})'.format(room_name, online_number))
            room_list_model.appendRow(item)
        self.room_list.setModel(room_list_model)

    @QtCore.pyqtSlot()
    def update_memberlist(self):
        if not self.client.current_room:
            return

        member_list = self.client.list_members()
        member_list_model = QtGui.QStandardItemModel(self.room_list)

        if not member_list:
            return
        for member in member_list:
            item = QtGui.QStandardItem()
            item.setText(member)
            member_list_model.appendRow(item)
        self.member_list.setModel(member_list_model)

    @QtCore.pyqtSlot()
    def update_messages(self):
        msg_list = self.client.recv_msg()
        if not msg_list:
            print 'No New Message'
            return
        print 'updating messages'
        for msg in msg_list:
            msg_from, msg_time, msg_content = msg.split('\t')
            message = u'{0} ({1}):\n{2}\n'.format(msg_from, msg_time, msg_content)
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
