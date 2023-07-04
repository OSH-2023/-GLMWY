

# 监听端口xxxx，接收来自web的消息，消息放在队列里（进程一）



# 处理函数，从队列取消息（进程二）
    # 解析
    # 处理
        # Upload(file)
            # 调用纠删码模块("command,filepath")，返回值成功与否
            # 调用ray模块("command,filepath")，返回存入neo缓存成功与否
        # Download
            # 调用纠删码模块("command,name"),返回值为解码文件
            # 解码文件传回web
        # Remove
            # 调用纠删码模块("command,name")，返回值删除成功与否
            # 调用ray模块("command,name")，删除neo4j,返回值删除成功与否
    # commit的生成
        # 调用纠删码模块，向存储集群握手，返回值为握手成功与否
        # 成功个数满足条件则向存储集群和ray模块发送commit