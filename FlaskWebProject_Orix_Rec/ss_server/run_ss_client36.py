import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # サーバを指定
    s.connect(('172.31.19.115', 50007))
    # サーバにメッセージを送る
    #s.sendall(b'1234567')
    #s.sendall(b'0')
    s.sendall(b'15686')
    # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
    data = s.recv(1024)
    #
    print(repr(data))
