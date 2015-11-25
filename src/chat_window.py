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
        self.setWindowTitle('Room: {0}'.format(self.client.current_room))
        self.setWindowIcon(QtGui.QIcon('img\\claptrap.ico'))
        self.resize(550, 550)

        self.textBrowser = QtGui.QTextBrowser(self)
        self.textBrowser.setGeometry(QtCore.QRect(25, 25, 400, 400))

        self.textEditor = QtGui.QTextEdit(self)
        self.textEditor.setGeometry(QtCore.QRect(25, 450, 350, 500))

        self.send_btn = QtGui.QPushButton('Send', self)
        self.send_btn.setGeometry(375, 450, 400, 500)
        self.send_btn.clicked.connect(self.send_msg)

        # layout = QtGui.QVBoxLayout(self)
        # layout.addWidget(self.textBrowser)
        # layout.addWidget(self.textEditor)
        # layout.addWidget(self.send_btn)

    def send_msg(self):
        # codec trick
        codec = QtCore.QTextCodec.codecForName('UTF-16')
        msg = unicode(codec.fromUnicode(self.textEditor.toPlainText()), 'UTF-16').encode('utf-8')
        if not msg:
            return
        self.client.send_msg(msg)
        self.textEditor.clear()
        self.update_display()

    def update_display(self):
        msg_list = self.client.recv_msg()
        for msg in msg_list:
            msg_from, msg_time, msg_content = msg.split('\t')
            self.textBrowser.append(msg_content.decode('utf-8'))

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Return:
            self.send_msg()


if __name__ == '__main__':
    client = ChatClient()
    client.join_room('test1')
    print client.current_room
    app = QtGui.QApplication(sys.argv)
    chat_window = ChatWindow(client)
    chat_window.show()
    sys.exit(app.exec_())
