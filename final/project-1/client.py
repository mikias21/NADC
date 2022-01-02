import pickle
import socket
import struct
import threading
import string
import tkinter as tk
import tkinter.scrolledtext as scr_text
import tkinter.messagebox as msg_box
from tkinter import *
from tkinter import filedialog
import cv2

# constants
IP = '192.168.118.1'
PORT = 4433
font = ("Terminal", 13)

# client socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def show_message(message: string):
    m_box.config(state=tk.NORMAL)
    m_box.insert(tk.END, message + '\n')
    m_box.config(state=tk.DISABLED)


def file_upload_action(event=None):
    file = filedialog.askopenfilename(title='select file', filetypes=(("Text files", "*.txt*"), ("Tll files", "*.*")))
    m_textbox.insert(0, file)


def video_call_request():
    video_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 4434
    video_client.connect((IP, port))

    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        while len(data) < payload_size:
            packet = video_client.recv(4 * 1024)
            if not packet: break
            data += packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]
        while len(data) < msg_size:
            data += video_client.recv(4 * 1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow('VideoCall', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if cv2.getWindowProperty('VideoCall', 4) < 1:
            break
    video_client.close()


def connect():
    try:
        client.connect((IP, PORT))
        print("[/] connection success")
        show_message("admin$~ connection success")
    except ConnectionError as e:
        msg_box.showerror("error", "unable to make connection")
    username = u_textbox.get()
    if username != '':
        client.sendall(username.encode())
    else:
        msg_box.showerror("error", "username is empty")
    threading.Thread(target=listen_for_messages_from_server, args=(client,)).start()
    u_textbox.config(state=tk.DISABLED)
    u_button.config(state=tk.DISABLED)


def send_message():
    message = m_textbox.get()
    if message != '':
        client.sendall(message.encode())
        m_textbox.delete(0, len(message))
    else:
        msg_box.showerror("error", "message is empty")


# UI setup
root = tk.Tk()
root.geometry("800x600")
root.title("NPU internal chat application")
logo = PhotoImage(file="./assets/img/logo.png")
root.iconphoto(False, logo)
root.resizable(False, False)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)
# Frames
t_frame = tk.Frame(root, width=600, height=100, bg="#464EB8")
t_frame.grid(row=0, column=0, sticky=tk.NSEW)
m_frame = tk.Frame(root, width=600, height=400, bg="#0f1a29")
m_frame.grid(row=1, column=0, sticky=tk.NSEW)
b_frame = tk.Frame(root, width=600, height=100, bg="#464EB8")
b_frame.grid(row=2, column=0, sticky=tk.NSEW)
# components
u_label = tk.Label(t_frame, text="Username", font=font, bg="#464EB8", fg="white")
u_label.pack(side=tk.LEFT, padx=10)
u_textbox = tk.Entry(t_frame, font=font, bg="white", fg="black", width=23)
u_textbox.pack(side=tk.LEFT)
u_button = tk.Button(t_frame, text="Join Chat", font=font, bg="#0f2642", fg="white", command=connect)
u_button.pack(side=tk.LEFT, padx=25)

m_textbox = tk.Entry(b_frame, font=font, bg="white", fg="black", width=38)
m_textbox.pack(side=tk.LEFT, padx=10)
m_button = tk.Button(b_frame, text="Send", font=font, bg="#0f2642", fg="white", command=send_message)
m_button.pack(side=tk.LEFT, padx=10)

f_button = tk.Button(b_frame, text="File", font=font, bg="#0f2642", fg="white", command=file_upload_action)
f_button.pack(side=tk.LEFT, padx=15)

v_button = tk.Button(b_frame, text="Video", font=font, bg="#0f2642", fg="white", command=video_call_request)
v_button.pack(side=tk.LEFT, padx=20)

m_box = scr_text.ScrolledText(m_frame, font=font, bg="#0f1a29", fg="white", width=67, height=26.5)
m_box.config(state=tk.DISABLED)
m_box.pack(side=tk.TOP)


def listen_for_messages_from_server(i_client: socket.socket):
    while True:
        message = i_client.recv(2048).decode('utf-8')
        if message != '':
            username = message.split('>')[0]
            content = message.split('>')[1]
            show_message(f"{username}$~ {content}")
        else:
            msg_box.showerror("error", "no message received")


# main function
def main():
    root.mainloop()


if __name__ == '__main__':
    main()
