import random
import threading
import socket
from zfec.easyfec import Encoder, Decoder

receive_data = []
k = 4
m = 7
storage_ip=["192.168.209.132,0"]
storage_port=8888
listen_ip="0.0.0.0"
listen_port=6000

def erasure(message):
    global receive_data
    storage_num=2
    fragment_nums=[]
    thread_rec = []
    thread_send = []
    command_buffer=""
    for i in range(storage_num):
        receive_data[i]="0"
    ave_fragment_num=int((k+m)/storage_num)
    for i in range(storage_num-1):
        fragment_nums[i]=ave_fragment_num
    fragment_nums[storage_num-1]=k+m-ave_fragment_num*(storage_num-1)
    command=message.split(",")[0]
    filepath=message.split(",")[1]
    id=message.split(",")[2]
    filename = str(id) + ''.join('a' for _ in range(len(id)-1))

    # encode
    encoded_data = encoding(filepath)
    a,b=0,0
    for i in range(storage_num):
        thread_rec.append(threading.Thread(target=listen_storage, args=(i,)))
        if command == "Upload":
            a = b
            b = a+ fragment_nums[i]
            data=encoded_data[a:b]
        else:
            data="None"
        thread_send.append(threading.Thread(target=send_to_storage, args=(data, command, filename,i,)))

    for i in range(storage_num):
        thread_rec[i].start()
    for i in range(storage_num):
        thread_send[i].start()
    for i in range(storage_num):
        thread_rec[i].join(1)
        thread_send[i].join(1)
    if command == "Upload":
        total=0
        for i in range(storage_num):
            total+=int(receive_data[i])
        if total >= k:
            return True
        else:
            return False
    elif command == "Delete":
        pass
    elif command == 'Commit':
        flag=True
        for i in range(len(receive_data)):
            if receive_data != "yes":
                flag=False
                break
        if flag:  # 握手成功
            for i in range(storage_num - 1):
                thread_send.append(threading.Thread(target=send_to_storage, args=("None", "Go", filename, i,)))
                thread_send[i].start()
            for i in range(storage_num):
                thread_send[i].join(1)
    else:
        print("Error:Undefined Command")
        return False

def send_to_storage(data, command, filename,storage_idx):
    # 发送数据到服务器
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 第一个存储节点
    s.connect((storage_ip[storage_idx], storage_port))
    data=repr(data)
    send_data=command+"&"+filename+"&"+data
    s.sendall(send_data.encode())
    s.close()

def listen_storage(storage_idx):
    # 监听服务器storage_idx的返回值
    receive=b""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((listen_ip, listen_port))
    sock.listen(1)
    print("等待连接...")
    conn, addr = sock.accept()
    print("连接已建立:", addr)
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            break
        receive += chunk
    receive = receive.decode("utf-8")
    receive_data[storage_idx] = receive
    conn.close()

def encoding(filepath):
    # m-k correction blocks for every k blocks
    enc = Encoder(k, m)
    with open(filepath, 'rb') as f:
        data = f.read()
    # encode
    encoded_data = list(enc.encode(data))
    # print(f"总的数据块数:{len(encoded_data)}")
    return encoded_data

def decoding(receive_data_list, filename):
    dec = Decoder(k, m)
    # calculate padding length
    if len(data) % k != 0:
        padlen = (len(data) // k) - len(data) % k
    else:
        padlen = 0
    blocknums = random.sample(receive_data_list, k)
    blocks = [encoded_data[i] for i in blocknums]
    decoded_data = dec.decode(blocks, sharenums=blocknums, padlen=padlen)
    with open(f"downloadfile/{filename}", "wb") as f:
        f.write(decoded_data)

