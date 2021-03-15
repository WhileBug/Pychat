# Pychat
Python instant messaging script
用法：

一、 SQL

1.安装MySQL
2.替换数据库操作pymysql.connect("localhost","pythonuse","Pyth0NUs3","pythonuse")中的变量
3.新建数据库A用来替换数据库（第二个pythonuse）
4.新建用户test来替换用户（第一个pythonuse），并附上自己设定的密码（用来替换Pyth0NUs3）


注：pythonuse数据库中需要的表有：message，users
	 users的列名有：username，pass，ip，port，online，havedata
	 message的列名有：whosend，whensend，whatsend，whowassent
	 注意列名顺序要相同


二、 项目文件
服务器端：chaterServer.py
客户端：chaterCilent.py
配置文件：SETTINGS.py


三、 配置文件
服务器端必须与配置文件在同一目录下
客户端必须与配置文件在同一目录下
服务器端与客户端配置文件的第一部分（1~21行）必须一致

一般来说需要修改的部分

	1、 serverIP
	2、 serverFileSavePath 
	3、 sqlUsername
	4、 sqlPassword
	5、 sqlDB
	6、 cilentFileSavePath
	
一般来说不需要修改的部分

	1、 serverPort
	2、 bufferSize
	3、 fileReadSize
	4、 argSplit
	5、 packSplit
	6、 fileCodeStartAt
	
根据需求修改

	1、 sqlIP
	2、 timeOffset


四、 启动
先启动服务器端
再启动客户端

如果客户端需要独立运行
请将57、58、59行的#去掉，使其被执行

如果未安装SQL也要运行服务器
请运行tryServer.py
会无视业务逻辑，返回一些假消息
