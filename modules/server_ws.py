import socket
import json
import logging
from threading import Thread
from pymongo.mongo_client import MongoClient  # pip install pymongo
from pymongo.server_api import ServerApi      # pip install pymongo

from variables import *


def save_to_db(data):
    client = MongoClient(config.get("MONGODB_URI", "mongodb://localhost:27017"), server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        db = client[config.get("MONGODB_NAME", "database")]
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        return;

    collection = config.get("MONGODB_COLLECTION", "collection")
    try:
        logging.info(f"Saving {data} to MongoDB")
        db[collection].insert_one(data)
    except Exception as e:
        logging.error(f"Error saving data to MongoDB: {e}")
    return


def start_ws_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            port_ws = int(config.get("WS_PORT", 5000))
            host_ws = config.get("WS_HOST", "")
            s.bind((host_ws, port_ws))
            s.listen()
            logging.info(f"Socket Server started at ws://{host_ws if host_ws else '*'}:{port_ws}")
            while True:
                conn, addr = s.accept()
                with conn:
                    handshake = conn.recv(32).decode()
                    if not handshake or config.get("WS_SECRET", "secret") != handshake:
                        break
                    conn.send(config.get("WS_ACK", "secret").encode())
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    data = json.loads(data)
                    data['message'] = data['message'].replace("+", " ").strip()
                    data['username'] = data['username'].replace("+", " ")
                logging.info(f"Received {data}")
                Thread(target=save_to_db, args=(data,)).start()

    except KeyboardInterrupt:
        logging.info("Stopping socket server")
    finally:
        logging.warning('Socket server closed')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    start_ws_server()
# else:
    # from main import config
