import random
import threading
import socket
from zfec.easyfec import Encoder, Decoder

receive_data1 = ''
receive_data2 = ''
k = 4
m = 7

def EC_module(command, filepath, id):
    filename = str(id)+'a'
    # 解析
    # 处理
        # Upload(filepath)
            # 读文件
            # 纠删码计算得到碎片
            # 发送碎片文件到存储节点缓冲区(多线程，加锁的计数器)
            # 设置主线程阻塞时间，得到计数器值
            # 生成返回值，存入存储节点缓冲区成功与否
        # Download
        # Remove
        # 握手
            # 向各存储节点握手(多线程，加锁的计数器)
            # 设置主线程阻塞时间，得到计数器值
            # 生成返回值，存入握手成功与否
        # commit
            # 向各存储节点缓冲区发送commit(多线程)
        
    global receive_data1
    global receive_data2

    if command != 'Commit' :
        command_buffer = command

    if command == 'Upload' :
        # encode
        encoded_data = encoding(filepath)
        thread_rec1 = threading.Thread(target=listen_storage1, args=(command,))
        thread_rec2 = threading.Thread(target=listen_storage2, args=(command,))
        thread_rec1.start()
        thread_rec2.start()
        #双线程发送文件信息到两个不同的存储节点
        thread_send1 = threading.Thread(target=send_to_storage1, args=(encoded_data,command,filename,))
        thread_send2 = threading.Thread(target=send_to_storage2, args=(encoded_data,command,filename,))
        thread_send1.start()
        thread_send2.start()
        if int(receive_data1) + int(receive_data2) >= k :
            return True
        else :
            return False
    elif command == 'D' or command == 'R':
        return True
    elif command == 'Commit' :
        thread_rec1 = threading.Thread(target=listen_storage1, args=(command,))
        thread_rec2 = threading.Thread(target=listen_storage2, args=(command,))
        thread_rec1.start()
        thread_rec2.start()
        #双线程发送信息到两个不同的存储节点
        thread_send1 = threading.Thread(target=send_to_storage1, args=(encoded_data,command,filename,))
        thread_send2 = threading.Thread(target=send_to_storage2, args=(encoded_data,command,filename,))
        thread_send1.start()
        thread_send2.start()
        time.sleep(1)
        if receive_data1 == 'y' and receive_data2 == 'y':#握手成功
            if command_buffer == 'Upload':
                #令command == G ，即处理缓存后的操作
                command = 'G'
                #双线程发送信息到两个不同的存储节点
                thread_send1 = threading.Thread(target=send_to_storage1, args=(encoded_data,command,filename,))
                thread_send2 = threading.Thread(target=send_to_storage2, args=(encoded_data,command,filename,))
                time.sleep(1)
                return True
            elif command_buffer == 'D' :
                #双线程发送信息到两个不同的存储节点
                thread_send1 = threading.Thread(target=send_to_storage1, args=(encoded_data,command_buffer,filename,))
                thread_send2 = threading.Thread(target=send_to_storage2, args=(encoded_data,command_buffer,filename,))
                thread_send1.start()
                thread_send2.start()
                receive_data = receive_data1 + ',' + receive_data2
                receive_data_list = receive_data.split(',')
                decoded_data=decoding(receive_data_list, filename)
                return True
            elif command == 'R' :
                thread_send1 = threading.Thread(target=send_to_storage1, args=(encoded_data,command_buffer,filename,))
                thread_send2 = threading.Thread(target=send_to_storage2, args=(encoded_data,command_buffer,filename,))
                thread_send1.start()
                thread_send2.start()
                return True
        else :
            return False

def encoding(filepath):
    global k
    global m
    # m-k correction blocks for every k blocks
    enc = Encoder(k, m)
    with open(filepath, 'rb') as f:
        data = f.read()
    # encode
    encoded_data = list(enc.encode(data))
    #print(f"总的数据块数:{len(encoded_data)}")
    return encoded_data

def decoding(receive_data_list, filename):
    global k
    global m
    dec = Decoder(k, m)
    # calculate padding length
    if len(data) % k != 0:
        padlen = (len(data)//k) - len(data)%k
    else: padlen = 0
    blocknums = random.sample(receive_data_list, k)
    blocks = [encoded_data[i] for i in blocknums]
    decoded_data = dec.decode(blocks, sharenums=blocknums,padlen=padlen)
    with open(f"downloadfile/{filename}", "wb") as f:
        f.write(decoded_data)



def send_to_storage1(data, command, filename):
    if command == 'U':
        # 发送前3块数据到服务器1
        data1 = data[:3]
        data1.insert(0, filename)
        data1.insert(0, command)
        data1_str = ','.join(str(i) for i in data1)
    elif command == 'D':
        data1 = ['D', filename]
        data1_str = ','.join(str(i) for i in data1)
    elif command == 'R' :
        data1 = ['D', filename]
        data1_str = ','.join(str(i) for i in data1)
    elif command == 'C' :
        data1_str = 'C'
    # 发送数据到服务器
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #第一个存储节点
    s.connect(('server1_ip', 8888))
    s.sendall(data1_str.encode())
    s.close()

def send_to_storage2(data, command, filename):
    # 发送后4块数据到服务器2
    if command == 'U':
        data2 = data[3:]
        data2.insert(0, filename)
        data2.insert(0, command)
        data2_str = ','.join(str(i) for i in data2)
    elif command == 'D':
        data2 = ['D', filename]
        data2_str = ','.join(str(i) for i in data2)
    elif command == 'R' :
        data2 = ['D', filename]
        data2_str = ','.join(str(i) for i in data2)
    elif command == 'C' :
        data2_str = 'C'
    # 发送数据到服务器
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #第二个存储节点
    s.connect(('server2_ip', 8888))
    s.sendall(data2_str.encode())
    s.close()

def listen_storage1(command):
    global receive_data1
    # 监听服务器1的返回值
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('server1_ip', 8888))
    s.listen(1)
    if command == 'U' or command == 'C':
        conn, addr = s.accept()
        receive_data1 = conn.recv(1024).decode()
        conn.close()
    elif command == 'D':
        conn, addr = s.accept()
        receive_data1 = conn.recv(1024).decode()
        time.sleep(1)
        conn.close()

def listen_storage2():
    global receive_data2
    # 监听服务器2的返回值
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('server2_ip', 8888))
    s.listen(1)
    if command == 'U'or comand == 'C':
        conn, addr = s.accept()
        receive_data2 = conn.recv(1).decode()
        time.sleep(1) #运行2s
        conn.close()
    elif command == 'D':
        conn, addr = s.accept()
        receive_data2 = conn.recv(1024).decode()
        time.sleep(1)
        conn.close()
