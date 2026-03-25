import logging

from .utils import Bet, store_bets


class Lottery:
    # Parse the message and process the batch of bets.
    def handle_message(self, msg):
        fields = msg.split('\n')
        msg_type = fields[0]

        if msg_type != 'BATCH':
            logging.error(f'action: handle_message | result: fail | error: unknown message type {msg_type}')
            return 'ERR'

        agency = fields[1]
        count = int(fields[2])
        bets = []
        for i in range(count):
            parts = fields[3 + i].split(',')
            bets.append(Bet(agency, parts[0], parts[1], parts[2], parts[3], parts[4]))
        store_bets(bets)
        logging.info(f'action: apuesta_recibida | result: success | cantidad: {count}')
        return 'OK'
