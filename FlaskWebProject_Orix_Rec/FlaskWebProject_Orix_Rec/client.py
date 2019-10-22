
import socket

inst = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
inst.sendto(b'Hello UDP', ('127.0.0.1', 50007))