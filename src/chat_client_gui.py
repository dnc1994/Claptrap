# -*- encoding:utf-8 -*-
import sys
from PyQt4 import QtGui
from chat_client import ChatClient
from login_dialog import LoginDialog
from chat_window import ChatWindow


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    client = ChatClient()
    chat_window = ChatWindow(client)

    if LoginDialog(client).exec_() == QtGui.QDialog.Accepted:
        chat_window.update_display()
        chat_window.show()
        sys.exit(app.exec_())
