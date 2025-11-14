import socket
import json
import logging
from datetime import datetime
from pymongo import MongoClient

import config


def setup_mongo_client():
    try:
        client = MongoClient(config.MONGO_URI)
        db = client[config.DB_NAME]
        collection = db[config.COLLECTION_NAME]
        logging.info("З'єднання з MongoDB встановлено успішно.")
        return collection
    except Exception as e:
        logging.error(f"Не вдалося підключитися до MongoDB: {e}")
        return None


def run_socket_server(server_socket, mongo_collection):
    if mongo_collection is None:
        logging.error("Socket-сервер не може запуститися без з'єднання з MongoDB.")
        return

    while True:
        try:
            data, addr = server_socket.recvfrom(1024)
            data_dict = json.loads(data.decode("utf-8"))

            message_to_save = {
                "date": str(datetime.now()),
                "username": data_dict.get("username"),
                "message": data_dict.get("message"),
            }

            mongo_collection.insert_one(message_to_save)
            logging.info(
                f"Отримано та збережено повідомлення від {addr}: {message_to_save}"
            )

        except json.JSONDecodeError:
            logging.error(f"Отримано пошкоджені дані від {addr}")
        except Exception as e:
            logging.error(f"Помилка в роботі Socket-сервера: {e}")


def start_server():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((config.SOCKET_HOST, config.SOCKET_PORT))
    logging.info(f"Socket-сервер запущено на {config.SOCKET_HOST}:{config.SOCKET_PORT}")

    mongo_collection = setup_mongo_client()

    run_socket_server(server_socket, mongo_collection)


if __name__ == "__main__":
    start_server()
