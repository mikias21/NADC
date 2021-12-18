# Author : Mikias Berhanu
# Date : 18/12/2021

import socket
import select


class Server:
    """
        This class is responsible for the server logic
        initializes the server socket
        binds the local host port with port 7777
        accepts incoming connections from other computers or networks
    """
    def __init__(self):
        self.header_length = 10
        self.ip = "127.0.0.1"
        self.port = 45678
        self.server_socket = None
        self.socket_list = [self.server_socket]
        self.users = {}

    def init_server_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen()
        print(f"server is listening on port {self.ip}:{self.port}")
        return self.server_socket

    def receive_client_messages(self, client_socket: socket.socket):
        try:
            message_header = client_socket.recv(self.header_length)
            if not len(message_header):  # if there is not message
                return False
            # get the length and receive message based on the message length not more than that
            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': client_socket.recv(message_length)}
        except:
            return False


if __name__ == '__main__':
    # Program Loop
    # keep listening and accepting connections
    server = Server()
    server_socket = server.init_server_socket()
    socket_list = [server_socket]
    users = {}
    while True:
        incoming_sockets, _, exception_sockets = select.select(socket_list, [], socket_list)
        for n_socket in incoming_sockets:
            if n_socket == server_socket:  # check if the incoming socket is server socket
                c_socket, c_address = server_socket.accept()
                client = server.receive_client_messages(c_socket)
                if not client:
                    continue
                socket_list.append(c_socket)
                users[c_socket] = client
                print('[*][*]new connection from {}:{}, username: {}'.format(*c_address, client['data'].decode('utf-8')))
            else: # a client from our list is sending message
                c_message = server.receive_client_messages(n_socket)
                if not c_message:  # check if there is a client message no client connected
                    print('[-][-]unable to make connection')
                    socket_list.remove(n_socket)
                    del users[n_socket]
                    continue
                client = users[n_socket] # get the user who is sending message
                print(f'Received message from {client["data"].decode("utf-8")}: {c_message["data"].decode("utf-8")}')
                for c_socket in users:  # for users in our list broadcast message
                    if c_socket != n_socket:
                        c_socket.send(client['header'] + client['data'] + c_message['header'] + c_message['data'])

        # handle socket exceptions
        for n_socket in exception_sockets:
            socket_list.remove(n_socket)
            del users[n_socket]