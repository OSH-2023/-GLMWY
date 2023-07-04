from receive_file import receive_file
from send_file import send_file
from threading import Thread
import queue
import socket
from EC_module import erasure
from Ray_Module import ray_control
import os

message_queue = queue.Queue()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

web_ip = 127.0.0.1
web_port = 10000

def listen():
    sock.bind((web_ip, web_port))
    sock.listen(1)
    print('等待连接')
    conn, addr = sock.accept()
    print('连接已建立: 'addr)
    buffer = conn.recv(4096)
    message = buffer.split(',')
    if message[0] == 'Upload':  # 上传：Upload,file_path/filename,content
        content = massage[2]
        with open(os.join.path('uploadfile',filename)) as file:
            while content:
                file.write(content)
                content = conn.recv(4096)
        message[1] = os.join.path('uploadfile',filename)
        message = message[0:1]
        message_queue.put(message)
    
    elif message[0] == 'Download':
        message_queue.put(message)

    elif message[0] == 'Remove':
        message_queue.put(message)
    return


def handle():
    while True:
        if message_queue.empty():
            pass
        else:
            message = message_queue.get()
            if message[0] == 'Upload':
                message[1] == message[1].replace('/','_')
                if fileupload(message[1]):
                    print('upload success')
            elif message[0] == 'Download':
                message[1] == message[1].replace('/','_')
                if filedownload(message[1]):
                    print('download success')

            elif message[0] == 'Remove':
                message[1] == message[1].replace('/','_')
                if remove(message[1]):
                    print('remove success')

            else:
                raise Exception('未定义操作')


def fileupload(file_path):
    if erasure('Upload'+','+file_path) is False:
        print('存储模块错误')
        return False

    if ray_control('Upload'+','+file_path) is False:
        print('ray模块错误')
        return False

    if erasure('Commit') is False:
        print('存储模块错误')
        return False

    ray_control('Commit')

    return True


def filedownload(file_name):
    if erasure('Download'+','+file_path) is False:
        print('下载错误')
        return False
    file_path = os.path.join('Download',file_name))
    
    # 连接目标主机
    sock.connect((web_ip, web_port))
    # 打开要发送的文件
    with open(file_path, 'rb') as file:
        # 读取文件内容
        data = file.read()
        # 发送文件数据
        sock.sendall(data)
    print("文件发送完成")
    sock.close()
    return True


def remove(file_path):
    if erasure('Remove'+file_path) is False:
        print('存储模块错误')
        return False

    if ray_control('Remove'+file_path) is False:
        print('ray模块错误')
        return False

    if erasure('Commit') is False:
        print('存储模块错误')
        return False

    if ray_control('Commit') is False:
        print('ray commit error')
        return False

    return True


if __name__ == "__main__":
    listen_thread = Thread(target=listen)
    handle_thread = Thread(target=handle)
    listen_thread.start()
    handle_thread.start()
    listen_thread.join()
    handle_thread.join()
