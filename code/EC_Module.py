import time
import threading
import socket
import random
from zfec.easyfec import Encoder, Decoder

storage_num=1
k = 4
m = 7
receive_data = ["0" for _ in range(storage_num)]
storage_ip=["192.168.209.137"]
storage_port=8888
listen_ip="0.0.0.0"
listen_port=6000

def erasure(message):
    fragment_nums=[]
    thread_rec = []
    thread_send = []
    # print("     ----Check----receive_data:",str(receive_data))
    # 分配碎片
    ave_fragment_num=int(m/storage_num)
    for i in range(storage_num-1):
        fragment_nums.append(ave_fragment_num)
    fragment_nums.append(m-ave_fragment_num*(storage_num-1))
    # 解析message
    command=message.split(",")[0]
    filepath=message.split(",")[1]
    id=message.split(",")[2]
    filename = str(id)
    # 纠删码计算
    encoded_data=[]
    if command == "Upload":
        encoded_data = encoding(filepath)
    a,b=0,0
    for i in range(storage_num):
        # 定义listen（监听storage）进程
        thread_rec.append(threading.Thread(target=listen_storage, args=(i,)))
        # 准备发送给storage的碎片
        if command == "Upload":
            a = b
            b = a+ fragment_nums[i]
            data=encoded_data[a:b]
        else:
            data=""
        # 定义发送给storage的进程
        thread_send.append(threading.Thread(target=send_to_storage, args=(data, command, filename,i,)))
    # 开启监听进程
    for i in range(storage_num):
        thread_rec[i].start()
    # 等待监听进程开启监听
    time.sleep(0.5)
    # 开启发送进程并等待发送结束，这时监听进程已经得到storage的回复
    for i in range(storage_num):
        thread_send[i].start()
    for i in range(storage_num):
        thread_send[i].join(1)
    thread_send = []
    # 等待监听进程
    for i in range(storage_num):
        thread_rec[i].join(1)
    thread_rev = []
    if command == "Upload":
        print("     ----Check----receive_data:"+str(receive_data))
        total=0
        for i in range(storage_num):
            total+=int(receive_data[i])
        if total >= k:
            print("storage存入缓冲区成功")
            return True
        else:
            return False
    elif command == "Delete":
        for i in range(storage_num):
            if receive_data[i] == "0":
                return False
        return True
    elif command == "Download":
        download_list=[]
        for i in range(storage_num):
            if receive_data[i] == "0":
                return False
        for i in range(storage_num):
            download_list+=eval(receive_data[i])
        decoding(download_list)
        return True
    elif command == 'Commit':
        flag=True
        print("     ----Check----receive_data:",str(receive_data))
        for i in range(len(receive_data)):
            if receive_data[i] != "yes":
                flag=False
                break
        if flag:
            print("EC模块和storage握手成功")
            for i in range(storage_num):
                thread_send.append(threading.Thread(target=send_to_storage, args=("", "Go", filename, i,)))
                thread_send[i].start()
            for i in range(storage_num):
                thread_send[i].join(1)
    else:
        print("Error:Undefined Command")
        return False

def send_to_storage(data, command, filename,storage_idx):
    # 发送数据到服务器
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 第一个存储节点
    print("准备发送到storage"+str(storage_idx))
    sock.connect((storage_ip[storage_idx], storage_port))
    data=repr(data)
    # print("-----Check----data:"+str(data))
    split_char="%$$%@#!#(*%^&%"
    send_data=command+split_char+filename+split_char+data
    sock.sendall(send_data.encode("utf-8"))
    print("发送到storage成功")
    sock.close()

def listen_storage(storage_idx):
    # 监听服务器storage_idx的返回值
    receive=b""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((listen_ip, listen_port))
    sock.listen(1)
    print("EC模块等待连接...")
    conn, addr = sock.accept()
    print("EC模块连接已建立:", addr)
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            break
        receive += chunk
    receive = receive.decode("utf-8")
    receive_data[storage_idx] = receive
    print("EC模块接收到消息")
    conn.close()
    sock.close()

def encoding(filepath):
    # m-k correction blocks for every k blocks
    enc = Encoder(k, m)
    with open(filepath, 'rb') as f:
        data = f.read()
    # encode
    encoded_data = list(enc.encode(data))
    with open("total_len.tmp","w") as t:
        t.write(str(len(data)))
    with open("encoding1.tmp","w") as s:
        s.write(str(encoded_data))
    # print(f"总的数据块数:{len(encoded_data)}")
    return encoded_data

def decoding(data):
    with open("encoding2.tmp","w") as t:
        t.write(str(data))
    with open("total_len.tmp","r") as f:
        total_len=int(f.read())
    print("totoal_len:"+str(total_len))
    dec = Decoder(k, m)
    # calculate padding length
    if total_len % k != 0:
        padlen = (total_len // k) - total_len % k
    else:
        padlen = 0
    numbers = list(range(m))
    blocknums = random.sample(numbers, k)
    blocks = [data[i] for i in blocknums]
    decoded_data = dec.decode(blocks, sharenums=blocknums, padlen=padlen)
    # print(decoded_data)
    with open(f"downloadfile/tttt", "wb") as f:
        f.write(decoded_data)

