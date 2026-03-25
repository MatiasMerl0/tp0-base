import signal
import socket
import logging

from .protocol import send_message, receive_message
from .lottery import Lottery


class Server:
    def __init__(self, port, listen_backlog):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._running = True
        self._lottery = Lottery()

        signal.signal(signal.SIGTERM, self._sigterm_handler)

    def _sigterm_handler(self, sig, frame):
        logging.info("action: sigterm_received | result: success")
        self._running = False
        self._server_socket.close()

    def run(self):
        while self._running:
            try:
                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
            except OSError:
                break

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
