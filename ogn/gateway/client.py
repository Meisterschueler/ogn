import socket
import logging
from time import time

from ogn.gateway import settings
from ogn.aprs_parser import parse_aprs
from ogn.exceptions import AprsParseError, OgnParseError, AmbigousTimeError


def create_aprs_login(user_name, pass_code, app_name, app_version, aprs_filter=None):
    if not aprs_filter:
        return "user {} pass {} vers {} {}\n".format(user_name, pass_code, app_name, app_version)
    else:
        return "user {} pass {} vers {} {} filter {}\n".format(user_name, pass_code, app_name, app_version, aprs_filter)


class ognGateway:
    def __init__(self, aprs_user, aprs_filter=''):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Connect to OGN as {} with filter '{}'".format(aprs_user, (aprs_filter if aprs_filter else 'full-feed')))
        self.aprs_user = aprs_user
        self.aprs_filter = aprs_filter

    def connect(self):
        # create socket, connect to server, login and make a file object associated with the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        if self.aprs_filter:
            port = settings.APRS_SERVER_PORT_CLIENT_DEFINED_FILTERS
        else:
            port = settings.APRS_SERVER_PORT_FULL_FEED

        self.sock.connect((settings.APRS_SERVER_HOST, port))
        self.logger.debug('Server port {}'.format(port))

        login = create_aprs_login(self.aprs_user, -1, settings.APRS_APP_NAME, settings.APRS_APP_VER, self.aprs_filter)
        self.sock.send(login.encode())
        self.sock_file = self.sock.makefile('rw')

    def disconnect(self):
        self.logger.info('Disconnect')
        try:
            # close everything
            self.sock.shutdown(0)
            self.sock.close()
        except OSError:
            self.logger.error('Socket close error', exc_info=True)

    def run(self, callback, autoreconnect=False):
        self.process_beacon = callback

        while True:
            try:
                keepalive_time = time()
                while True:
                    if time() - keepalive_time > settings.APRS_KEEPALIVE_TIME:
                        self.logger.info('Send keepalive')
                        self.sock.send('#keepalive'.encode())
                        keepalive_time = time()

                    # Read packet string from socket
                    packet_str = self.sock_file.readline().strip()

                    # A zero length line should not be return if keepalives are being sent
                    # A zero length line will only be returned after ~30m if keepalives are not sent
                    if len(packet_str) == 0:
                        self.logger.warning('Read returns zero length string. Failure.  Orderly closeout')
                        break

                    self.proceed_line(packet_str)
            except BrokenPipeError:
                self.logger.error('BrokenPipeError', exc_info=True)
            except socket.error:
                self.logger.error('socket.error', exc_info=True)

            if autoreconnect:
                self.connect()
            else:
                return

    def proceed_line(self, line):
        try:
            beacon = parse_aprs(line)
            self.logger.debug('Received beacon: {}'.format(beacon))
        except AprsParseError:
            self.logger.error('AprsParseError while parsing line: {}'.format(line), exc_info=True)
            return
        except OgnParseError:
            self.logger.error('OgnParseError while parsing line: {}'.format(line), exc_info=True)
            return
        except AmbigousTimeError as e:
            self.logger.error('Drop packet, {:.0f}s from past: {}'.format(e.timedelta.total_seconds(), line))
            return

        if beacon is not None:
            self.process_beacon(beacon)
