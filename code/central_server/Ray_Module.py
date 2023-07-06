import tagging
import socket
import os

neo_ip="192.168.209.136"
neo_port=4000
listen_ip="0.0.0.0"
listen_port=4001
result_holder = [False]

def ray_control(message):
    # 解析
    command=message.split(",")[0]
    filepath=message.split(",")[1]
    fileid=message.split(",")[2]
    _ , filename=os.path.split(filepath)
    if command == "Upload":
        return Upload(filename,filepath,fileid)
    elif command == "Delete":
        return Delete(filename,fileid)
    elif command == "Commit":
        return Commit()
    else:
        print("Error:Undefined command")

def Upload(filename,filepath,fileid):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    keywords = tagging.tagging(filepath)
    split_char = "%$$%@#!#(*%^&%"
    send_data="Upload"+split_char+filename+split_char+keywords+split_char+fileid
    try:
        # 连接目标主机
        print("尝试连接neo4j_handle")
        sock.connect((neo_ip, neo_port))
        # 发送给neo4j_handle
        sock.sendall(send_data.encode("utf-8"))
        print("发送到neo4j_handle成功")
    except Exception as e:
        print("发送标签时出现错误:", str(e))
    finally:
        sock.close()

    listening(listen_ip, listen_port)
    print("     ----Check----result_holder:"+str(result_holder))
    if_success=result_holder[0]

    print("     ----Check----if_success:" + str(if_success))
    return if_success

def Delete(filename,fileid):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    split_char = "%$$%@#!#(*%^&%"
    send_data = "Delete"+split_char+filename+split_char+"None"+split_char+fileid
    try:
        # 连接目标主机
        print("尝试连接neo4j_handle")
        sock.connect((neo_ip, neo_port))
        # 发送给neo4j_handle
        sock.sendall(send_data.encode("utf-8"))
        print("发送到neo4j_handle成功")
    except Exception as e:
        print("发送标签时出现错误:", str(e))
    finally:
        sock.close()

    listening(listen_ip, listen_port)
    print("     ----Check----result_holder:" + str(result_holder))
    if_success = result_holder[0]

    print("     ----Check----if_success:" + str(if_success))
    return if_success

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
    return True

def listening(listen_ip,listen_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定IP和端口
    try:

        sock.bind((listen_ip, listen_port))
        # 监听连接
        sock.listen(1)
        print("Ray模块等待连接...")
        # 接受连接
        conn, addr = sock.accept()
        print("Ray模块连接已建立:", addr)
        # 创建保存文件的空文件
        data = conn.recv(4096)
        data=data.decode('utf-8')
        if(data == "Success"):
            result_holder[0]=True
            print("     ----Check----result_holder:" + str(result_holder))
        # 关闭连接
    finally:
        sock.close()
    # event.set()
