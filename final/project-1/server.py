# imports
import socket
import threading
import string
import re
import os

# constants
IP = socket.gethostbyname(socket.gethostname())
PORT = 4433
users = []


def check_if_message_contains_file(message: string):
    if re.findall(r'(\/.*?\.[\w:]+)', string):
        return True
    return False


def read_file(file):
    with open(file, 'rb') as f:
        data = f.read()
    return data


def write_data(data, filename):
    path = os.path.join(os.getcwd(), 'downloads', filename)
    with open(path, 'wb+') as f:
        f.write(data)


def receive_messages(client: socket.socket, username: string):
    while True:
        message = client.recv(2048).decode('utf-8')
        if message != '':
            if os.path.isfile(message):
                filename = os.path.basename(message)
                msg = username + '>' + filename
                data = read_file(message)
                write_data(data, filename)
                broadcast_msg(msg)
            else:
                msg = username + '>' + message
                broadcast_msg(msg)
        else:
            print("[!] message is empty")


def send_msg(client: socket.socket, message: string):
    client.sendall(message.encode())


def broadcast_msg(message: string):
    for user in users:
        send_msg(user[1], message)


def handle_clients(client: socket.socket):
    while True:
        username = client.recv(2048).decode('utf-8')
        if username != '':
            users.append((username, client))
            prompt_message = "admin>" + f"{username} added to the chat"
            broadcast_msg(prompt_message)
            break
        else:
            print("[!] no user joined the chat yet")
    threading.Thread(target=receive_messages, args=(client, username,)).start()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((IP, PORT))
        print(f"[/] server is running {IP}:{PORT}")
    except ConnectionError as e:
        print("[!] unable to make connection")
    server.listen(5)

    while True:
        client, address = server.accept()
        print(f"connection made with {address[0]}:{address[1]}")
        threading.Thread(target=handle_clients, args=(client,)).start()


if __name__ == '__main__':
    main()
