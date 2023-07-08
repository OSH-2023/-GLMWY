import os
import sys
import socket
import shutil

sys.path.append(os.path.dirname(sys.path[0]))
import config
setting=config.args()
settings=setting.set

with open("storage_ip.txt","r") as f:
    ip=f.read()
print("     ----Check---ip:"+str(ip))
storage_ip=str(ip.strip())
storage_idx=settings["storage_ip"].index(storage_ip)
print("storage_idx:"+str(storage_idx))

listen_ip=settings["listen_ip"]
listen_port=settings["storage_listen_EC"][storage_idx]
ec_ip =settings["central_ip"]
ec_port =settings["storage_send_EC"][storage_idx]

absolute_path=settings["absolute_path"]
temp="temp\\"


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((listen_ip, listen_port))
    sock.listen(1)
    print("storage等待连接...")
    command_buffer=""
    fragment_num = 0
    data = []
    while True:
        receive_data = b""
        conn, addr = sock.accept()
        print("storage连接已建立:", addr)
        # 接收消息
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            # print("----Check----:",chunk)
            receive_data += chunk
        receive_data=receive_data.decode("utf-8")
        conn.close()
        print("storage接收消息成功")
        # print("     ---Check---:receive_data:"+receive_data)
        split_char = "%$$%@#!#(*%^&%"
        message_list = receive_data.split(split_char)
        # 解析消息
        command=message_list[0]
        if command == "Upload" or command == "Delete":
            command_buffer=command
        filename=message_list[1]#####################################
        print("     ---Check---:command:"+command)
        # print("---Check---:message_list[2]:"+message_list[2])
        # print("     ----Check----data_len:",len(data))
        # 发送碎片个数给EC模块
        if command == 'Upload':
            data = eval(message_list[2])
            fragment_num = str(len(data))
            send_EC_Module(fragment_num)
        elif command== 'Delete' :
            send_EC_Module("yes")
        elif message_list[0] == 'Download':
            file_list = []
            print("准备下载数据")
            if os.path.exists('storage/' + filename):
                for i in range(len(os.listdir('storage/' + filename + '/'))):
                    with open('storage/' + filename + '/' + filename + str(i) + '.fragment', 'rb') as f:
                        content = f.read()
                        print("     ----Check----list:" + str(content))
                        file_list.append(content)
                    print("下载成功")
                send_EC_Module(repr(file_list))
            else:
                send_EC_Module("0")
        elif command == 'Go':  # 最后commit成功的消息
            # 存储操作
            print("     ----Check----command_buffer:",command_buffer)
            if command_buffer == "Upload":
                print("尝试从缓冲区存入")
                try:
                    os.makedirs('storage/' + str(filename))
                    print("创建文件夹成功")
                except Exception as e:
                    print("创建文件夹失败：", str(e))
                for i in range(int(fragment_num)):
                    try:
                        with open('storage/'+str(filename)+'/'+str(filename)+str(i)+'.fragment', 'wb') as f:
                            f.write(data[i])
                    except Exception as e:
                        print("存入失败:", str(e))
                    finally:
                        print("存入成功")
            elif command_buffer == "Delete" :
                print("尝试删除文件")
                try:
                    for file in os.listdir('storage/'):
                        if filename == file:
                            # 删除非空文件夹
                            shutil.rmtree('storage/'+filename)
                except Exception as e:
                        print("删除失败:", str(e))
                finally:
                    print("删除成功")
        elif command == 'Commit':
            print("握手成功")
            send_EC_Module("yes")
    sock.close()


def send_EC_Module(send_data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("     ----Check----ec_port:"+str(ec_port))
    s.connect((ec_ip, ec_port))
    print("     ----Check----:send_data:"+str(send_data))
    s.send(send_data.encode("utf-8"))
    s.close()


if __name__ == '__main__':
    main()


