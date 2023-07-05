import socket
import os

ec_ip =
ec_port =6000
listen_ip="0.0.0.0"
listen_port=8888

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((listen_ip, listen_port))
    sock.listen(1)
    print("等待连接...")
    fragment_num=0
    receive_data=b""
    command_buffer=""
    while True:
        conn, addr = sock.accept()
        print("连接已建立:", addr)
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            receive_data += chunk
        receive_data=receive_data.decode("utf-8")
        message_list = receive_data.split('&')
        command=message_list[0]
        if command != "Commit":
            command_buffer=command
        filename=message_list[1]
        data=eval(message_list[2])
        if command == 'Upload':
            fragment_num = str(len(data))
            send_EC_Module(fragment_num)
        elif command == 'Go':  # 最后commit成功的消息
            # 存储操作
            if command_buffer == "Upload":
                for i in range(fragment_num):
                    try:
                        with open('storage/'+str(filename)+str(i)+'.fragment', 'w') as f:
                            f.write(data[i])
                    except:
                        print("Error:store fail")

        elif message_list[0] == 'D':
            filename = message_list[1]
            file_list = []
            for file in os.listdir('storage/'):
                if filename in file:
                    with open(f'storage/{file}', 'r') as f:
                        file_list.extend(f.readlines())
            file_str = ','.join(str(i) for i in file_list)
            send_EC_Module(file_str)
            # conn.sendall(str(file_list).encode())
        elif message_list[0] == 'R':
            filename = message_list[1]
            try:
                for file in os.listdir('storage/'):
                    if filename in file:
                        os.remove(f'storage/{file}')
            except:
                s = 0

        elif command == 'Commit':
            send_EC_Module("yes")

def send_EC_Module(send_data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ec_ip, ec_port))
    s.send(send_data.encode("utf-8"))
    s.close()

if __name__ == '__main__':
    main()


