import socket
import os
from thread import *

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 7000
ThreadCount = 0
try:
    ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(5)


def threaded_client(connection):
    while True:
        data = connection.recv(2048)
        reply = 'Server Says: ' + data
        if not data:
            break
        connection.sendall(reply)
    connection.close()

while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()