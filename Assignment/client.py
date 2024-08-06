import socket
import time
import logging

class Client:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client_socket = None
        self.logger = logging.getLogger('client')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.FileHandler('client.log'))

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
        except socket.error as e:
            self.logger.error(f'Socket error: {e}')

    def send_query(self, query: str):
        try:
            self.client_socket.sendall(query.encode())
        except socket.error as e:
            self.logger.error(f'Socket error: {e}')

    def receive_response(self):
        try:
            response = self.client_socket.recv(1024).decode()
            return response
        except socket.error as e:
            self.logger.error(f'Socket error: {e}')

    def close(self):
        self.client_socket.close()

if __name__ == '__main__':
    client = Client('localhost', 8080)
    client.connect()
    query = 'test query'
    client.send_query(query)
    response = client.receive