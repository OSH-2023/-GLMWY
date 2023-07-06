from neo4j import GraphDatabase
import socket
import node_operation as no
from py2neo import Graph, Node

ray_ip="192.168.209.1"
ray_port=4001
listen_ip="0.0.0.0"
listen_port=4000
result_holder=["0"]

def call_ray():
    # event=threading.Event()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # 连接目标主机
        print("尝试连接")
        sock.connect((ray_ip, ray_port))
        # 打开要发送的文件
        sock.sendall("Success".encode("utf-8"))
        print("发送neo4j缓存成功消息")
        # 创建线程并启动
        # thread = threading.Thread(target=listening, args=(listen_ip, listen_port,event))
        # thread.start()
        if_success = result_holder[0]
    except Exception as e:
        print("发送标签时出现错误:", str(e))
    finally:
        # 关闭套接字
        sock.close()

def neo_driver():
    # Neo4j数据库的连接地址和端口号
    uri = "bolt://localhost:7687"
    # 身份验证信息
    user = "neo4j"
    password = "11"
    # 创建Neo4j数据库驱动
    graph= Graph(uri, auth=(user, password))
    return graph

# def listening(listen_ip,listen_port):
#     global result_holder
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     rev_data = b""
#     try:
#         # 绑定IP和端口
#         sock.bind((listen_ip, listen_port))
#         # 监听连接
#         sock.listen(1)
#         print("neo4j等待连接...")
#         # 接受连接
#         conn, addr = sock.accept()
#         print("neo4j连接已建立:", addr)
#         # 接收标签
#         while True:
#             chunk = conn.recv(4096)
#             # print("     ----Check----chunck:" + str(chunk))
#             if not chunk:
#                 break
#             rev_data += chunk
#         # print("     ----Check----rev_data:" + str(rev_data))
#         result_holder[0]=rev_data.decode("utf-8")
#         # 关闭套接字
#     finally:
#         sock.close()


if __name__ == "__main__":
    graph=neo_driver()
    nodes = []
    # event=threading.Event()
    print("成功创建neo4j的driver")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((listen_ip, listen_port))
        sock.listen(1)
        print("neo等待连接...")

        while(True):
            receive_data = b""
            conn, addr = sock.accept()
            print("neo连接已建立:", addr)
            # 接收消息
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                # print("----Check----:",chunk)
                receive_data += chunk
            receive_data = receive_data.decode("utf-8")
            conn.close()
            print("neo接收消息成功")
            print("     ---Check---:receive_data:"+receive_data)
            if receive_data != "Commit":
                with open("temp.temp", "wb") as file:
                    file.write(receive_data.encode("utf-8"))
                print("存入缓存成功")
                call_ray()
            else:
                with open("temp.temp", "r") as file:
                    cache_data=file.read()
                print("读取缓存成功")
                split_char = "%$$%@#!#(*%^&%"
                filename=cache_data.split(split_char)[0]
                tags=cache_data.split(split_char)[1]
                tags=eval(tags)
                # 创建结点
                nodes = [Node("File",name=filename)]
                for tag in tags:
                    nodes.append(Node("Tag",name=tag))
                file_node_id=no.create_nodes(graph, nodes)
                print("创建结点成功")

                # 创建边
                relationships=[]
                for i,tag in enumerate(tags):
                    if i!=0:
                        relationships.append({'start_node_id': file_node_id[i], 'end_node_id': file_node_id[0],})
                no.create_relationships(graph, relationships)
                print("创建边成功")
    finally:
        sock.close()