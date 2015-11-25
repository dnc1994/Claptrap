# -*- encoding:utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
from chat_client import ChatClient


class LoginDialog(QtGui.QDialog):
    def __init__(self, client):
        super(LoginDialog, self).__init__()
        self.client = client
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Claptrap Login')
        self.resize(300, 300)

        self.username_label = QtGui.QLabel('Username', self)
        self.username_input = QtGui.QLineEdit(self)
        self.password_label = QtGui.QLabel('Password', self)
        self.password_input = QtGui.QLineEdit(self)
        self.login_btn = QtGui.QPushButton('Login', self)
        self.login_btn.clicked.connect(self.login)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        login_resp = self.client.login(username, password)
        if not login_resp:
            QtGui.QMessageBox.warning(self, 'Login Failed', 'Wrong username or password')
        else:
            self.accept()


if __name__ == '__main__':
    client = ChatClient()
    app = QtGui.QApplication(sys.argv)
    login_dialog = LoginDialog(client)
    login_dialog.show()
    sys.exit(app.exec_())
