import socket

ip = '127.0.0.1'
p1 = 7001
p2 = 7002
p3 = 7003

cport = input('Port: ')

ClientSocket = socket.socket()
ClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ClientSocket.bind((ip, cport))
host = '127.0.0.1'
port = 7000

print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

#Response = ClientSocket.recv(1024)
while True:
    Input = raw_input('Say Something: ')
    ClientSocket.send(Input)
    Response = ClientSocket.recv(1024)
    print(Response)

ClientSocket.close()