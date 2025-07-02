# ******************************************************************************
# 
#  File       : client.py
#  Author     : Stepan Nikonov
#  Created on : 2025-06-05
# 
#  Description: File serves as a representation of a user and its abilities.
#               User gets this scrip along with  in order to communicate. 
# ******************************************************************************

# All imports are default, the documentation can be found in the official python docks.

import socket 
import threading
import json 
import logging 
import os 
from utils import setup_logging, load_config, encode_file_to_base64, decode_base64_to_file

class Client:
    # initialising Client 
    def __init__(self, host, port):   
        self.host = host      # connection host(servers ip adress)
        self.port = port      # connection port(servers port)    
        self.username = None  # username   
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # default TCP stream
        self.contacts = set() # list with users
        self.running = True   # otherwise saying - while connected

    # connect to the server
    def connect(self):
        try:
            # user connects and sends username(json format) within running thread
            # depends on how u run the server, the connection might vary 
            self.client_socket.connect((self.host, self.port)) 
            self.username = input("Enter your username: ")
            init_message = json.dumps({"type": "init", "username": self.username}) # serialises object to a json formatted string
            self.client_socket.send(init_message.encode())
            threading.Thread(target=self.receive_messages).start() # user is given a thread and he recieves messages 

        except Exception as e:
            logging.error(f"Connection error: {e}")
            self.client_socket.close()

    # receive messages from the server
    def receive_messages(self):
        while self.running:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break 
                # everything is handeled by json and the "type" field. 
                # have to check type for correct execution of a query
                message = json.loads(data) 
                if message.get("type") == "message":
                    print(f"{message['from']}: {message['payload']}")
                elif message.get("type") == "file":
                    decode_base64_to_file(message["payload"], f"received_{message['filename']}")
                    print(f"File {message['filename']} received and saved as received_{message['filename']}")
                elif message.get("type") == "contact":
                    print(f"Contact {message['from']} {message['action']} you in their list")
                elif message.get("type") == "online_users":
                    print(f"Online users: {', '.join(message['users'])}")
                elif message.get("type") == "status":
                    print(f"Status: {message['payload']}")
                elif message.get("type") == "error":
                    print(f"Error: {message['payload']}")
            except Exception as e:
                logging.error(f"Error receiving message: {e}")
                break

    # send a text message
    def send_message(self, recipient, text):
        try:
            msg = json.dumps({"type": "message", "from": self.username, "to": recipient, "payload": text})
            self.client_socket.send(msg.encode())
            logging.info(f"Sent message to {recipient}: {text}")
        except Exception as e:
            logging.error(f"Error sending message: {e}")

    # send a file
    def send_file(self, recipient, file_path):
        try:
            if not os.path.exists(file_path):
                print("File not found")
                return
            base64_data = encode_file_to_base64(file_path)
            msg = json.dumps({
                "type": "file",
                "from": self.username,
                "to": recipient,
                "filename": os.path.basename(file_path),
                "payload": base64_data
            })
            self.client_socket.send(msg.encode())
            logging.info(f"Sent file {file_path} to {recipient}")
        except Exception as e:
            logging.error(f"Error sending file: {e}")

    # add a contact
    def add_contact(self, contact):
        try:
            self.contacts.add(contact)
            msg = json.dumps({
                "type": "contact",
                "from": self.username,
                "to": contact,
                "action": "add",
                "contact": contact
            })
            self.client_socket.send(msg.encode())
            logging.info(f"Contact {contact} added")
            print(f"Contact {contact} added")
        except Exception as e:
            logging.error(f"Error adding contact: {e}")
            
    # remove a contact
    def remove_contact(self, contact):
        try:
            self.contacts.discard(contact)
            msg = json.dumps({
                "type": "contact",
                "from": self.username,
                "to": contact,
                "action": "remove",
                "contact": contact
            })
            self.client_socket.send(msg.encode())
            logging.info(f"Contact {contact} removed")
            print(f"Contact {contact} removed")
        except Exception as e:
            logging.error(f"Error removing contact: {e}")

    # show the contact list
    def list_contacts(self):
        if self.contacts:
            print("Your contacts:", ", ".join(self.contacts))
        else:
            print("Contact list is empty")

    # request the list of online users
    def request_online_users(self):
        try:
            msg = json.dumps({"type": "online_users", "from": self.username, "action": "request"})
            self.client_socket.send(msg.encode())
            logging.info("Requested online users list")
        except Exception as e:
             logging.error(f"Error requesting user list: {e}")

    # after the successful registration the cleint gets access to methods.
    # run the client interface
    def run(self):
        self.connect()
        while self.running:
            try:
                command = input("Enter command (send/file/add_contact/remove_contact/list_contacts/list_users/exit): ")
                if command == "send":
                    recipient = input("To: ")
                    text = input("Message: ")
                    self.send_message(recipient, text)
                elif command == "file":
                    recipient = input("To: ")
                    file_path = input("File path: ")
                    self.send_file(recipient, file_path)
                elif command == "add_contact":
                    contact = input("Contact name: ")
                    self.add_contact(contact)
                elif command == "remove_contact":
                    contact = input("Contact name: ")
                    self.remove_contact(contact)
                elif command == "list_contacts":
                    self.list_contacts()
                elif command == "list_users":
                    self.request_online_users()
                elif command == "exit":
                    self.running = False
                    self.client_socket.close()
                    break
            except Exception as e:
                logging.error(f"Command error: {e}")
                break

if __name__ == "__main__":
    # initialising client with data provided in the config.json
    setup_logging()
    config = load_config() 
    client = Client(config["server"]["host"], config["server"]["port"])
    client.run()