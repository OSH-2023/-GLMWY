## 数据一致性架构
1.分别向存储、ray发缓存数据，并确认收到（超时自动rollback）
2.ray：执行完并向neo发送半消息，neo回消息。如果失败向网页端和存储发送rollback（超时自动rollback）；如果成功经过网页端向存储发送commit
3.存储：如果执行成功跳转4；如果失败，通过网页端向ray发送rollback，ray向neo发送rollback（超时自动rollback）
4.向mysql发送半消息并回消息。失败：回滚存储并通过网页端向ray发送rollback，ray向neo发送rollback（超时自动rollback）。成功：给mysql发送commit并通过网页端向ray发送commit，ray向neo发送commit
5.更新网页端。如果rollback则显示问题所在或者重试


## upload过程
```
$("#button_upload").click(function () {
		$("#files").click();  //调用fileupload()
		//location.reload();
	});
```
html定义按钮，点击button_upload模拟点击#files，
```
<input type="file" id="files" style="display: none" onchange="fileUpload();">
```
调用fileUpload()
```
function fileUpload() {
	console.log("begin to fileUpload");
	let selectedFile = document.getElementById('files').files[0];//TODO multisel file
	console.log("begin to encode");
	encodeFile(selectedFile);
	console.log("***************************************************");
	console.log(selectedFile);
	console.log("***************************************************");
	// console.log("begin to download to ray");
	// fileDownloadtoRay(selectedFile);
	// console.log("finish downloading to ray");

}
```
获取第一个文件，调用encodeFile()纠栅码分解
encodeFile()调用callEncoder(raw, numOfDivision, numOfAppend)，encodeCallBack
encodeCallBack调用x-TOBEDONE-main/web/grandpro_2023/WebContent/src/main/java/userManagement/FileUploader.java文件中的uploadRegister函数
uploaderRegister函数返回可用的存储节点的列表，encodeCallBack继续调用WebSocketUpload函数将碎片文件传输至存储节点对应端口。WebSocketUpload调用CallEncoder纠栅码分解，CallEncoder在webassembly里，为二进制文件。

WebSocketUpload函数发送了ws.send("U");信息，下面找谁接受了这个信息。找到x-TOBEDONE-main/storage/src/main/java/connect/FragmentManager.java中的FragmentManager类，此类中有user.recv。下面找谁创建了这个类的对象。发现有Client.java, RequestManager.java, ServerConnector.java。？？？

Client.java调用RequestManager.java，RequestManager.java传给FragmentManager user，user接受碎片文件信息，recDigest等把碎片文件写在本地。是存储节点接受碎片文件的过程。
Client.java调用ServerConnector.java连接server(mysql)，和server互发消息确认。
server下DFS_server.java调用serverthread，serverthread调用clientthread，实现接收信息。
重点看clientthread。getinputstream
ServerConnector.jav和ClientThread.java通信。通信了什么？
