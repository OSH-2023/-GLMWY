import tagging
import socket
import os
import threading

neo_ip="192.168.209.135"
neo_port=4000
listen_ip="0.0.0.0"
listen_port=4001

def ray_control(message):
    # 解析
    command=message.split(",")[0]
    filepath=message.split(",")[1]
    _ , filename=os.path.split(filepath)
    if command == "Upload":
        return Upload(filename,filepath)
    elif command == "Remove":
        return Remove(filename)
    elif command == "Commit":
        return Commit()
    else:
        print("Error:Undefined command")

def Upload(filename,filepath):
    if_success=False
    result_holder=[False]
    event = threading.Event()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    keywords = tagging.tagging(filepath)
    send_data=filename+","+keywords
    try:
        # 连接目标主机
        print("尝试连接")
        sock.connect((neo_ip, neo_port))
        # 打开要发送的文件
        sock.sendall(send_data.encode("utf-8"))
        print("发送标签成功")
        # 创建线程并启动
        thread = threading.Thread(target=listening, args=(listen_ip,listen_port,result_holder,event))
        thread.start()
        event.wait(2)
        if_success=result_holder[0]
    except Exception as e:
        print("发送标签时出现错误:", str(e))
    finally:
        # 关闭套接字
        sock.close()
        print("Check:if_success:"+str(if_success))
        return if_success

def Remove(filename):
    pass

def Commit():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # 连接目标主机
        sock.connect((neo_ip, neo_port))
        # 打开要发送的文件
        sock.sendall("Commit".encode("utf-8"))
        print("发送Commit消息成功")
    except Exception as e:
        print("发送Commit消息时出现错误:", str(e))
    finally:
        # 关闭套接字
        sock.close()

def listening(listen_ip,listen_port,result_holder,event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # 绑定IP和端口
        sock.bind((listen_ip, listen_port))
        # 监听连接
        sock.listen(1)
        print("等待连接...")
        # 接受连接
        conn, addr = sock.accept()
        print("连接已建立:", addr)
        # 创建保存文件的空文件
        data = conn.recv(4096)
        data=data.decode('utf-8')
        print("Check:data:"+str(data))
        if(data == "Success"):
            result_holder[0]=True
    except Exception as e:
        print("接收是否成功消息时出现错误:", str(e))
    finally:
        # 关闭连接
        conn.close()
        # 关闭套接字
        sock.close()
        event.set()
