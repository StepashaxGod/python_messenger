# ******************************************************************************
# 
#  File       : message_handler.py
#  Author     : Stepan Nikonov
#  Created on : 2025-06-05
# 
#  Description: MessageHandler helps the server to precoess messages of a certain "type".
#                
# ******************************************************************************

# All imports are default, the documentation can be found in the official python docks.

import json
import logging

class MessageHandler:
    # process the initial messages after the registration, redirects them to the specific function based on the type 
    # process an incoming message
    def process_message(self, message, clients):
        try:
            msg_type = message.get("type")
            if msg_type == "message": # then handle_text_message
                self.handle_text_message(message, clients)
            elif msg_type == "file":
                self.handle_file_message(message, clients)
            elif msg_type == "contact":
                self.handle_contact_update(message, clients)
            else:
                logging.warning(f"Unknown message type: {msg_type}")
        except Exception as e:
            logging.error(f"Error processing message: {e}")

    # forward a text message
    def handle_text_message(self, message, clients):
        try:
            # looks for the recipinet in clinets and sends 
            # replies wtih status 
            # logs 
            recipient = message["to"]
            if recipient in clients:
                clients[recipient].send(json.dumps(message).encode())
                self.send_status(message["from"], recipient, "delivered", clients)
                logging.info(f"Message from {message['from']} to {recipient} delivered")
            else:
                self.send_status(message["from"], recipient, "offline", clients)
                logging.warning(f"Recipient {recipient} is offline")
        except Exception as e:
            logging.error(f"Error delivering message: {e}")

    # forward a file
    def handle_file_message(self, message, clients):
        try:
            recipient = message["to"]
            if recipient in clients:
                clients[recipient].send(json.dumps(message).encode())
                self.send_status(message["from"], recipient, "delivered", clients)
                logging.info(f"File from {message['from']} to {recipient} delivered")
            else:
                self.send_status(message["from"], recipient, "offline", clients)
                logging.warning(f"Recipient {recipient} is offline")
        except Exception as e:
            logging.error(f"Error delivering file: {e}")

    # handle a contact update
    def handle_contact_update(self, message, clients):
        try:
            recipient = message["to"]
            if recipient in clients:
                clients[recipient].send(json.dumps(message).encode())
                self.send_status(message["from"], recipient, f"{message['action']} successful", clients)
                logging.info(f"Contact update from {message['from']} to {recipient} delivered")
            else:
                self.send_status(message["from"], recipient, "offline", clients)
                logging.warning(f"Recipient {recipient} is offline")
        except Exception as e:
            logging.error(f"Error handling contact update: {e}")
            
    # send a status notification
    def send_status(self, sender, recipient, status, clients):
        try:
            status_msg = json.dumps({
                "type": "status",
                "from": "server",
                "to": sender,
                "payload": f"Message to {recipient} {status}"
            })
            if sender in clients:
                clients[sender].send(status_msg.encode())
                logging.info(f"Sent status notification to {sender}: {status}")
        except Exception as e:
            logging.error(f"Error sending status: {e}")