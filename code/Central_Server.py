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
                if FileDelete(filepath):
                    print('remove success')
            else:
                raise Exception('message error')


def FileUpload(file_path,fileid="0"):
    print("开始上传")
    if erasure('Upload' + ',' + file_path+","+fileid) is False:
        print('存储模块碎片文件存入缓冲区错误')
        return False
    if ray_control('Upload' + ',' + file_path+","+fileid) is False:
        print('Ray模块标签存入缓冲区错误')
        return False
    if erasure('Commit,None,'+fileid) is False:
        print('存储模块握手错误')
        return False
    # 这三行放入EC_Module
    # if ray_control('Commit'+',None'+','+fileid) is False:
    #     print('ray commit error')
    #     return False
    return True


def FileDownload(file_path="D:\PycharmProjects",fileid="0"):
    erasure('Download,'+file_path+','+fileid)
    return True

def FileDelete(file_path,fileid="0"):
    if erasure('Delete,' + file_path+','+fileid) is False:
        print('存储模块删除命令存入缓冲区错误')
        return False
    if ray_control('Delete' + ','+file_path+','+fileid) is False:
        print('Ray模块删除命令存入缓冲区错误')
        return False
    if erasure('Commit,None,'+fileid) is False:
        print('存储模块握手错误')
        return False
    # 这三行放入EC_Module
    # if ray_control('Commit'+',None'+','+fileid) is False:
    #     print('ray commit error')
    #     return False

    return True

message_queue = queue.Queue()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Example
message_queue.put("Delete,test.txt")
if __name__ == "__main__":
    listen_thread = Thread(target=listenning)
    handle_thread = Thread(target=handle_web_message)
    listen_thread.start()
    handle_thread.start()
    listen_thread.join()
    handle_thread.join()
