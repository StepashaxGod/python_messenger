# create server that handles 1 http request at a time
# accept + parse http request 
# get requestd file from servers local file system
# create http response message (request file + header lines) and send them back
# model => client asks server for a file; server sends back the file with message
# if no requested file server send 404 not found

from socket import *
import sys 

host = "127.0.0.1"
port = 8000

server = socket(AF_INET, SOCK_STREAM)
server.bind((host, port))
server.listen(1)
print("Ready to serve...")

while True:
   print("connected")
   conn, addr = server.accept()

   try:
      message = conn.recv(1024).decode()
      filename = message.split()[1]
      f = open(filename[1:])

      outputdata = f.read()

      conn.send("HTTP/1.1 200 OK\r\n\r\n".encode())

      conn.sendall(outputdata.encode()) 
      conn.send("\r\n".encode())   

      conn.close()

   except IOError:
      conn.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())

      conn.close()







