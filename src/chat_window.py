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
        self.setWindowTitle(self.client.current_room+'test')
        self.setWindowIcon(QtGui.QIcon('img\\claptrap.ico'))
        self.resize(550, 550)

        self.textBrowser = QtGui.QTextBrowser(self)
        self.textBrowser.setGeometry(QtCore.QRect(25, 25, 400, 400))

        self.textEditor = QtGui.QTextEdit(self)
        self.textEditor.EchoMode = 2
        self.textEditor.setGeometry(QtCore.QRect(25, 450, 400, 500))

        self.send_btn = QtGui.QPushButton('Send', self)
        self.connect(self.send_btn, QtCore.SIGNAL('pressed()'), self.send_msg)

    def send_msg(self):
        msg = str(self.textEditor.toPlainText())
        self.client.send_msg(msg)
        self.textEditor.clear()
        self.update_display()
        pass

    def update_display(self):
        msg_list = self.client.recv_msg()
        for msg in msg_list:
            msg_from, msg_time, msg_content = msg.split('\t')
            self.textBrowser.append(msg_content)


if __name__ == '__main__':
    client = ChatClient()
    client.join_room('test1')
    app = QtGui.QApplication(sys.argv)
    chat_window = ChatWindow(client)
    chat_window.show()
    sys.exit(app.exec_())
