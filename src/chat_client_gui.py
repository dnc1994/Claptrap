# -*- encoding:utf-8 -*-
import sys
from PyQt4 import QtGui
from login_dialog import LoginDialog
from chat_window import ChatWindow


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    chat_window = ChatWindow()

    if LoginDialog(chat_window).exec_() == QtGui.QDialog.Accepted:
        print 'login OK, show UI'
        chat_window.init_ui()
        chat_window.show()
        sys.exit(app.exec_())
