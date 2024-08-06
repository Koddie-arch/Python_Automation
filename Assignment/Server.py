import socket
import ssl
import threading
import configparser
import os
import time
import logging

class Server:
    def __init__(self, config_file: str):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.path = self.config.get('linuxpath')
        self.reread_on_query = self.config.getboolean('REREAD_ON_QUERY')
        self.ssl_enabled = self.config.getboolean('SSL_ENABLED')
        self.ssl_cert = self.config.get('SSL_CERT')
        self.ssl_key = self.config.get('SSL_KEY')
        self.max_connections = self.config.getint('MAX_CONNECTIONS')
        self.timeout = self.config.getint('TIMEOUT')
        self.server_socket = None
        self.logger = logging.getLogger('server')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.FileHandler('server.log'))

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 8080))
        self.server_socket.listen(self.max_connections)
        self.logger.info('Server started. Listening on port 8080...')

        if self.ssl_enabled:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(self.ssl_cert, self.ssl_key)
            self.server_socket = context.wrap_socket(self.server_socket, server_side=True)

        while True:
            try:
                client_socket, address = self.server_socket.accept()
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket, address))
                client_handler.start()
            except socket.error as e:
                self.logger.error(f'Socket error: {e}')

    def handle_client(self, client_socket: socket.socket, address: tuple):
        start_time = time.time()
        try:
            client_socket.settimeout(self.timeout)
            query = client_socket.recv(1024).decode().strip('\x00')
            self.logger.info(f'Received query "{query}" from {address[0]}')

            if self.reread_on_query:
                with open(self.path, 'r') as file:
                    lines = file.readlines()
            else:
                if not hasattr(self, 'lines'):
                    with open(self.path, 'r') as file:
                        self.lines = file.readlines()

            result = 'STRING EXISTS' if query + '\n' in self.lines else 'STRING NOT FOUND'
            client_socket.sendall(result.encode() + b'\n')
            self.logger.info(f'Sent response "{result}" to {address[0]} in {time.time() - start_time:.2f}ms')
        except socket.error as e:
            self.logger.error(f'Socket error: {e}')
        except Exception as e:
            self.logger.error(f'Error: {e}')
        finally:
            client_socket.close()

    def close(self):
        self.server_socket.close()

if __name__ == '__main__':
    server = Server('config.ini')
    try:
        server.start()
    except KeyboardInterrupt:
        server.close()