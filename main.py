import logging
from multiprocessing import Process

from http_server import run_http_server
from socket_server import start_server


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(processName)s - %(levelname)s - %(message)s",
    )

    http_process = Process(target=run_http_server, name="HTTPServerProcess")
    socket_process = Process(target=start_server, name="SocketServerProcess")

    logging.info("Запуск HTTP-сервера...")
    http_process.start()

    logging.info("Запуск Socket-сервера...")
    socket_process.start()

    http_process.join()
    socket_process.join()


if __name__ == "__main__":
    main()
