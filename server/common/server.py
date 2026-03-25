import signal
import socket
import logging
import threading

from .protocol import send_message, receive_message
from .lottery import Lottery


class Server:
    def __init__(self, port, listen_backlog, total_agencies):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._running = True
        self._lottery = Lottery(total_agencies)
        self._worker_threads = []

        signal.signal(signal.SIGTERM, self._sigterm_handler)

    def _sigterm_handler(self, sig, frame):
        logging.info("action: sigterm_received | result: success")
        self._running = False
        self._server_socket.close()

    def run(self):
        while self._running:
            try:
                client_sock = self.__accept_new_connection()
                worker = threading.Thread(target=self.__handle_client_connection, args=(client_sock,))
                worker.start()
                self._worker_threads.append(worker)
            except OSError:
                break

        for worker in self._worker_threads:
            worker.join(timeout=1)
        logging.info("action: close_server_socket | result: success")

    def __handle_client_connection(self, client_sock):
        try:
            while True:
                msg = receive_message(client_sock)
                response = self._lottery.handle_message(msg)
                send_message(client_sock, response)
        except ConnectionError: # Client closed connection
            pass
        except Exception as e:
            logging.error(f'action: handle_connection | result: fail | error: {e}')
            send_message(client_sock, 'ERR')
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
