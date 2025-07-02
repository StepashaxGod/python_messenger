# ******************************************************************************
# 
#  File       : server.py
#  Author     : Stepan Nikonov
#  Created on : 2025-06-05
# 
#  Description: File that provides Server, which connects end users.    
#               Messages are handeled by the server using messageHandler, which routes each message
#               based on its type field to appropriate method.
# ******************************************************************************

# All imports are defalault, the documentation can be found in the official python docks.

import socket
import threading
import json
import logging
from message_handler import MessageHandler
from utils import setup_logging, load_config


# evrything applies to the instance of the class. 
class Server:
    # initialising Server  
    def __init__(self, host, port):
        self.host = host    # server host(ip adress)
        self.port = port    # server port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # server socket 
        self.clients = {}  # {username: socket}
        self.message_handler = MessageHandler() # instance of MessageHandler
    # start the server and listen for connections
    def start(self):
        setup_logging()
        try:
            # creating server, enabling server to listen
            self.server_socket.bind((self.host, self.port)) 
            self.server_socket.listen()
            logging.info(f"Server started on {self.host}:{self.port}")
            while True:
                # returning client socket, initialising thread for him.
                client_socket, addr = self.server_socket.accept() 
                threading.Thread(target=self.handle_client, args=(client_socket, addr)).start() # handle_cleint is called and thread is initialised. 
        except Exception as e:
            logging.error(f"Server startup error: {e}")
            self.server_socket.close()

    # handles data from user within a connection.
    # handle a client connection
    def handle_client(self, client_socket, addr):
        username = None
        try:
            # ensuring successful registration
            data = client_socket.recv(1024).decode()
            init = json.loads(data)
            if init.get("type") != "init" or not init.get("username"):
                client_socket.send(json.dumps({"type": "error", "payload": "Invalid init message"}).encode())
                client_socket.close()
                return
            username = init["username"]  # recieved the username 
            if username in self.clients: # if username is a duplicate.
                client_socket.send(json.dumps({"type": "error", "payload": "Username already taken"}).encode())
                client_socket.close()
                return
            self.clients[username] = client_socket # dictionary of users {username: socket }
            logging.info(f"Client {username} connected from {addr}")
            client_socket.send(json.dumps({"type": "status", "payload": "Registration successful"}).encode())

            # always recieves from the registered user 
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                try:
                    message = json.loads(data)                  # data recieved from user in json format, makes it a dict
                    if message.get("type") == "online_users":   # if asks for online_users send him
                        self.handle_online_users(message, client_socket)
                    else:
                        # processes the initial messages after the registration
                        # as input: data from user, dict of users 
                        self.message_handler.process_message(message, self.clients) # 
                except Exception as e:
                    logging.error(f"Error processing message from {username}: {e}")
        except Exception as e:
            logging.error(f"Error handling client {username}: {e}")
        finally: # deletes client
            if username in self.clients: 
                del self.clients[username]
                client_socket.close()
                logging.info(f"Client {username} disconnected")

    # send the list of online users
    def handle_online_users(self, message, client_socket):
        
        try:
            users = list(self.clients.keys())
            response = json.dumps({"type": "online_users", "users": users})
            client_socket.send(response.encode())
            logging.info(f"Sent online users list to {message['from']}: {users}")
        except Exception as e:
            logging.error(f"Error sending user list: {e}")    

if __name__ == "__main__": 
    # initialisng an instance of the server with provided parameters from the config.json
    config = load_config() 
    server = Server(config["server"]["host"], config["server"]["port"]) 
    server.start()  