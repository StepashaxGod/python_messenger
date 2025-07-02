# ******************************************************************************
# 
#  File       : utils.py
#  Author     : Stepan Nikonov
#  Created on : 2025-06-05
# 
#  Description: file provides additional functionality for client.
#               File needed for client for proper start.    
# ******************************************************************************

# All imports are default, the documentation can be found in the official python docks.

import logging
import json
import base64 # turned out to be twice as fast then ascii, or other manual approaches.
import os
import socket

# one-shot configuration
# set up logging
def setup_logging():
    logging.basicConfig(    
        filename="messenger.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# load configuration from config.json
def load_config(): 
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return {"server": {"host": "0.0.0.0", "port": 4444}} # my server listens to all intefaces  

# encode a file to a base64 string
def encode_file_to_base64(file_path):    
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        logging.error(f"Error encoding file {file_path}: {e}")
        return ""
    
# decode a base64 string to a file and open it
def decode_base64_to_file(base64_data, output_path):
    try:
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(base64_data))
        os.system(f"open \"{output_path}\"") 
    except Exception as e:
        logging.error(f"Error decoding file {output_path}: {e}")
