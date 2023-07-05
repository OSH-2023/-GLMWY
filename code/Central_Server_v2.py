from threading import Thread
import queue
import socket
from EC_Module import erasure_control
from Ray_Module import ray_control
import os

message_queue = queue.Queue()

sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_web = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

listen_ip = '0.0.0.0'
listen_port = 10000

web_ip = '192.168.8.132'
web_port = 9999

def listen():
    sock_listen.bind((listen_ip, listen_port))
    sock_listen.listen(1)
    print('等待连接')
    while True:
        conn, addr = sock_listen.accept()
        print('连接已建立: ',addr)

        buffer = conn.recv(4096)
        message = buffer.decode('utf-8').split(',')
        print('收到命令：')
        print(message)

        if message[0] == 'Upload':  # 上传：Upload,file_id,filename,content
            content = message[3]
            file_name = message[2]

            with open(os.path.join('uploadfile',file_name)) as file:
                while content:
                    file.write(content)
                    content = conn.recv(4096)

            message[3] = os.path.join('uploadfile',file_name)
            message = message[0:3]
            message_queue.put(message)
        
        elif message[0] == 'Download':  # 下载：Upload,file_id,filename
            message_queue.put(message)

        elif message[0] == 'Remove':  # 删除：Upload,file_id,filename
            message_queue.put(message)


def handle():
    while True:
        if message_queue.empty():
            pass
        else:
            message = message_queue.get()
            print("取出队首:"+str(message))

            if message[0] == 'Upload':
                if fileupload(message[1], message[2], message[3]):
                    print('upload success')

            elif message[0] == 'Download':
                if filedownload(message[1],message[2]):
                    print('download success')

            elif message[0] == 'Remove':
                if remove(message[1],message[2]):
                    print('remove success')

            else:
                raise Exception('未定义操作')


def fileupload(file_id, filename, file_path):
    if erasure_control('Upload'+','+file_path+file_id) is False:
        print('存储模块错误')
        return False

    if ray_control('Upload'+','+file_path) is False:
        print('ray模块错误')
        return False

    if erasure_control('Commit') is False:
        print('存储模块错误')
        return False

    ray_control('Commit')

    return True


def filedownload(file_id, filename):
    file_path = os.path.join('Download',filename)
    if erasure_control('Download'+','+file_path+','+file_id) is False:
        print('下载错误')
        return False
    
    
    # 连接目标主机
    sock_web.connect((web_ip, web_port))
    print('web连接已建立, 准备发送文件')
    # 打开要发送的文件
    with open(file_path, 'rb') as file:
        # 读取文件内容
        data = file.read()
        # 发送文件数据
        sock_web.sendall(data)
    print("文件发送完成")
    sock_web.close()
    return True


def remove(file_id, filename):
    if erasure_control('Remove'+','+filename+','+file_id) is False:
        print('存储模块错误')
        return False

    if ray_control('Remove'+filename) is False:
        print('ray模块错误')
        return False

    if erasure_control('Commit') is False:
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
