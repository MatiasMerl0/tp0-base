import logging
import threading

from .utils import Bet, store_bets, load_bets, has_won


class Lottery:
    def __init__(self, total_agencies):
        self._total_agencies = total_agencies
        self._finished_agencies = set()
        self._lock = threading.Lock()

    def handle_message(self, msg):
        fields = msg.split('\n')
        msg_type = fields[0]

        if msg_type == 'BATCH':
            return self._handle_batch(fields[1:])
        elif msg_type == 'FINISHED':
            return self._handle_finished(fields[1])
        elif msg_type == 'WINNERS':
            return self._handle_winners(fields[1])

        logging.error(f'action: handle_message | result: fail | error: unknown message type {msg_type}')
        return 'ERR'

    def _handle_batch(self, fields):
        agency = fields[0]
        count = int(fields[1])
        bets = []
        for i in range(count):
            parts = fields[2 + i].split(',')
            bets.append(Bet(agency, parts[0], parts[1], parts[2], parts[3], parts[4]))
        with self._lock:
            store_bets(bets)
        logging.info(f'action: apuesta_recibida | result: success | cantidad: {count}')
        return 'OK'

    def _handle_finished(self, agency):
        should_log_sorteo = False
        with self._lock:
            self._finished_agencies.add(agency)
            should_log_sorteo = len(self._finished_agencies) == self._total_agencies
        logging.info(f'action: finished | result: success | agency: {agency}')
        if should_log_sorteo:
            logging.info('action: sorteo | result: success')
        return 'OK'

    def _handle_winners(self, agency):
        with self._lock:
            if len(self._finished_agencies) < self._total_agencies:
                return 'NOT_READY'
            winners = [bet.document for bet in load_bets() if bet.agency == int(agency) and has_won(bet)]
        return ','.join(winners)
