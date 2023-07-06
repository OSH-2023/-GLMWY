from threading import Thread
import queue
import socket
from EC_Module import erasure
from Ray_Module import ray_control

def listenning():
    # todo
    return

def handle_web_message():
    while True:
        if message_queue.empty():
            pass
        else:
            message = message_queue.get()
            print("取出队首:"+str(message))
            command=message.split(',')[0]
            filepath=message.split(',')[1]
            if command == 'Upload':
                if FileUpload(filepath):
                    print('upload success')
            elif command == 'Download':
                if FileDownload(filepath):
                    print('download success')
            elif command == 'Delete':
                if FileRemove(filepath):
                    print('remove success')
            else:
                raise Exception('message error')


def FileUpload(file_path,file_id="0"):
    print("开始上传")
    if erasure('Upload' + ',' + file_path+","+file_id) is False:
        print('存储模块错误')
        return False
    if ray_control('Upload' + ',' + file_path) is False:
        print('ray模块错误')
        return False
    if erasure('Commit,None,'+file_id) is False:
        print('存储模块错误')
        return False
    ray_control('Commit,None')
    return True


def FileDownload(file_path):
    erasure('Download,D:\PycharmProjects,0')
    return True

def FileRemove(file_path):
    if erasure('Delete,' + file_path+',0') is False:
        print('存储模块错误')
        return False

    # if ray_control('Remove' + file_path) is False:
    #     print('ray模块错误')
    #     return False

    if erasure('Commit,None,0') is False:
        print('存储模块错误')
        return False

    # if ray_control('Commit') is False:
    #     print('ray commit error')
    #     return False

    return True

message_queue = queue.Queue()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Example
message_queue.put("Download,test.txt")
if __name__ == "__main__":
    listen_thread = Thread(target=listenning)
    handle_thread = Thread(target=handle_web_message)
    listen_thread.start()
    handle_thread.start()
    listen_thread.join()
    handle_thread.join()
