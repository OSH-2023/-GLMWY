import socket

# 上传：Upload,file_id,filename,content
# 下载：Download,file_id,filename
# 删除：Delete,file_id,filename

# sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

listen_ip = '0.0.0.0'
listen_port = 10000

central_ip = '172.16.74.89'
central_port = 9999


def upload_to_central(fileid, filename, file):
    sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_central.connect((central_ip, central_port))
        print('已连接到central server')
        content = file.read()
        print('content长度:', len(content))
        message = b'' + b'Upload,' + str(fileid).encode(
            'utf-8') + b',' + filename.encode('utf-8') + b',' + content
        sock_central.sendall(message)
        print('已发送上传命令')
        # sock_central.close()

        sock_listen.bind((listen_ip, listen_port))
        sock_listen.listen(5)
        print('等待central server连接')

        conn, addr = sock_listen.accept()
        print('已连接到central server')
        message = conn.recv(1024)
        print('已接收到central server的回复')
        # sock_listen.close()
        if message == b'Upload success':
            print('上传成功')
            return True
        elif message == b'Upload fail':
            print('上传失败')
            return False
        return False
    except OSError as e:
        print(e)
        print(type(sock_central))
        print(type(sock_listen))
    finally:
        print(type(sock_central))
        print(sock_central)
        print(type(sock_listen))
        sock_central.close()
        sock_listen.close()


def download_to_central(fileid, filename, file_path):
    sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_central.connect((central_ip, central_port))
        print('已连接到central server')
        message = b'' + b'Download,' + str(fileid).encode(
            'utf-8') + b',' + filename.encode('utf-8')
        sock_central.sendall(message)
        print('已发送下载命令')
        # sock_central.close()

        sock_listen.bind((listen_ip, listen_port))
        sock_listen.listen(5)
        print('等待central server连接')

        conn, addr = sock_listen.accept()
        print('已连接到central server')
        content = conn.recv(4096)
        if content.decode('utf-8') == 'download error':
            print('下载失败')
            return False
        print('已接收到central server的回复')

        with open(file_path, 'wb') as f:
            while content:
                f.write(content)
                content = conn.recv(4096)

        print('下载成功')

        return True

        # sock_listen.close()

    except OSError as e:
        print(e)
        print(type(sock_central))
        print(type(sock_listen))
    finally:
        print(type(sock_central))
        print(sock_central)
        print(type(sock_listen))
        sock_central.close()
        sock_listen.close()


def Delete_to_central(fileid, filename):
    sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_central.connect((central_ip, central_port))
        print('已连接到central server')
        message = b'' + b'Delete,' + str(fileid).encode(
            'utf-8') + b',' + filename.encode('utf-8')
        sock_central.sendall(message)
        print('已发送删除命令')
        # sock_central.close()

        sock_listen.bind((listen_ip, listen_port))
        sock_listen.listen(5)
        print('等待central server连接')

        conn, addr = sock_listen.accept()
        print('已连接到central server')
        message = conn.recv(1024)
        print('已接收到central server的回复')
        # sock_listen.close()
        if message == b'Delete success':
            print('删除成功')
            return True
        elif message == b'Delete fail':
            print('删除失败')
            return False
        return False
    except OSError as e:
        print(e)
        print(type(sock_central))
        print(type(sock_listen))
    finally:
        print(type(sock_central))
        print(sock_central)
        print(type(sock_listen))
        sock_central.close()
        sock_listen.close()