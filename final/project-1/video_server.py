import socket
import cv2
import pickle
import struct

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = socket.gethostbyname(socket.gethostname())
PORT = 4434

server.bind((IP, PORT))
server.listen(5)
print(f"[/]server is listening on {IP}:{PORT}")

while True:
    client, address = server.accept()
    if client:
        video = cv2.VideoCapture(0)
        while video.isOpened():
            image, frame = video.read()
            a = pickle.dumps(frame)
            message = struct.pack("Q", len(a)) + a
            client.sendall(message)
            cv2.imshow('Ongoing Video Call', frame)
            key = cv2.waitKey(1) & 0xFF
            if key ==  ord('q'):
                client.close()