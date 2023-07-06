from neo4j import GraphDatabase
import socket
import node_operation as no
from py2neo import Graph, Node, NodeMatcher

ray_ip="192.168.209.1"
ray_port=4001
listen_ip="0.0.0.0"
listen_port=4000
result_holder=["0"]

def call_ray():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # 连接目标主机
        print("尝试连接")
        sock.connect((ray_ip, ray_port))
        # 打开要发送的文件
        sock.sendall("Success".encode("utf-8"))
        print("发送neo4j缓存成功消息")
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

if __name__ == "__main__":
    graph=neo_driver()
    matcher = NodeMatcher(graph)
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
            split_char = "%$$%@#!#(*%^&%"
            temp=receive_data
            command=temp.split(split_char)[0]
            conn.close()
            print("neo接收消息成功")
            print("     ---Check---:receive_data:"+receive_data)
            if command != "Commit":
                with open("temp.temp", "wb") as file:
                    file.write(receive_data.encode("utf-8"))
                print("存入缓存成功")
                call_ray()
            else:
                with open("temp.temp", "r") as file:
                    cache_data=file.read()
                print("读取缓存成功")
                split_char = "%$$%@#!#(*%^&%"
                cache_command=cache_data.split(split_char)[0]
                filename=cache_data.split(split_char)[1]
                fileid=cache_data.split(split_char)[3]
                if cache_command == "Upload":
                    tags=cache_data.split(split_char)[2]
                    tags=eval(tags)
                    # 创建结点
                    nodes = [Node("File",name=filename,fileid=fileid)]
                    file_precreate_nodes=[]
                    for tag in tags:
                        node_match = matcher.match("Tag",name=tag)
                        if len(node_match) != 0:
                            file_precreate_nodes.append(node_match)
                            continue
                        nodes.append(Node("Tag",name=tag))
                    file_create_node_id=no.create_nodes(graph,nodes)
                    for nodes in file_precreate_nodes:
                        for node in nodes:
                            file_create_node_id.append(node.identity)
                    print("创建结点成功")

                    # 创建边
                    relationships=[]
                    for i,tag in enumerate(tags):
                        if i!=0:
                            relationships.append({'start_node_id': file_create_node_id[i], 'end_node_id': file_create_node_id[0],})
                    no.create_relationships(graph, relationships)
                    print("创建边成功")
                if cache_command == "Delete":
                    print("尝试删除")
                    try:
                        nodes = matcher.match("File", name=filename, fileid=fileid)
                        for node in nodes:
                            print("     ----Check----node:" + str(node))
                            graph.delete(node)
                            print("节点删除成功")
                    except Exception as e:
                        print("节点删除失败:", e)
                    # 使用 Cypher 查询找到孤立节点
                    query = f"MATCH (n:Tag) WHERE NOT ()--(n) RETURN n"
                    result = graph.run(query)
                    # 遍历结果并删除孤立节点
                    for record in result:
                        node = record["n"]
                        print(node)
                        try:
                            graph.delete(node)  # 删除节点及其关系边
                            print("孤立节点删除成功")
                        except Exception as e:
                            print("孤立节点删除失败:", e)
                    print("Delete成功")
    finally:
        sock.close()