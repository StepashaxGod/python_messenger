# instead of browser get to server, wrote a client that doese the get and asks for a file, then recieves the file 

import socket 

host = "127.0.0.1"
port = 8000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

get_file = "GET /HelloWorld.html HTTP/1.1\r\nHost:localhost:8000\r\n\r\n" # valid get
client.send(get_file.encode())

recieved_msg = client.recv(4096).decode() # recieve 200 OK and file 

print(recieved_msg)

client.close() 



