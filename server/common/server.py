import signal
import socket
import logging

from .protocol import send_message, receive_message
from .utils import Bet, store_bets


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._running = True

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
            msg = receive_message(client_sock)
            fields = msg.split('\n')

            if fields[0] != 'BET':
                send_message(client_sock, 'ERR')
                return

            bet = Bet(fields[1], fields[2], fields[3], fields[4], fields[5], fields[6])
            store_bets([bet])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
            send_message(client_sock, 'OK')
        except Exception as e:
            logging.error(f'action: apuesta_almacenada | result: fail | error: {e}')
            try:
                send_message(client_sock, 'ERR')
            except Exception: # We try/except because the error may have been a connection error.
                pass
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
