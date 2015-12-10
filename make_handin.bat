c:\python27\scripts\pyinstaller -w -F -i src\img\claptrap.ico src\chat_client_gui.py
c:\python27\scripts\pyinstaller -c -F -i src\img\claptrap.ico src\chat_server.py

mkdir submit
mkdir submit\src
mkdir submit\img

copy src\* submit\src\*
copy src\img\claptrap.ico submit\img\
copy src\globals.txt submit\
copy dist\chat_client_gui.exe submit\
copy dist\chat_server.exe submit\
copy doc\report.pdf submit\

pause