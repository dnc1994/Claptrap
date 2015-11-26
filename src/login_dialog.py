# -*- encoding:utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
from chat_client import ChatClient


class LoginDialog(QtGui.QDialog):
    def __init__(self, callback_window):
        super(LoginDialog, self).__init__()
        self.callback_window = callback_window
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Claptrap Login')
        self.setWindowIcon(QtGui.QIcon('img\\claptrap.ico'))
        self.resize(300, 300)

        self.host_label = QtGui.QLabel('Host', self)
        self.host_input = QtGui.QLineEdit('127.0.0.1', self)
        self.port_label = QtGui.QLabel('Port', self)
        self.port_input = QtGui.QLineEdit('6666', self)
        self.username_label = QtGui.QLabel('Username', self)
        self.username_input = QtGui.QLineEdit('xiaoming', self)
        self.password_label = QtGui.QLabel('Password', self)
        self.password_input = QtGui.QLineEdit('123', self)

        self.login_btn = QtGui.QPushButton('Login', self)
        self.login_btn.clicked.connect(self.login)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.host_label)
        layout.addWidget(self.host_input)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)

    # todo: limit chars
    def login(self):
        host = self.host_input.text()
        port = self.port_input.text()
        if not host or not port:
            QtGui.QMessageBox.warning(self, 'Error', 'Please input host address and port number.')
            return
        try:
            self.client = ChatClient(host, port)
        except:
            QtGui.QMessageBox.warning(self, 'Connection Failed', 'Failed to connect to host.')
            return

        username = unicode(self.username_input.text())
        if not username:
            QtGui.QMessageBox.warning(self, 'Error', 'Please input username.')
            return
        password = self.password_input.text()
        if not username:
            QtGui.QMessageBox.warning(self, 'Error', 'Please input password.')
            return

        login_resp = self.client.login(username, password)
        if not login_resp:
            QtGui.QMessageBox.warning(self, 'Login Failed', 'Wrong username or password.')
            return

        self.callback_window.client = self.client
        print 'login OK'
        self.accept()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Return:
            self.login()


if __name__ == '__main__':
    client = ChatClient()
    app = QtGui.QApplication(sys.argv)
    login_dialog = LoginDialog(client)
    login_dialog.show()
    sys.exit(app.exec_())
