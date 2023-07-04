import socket
import os

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 8888))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        message = conn.recv(1024).decode()
        message_list = message.split(',')
        if message_list[0] == 'U':
            #buffer
            message_list_buffer = message_list
            file_str = str(3)
            send_EC_Module(file_str)
        elif message_list[0] == 'G':#最后commit成功的消息
            #存储操作
            filename = message_list[1]
            for i in range(1, 3):
                try:
                    with open(f'storage/{filename}{i}.txt', 'a') as f:
                        f.write(message_list_buffer[i+1]+'\n')
                except:
                    continue
        elif message_list[0] == 'D':
            filename = message_list[1]
            file_list = []
            for file in os.listdir('storage/'):
                if filename in file:
                    with open(f'storage/{file}', 'r') as f:
                        file_list.extend(f.readlines())
            file_str = ','.join(str(i) for i in file_list)
            send_EC_Module(file_str)
            #conn.sendall(str(file_list).encode())
        elif message_list[0] == 'R':
            filename = message_list[1]
            try:
                for file in os.listdir('storage/'):
                    if filename in file:
                        os.remove(f'storage/{file}')
            except:
                s=0
        elif message_list[0] == 'C':
            file_str = 'y'
            send_EC_Module(file_str)


            
def send_EC_Module(str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 8888))
    s.send(str.encode())
    s.close()

    
            
if __name__ == '__main__':
    main()


