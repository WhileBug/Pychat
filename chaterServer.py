from socket import *
import time
import threading #多线程模块
import re #正则表达式模块
import pymysql#mysql模块
import os
import base64
import SETTINGS

pathFinderWindows = r'[^\\/:*?"<>|\r\n]+$'

ARGSPLIT = SETTINGS.argSplit
PACKSPLIT = SETTINGS.packSplit #间隔符

#从数据库取出来的数据统一后缀2

HOST = SETTINGS.serverIP
PORT = SETTINGS.serverPort
BUFSIZ = SETTINGS.bufferSize
ADDR = (HOST, PORT)
TIMEOFFSET = SETTINGS.timeOffset

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(SETTINGS.serverListenNumber)
userList=[]#用户列表的数据

fileRecvList = {}
FILESIZ = SETTINGS.fileReadSize
fileCodeTot = SETTINGS.fileCodeStartAt
fileSavePath =SETTINGS.serverFileSavePath

clist={}

def strToNum(str):
	num = 0
	for i in range(len(str)):
		num += (ord(str[i])-48) * (10**(len(str)-i-1))
	return num
	
def strToByte(str):
	return str
	
def cutPack(pack):
	packList = []
	temp = pack.split(PACKSPLIT)
	for i in temp:
		temp2 = i.split(ARGSPLIT)
		temp2.pop()
		packList.append(temp2)
	packList.pop()
	return packList

def packData(*dataList):
	pack = ''
	for i in dataList:
		pack+=i
		pack+=ARGSPLIT
	pack+=PACKSPLIT
	return pack.encode()

def listPackData(dataList):
	pack = ''
	for i in dataList:
		pack+=i
		pack+=ARGSPLIT
	pack+=PACKSPLIT
	return pack.encode()

def getPackNum(dic):
	return strToNum(dic['num'])

def signin(username,password,ip,port):
	db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)
	cursor = db.cursor()
	sql = "select * from users where \
		   username = '%s'" % (username)
	   
	try:#查找用户名是否重复
		cursor.execute(sql)
		results = cursor.fetchall()
		if results: 
			print('it already exist!')
			return '3' #发现存在
	except:
		db.rollback()
	db.close()

	db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)
	cursor = db.cursor()
	sql = "INSERT INTO users(username, \
		   pass, ip, port, online, havedata) \
		   VALUES ('%s', '%s', '%s', %d,  %d, %d)" % \
		   (username, password, ip, port, 0, 2)
		   
	try:#更新数据
		cursor.execute(sql)
		db.commit()
		print('create successfully!')
	except:
		db.rollback()
	db.close()
	return '1'

def login(username,password,ip,port):
	db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)
	cursor = db.cursor()
	sql = "select * from users where \
		   username = '%s'" % (username)
	   
	try:#查找用户名是否存在
		cursor.execute(sql)
		results = cursor.fetchall()
		if not results: #不存在直接返回
			print('it not exist!') 
			return '3',2 #用户名不存在
		else: #存在继续对比密码
			password2 = results[0][1]#取出数据库内容进行比对
			havedata2 = results[0][5]
			if(password!=password2): return '4',2
	except:
		db.rollback()
	db.close()

	db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)
	cursor = db.cursor()
	sql = "update users set ip='%s', port='%s', online=%d, havedata=%d\
		   where username = '%s'" % (ip,port,1,2,username)

	try: #更新数据库
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
	db.close()
	return '1',havedata2

def sendrentmessage(username,tcpCliSock,havedata2):
	if (havedata2==1):#如果有残留的信息，传输残留信息
		db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)
		cursor = db.cursor()
		sql = "SELECT * FROM message \
		   WHERE whowassent = '%s'" % (username)
		try: 
			cursor.execute(sql)
			# 获取所有记录列表
			results = cursor.fetchall()
			for row in results:
				whosend2 = row[0]
				whensend2 = row[1]
				whatsend2 = row[2]
				tcpCliSock.send(packData('getMessage',whosend2,whensend2,whatsend2))#将残留消息发送出去
		except:
			print("Error: unable to fetch data")
		db.close()
		
		db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)#更改havedata值
		cursor = db.cursor()
		sql = "update users set havedata=2\
			   where username = '%s'" % (username)

		try: 
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()
		db.close()
		
		db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)#删除剩余数据
		cursor = db.cursor()
		sql = "delete FROM message \
		   WHERE whowassent = '%s'" % (username)
		try: 
			cursor.execute(sql)
			db.commit()
		except:
			print("Error: unable to fetch data")
		db.close()
		
def logout(username):
	db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)
	cursor = db.cursor()
	sql = "update users set online=0 where \
		   username='%s'" % (username)
		   
	try:
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
	db.close()

def getUserList():
	db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)
	cursor = db.cursor()
	sql = "select * from users"
		   
	try:#输出用户列表
		cursor.execute(sql)
		results = cursor.fetchall()
		for row in results:
			userList.append(row[0])
			userList.append(str(row[4]))
	except:
		db.rollback()
	db.close()

def sendmessage(whosend,whensend,whatsend,whowassent):
	db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)
	cursor = db.cursor()
	sql = "select * from users where \
		   username = '%s'" % (whowassent)
	   
	try:#查找用户是否在线
		cursor.execute(sql)
		results = cursor.fetchall()
		online2 = results[0][4]
	except:
		db.rollback()
	db.close()
	
	if(online2==1):#如果在线直接发送
		clist[whowassent].send(packData('getMessage',whosend,whensend,whatsend))
	else:#不在线，存入数据库
		db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)
		cursor = db.cursor()
		sql = "INSERT INTO message(whosend, \
		   whensend, whatsend, whowassent) \
		   VALUES ('%s', '%s', '%s', '%s')" % \
		   (whosend, whensend, whatsend, whowassent)
		   
		try:
			cursor.execute(sql)
			db.commit()
		except Exception as err:
			db.rollback()
		db.close()
		
		db = pymysql.connect(SETTINGS.sqlIP,SETTINGS.sqlUsername,SETTINGS.sqlPassword,SETTINGS.sqlDB)#改变havedata
		cursor = db.cursor()
		sql = "update users set havedata=1 where \
		   username='%s'" % (whowassent)
		   
		try:
			cursor.execute(sql)
			db.commit()
		except Exception as err:
			db.rollback()
		db.close()

def fileWrite(fileDic):
	global fileSavePath
	filePath = fileSavePath+'\\'+fileDic['fileCode']+fileDic['fileName']
	fileDic['data'].sort(key = getPackNum)
	with open(filePath, 'wb') as f:
		for block in fileDic['data']:
			f.write(base64.b64decode(block['content'].encode()))


def sendFile(fileCode,sock):
	global fileSavePath
	global fileRecvList
	cutFile = []
	fileSize = 0
	
	print(fileCode)
	filePath = fileSavePath+'\\'+fileCode+fileRecvList[fileCode]['fileName']
	with open(filePath, "rb") as f:
		while True:
			block = f.read(FILESIZ)  # 每次读取固定长度到内存缓冲区
			if block:
				fileSize+=len(block)
				cutFile.append(base64.b64encode(block).decode())
			else:
				break  # 如果读取到文件末尾，则退出
	
	fileName = re.findall(pathFinderWindows, filePath)[0]
	
	for th in range(len(cutFile)):
		pack = packData('getFile', '1', fileCode, str(th), cutFile[th])
		time.sleep(TIMEOFFSET)
		sock.send(pack)
		
	pack = packData('getFile', '2', fileCode)
	sock.send(pack)
	
	
	return 'file send succeed'

def Deal(tcpCliSock,ip,port):
	global fileRecvList
	global fileCodeTot
	global clist
	username=''
	while True:
		str = tcpCliSock.recv(BUFSIZ).decode() #接收命令
		packsList=cutPack(str)
		if packsList:#如果包不为空
			for List in packsList:
				if (List[0]=='signin'):#命令为注册
					exist=signin(List[1],List[2],ip,port)#传入username，password
					tcpCliSock.send(packData('signin',exist))#回应注册情况
				elif(List[0]=='login'):#命令为登录
					exist,havedata2=login(List[1],List[2],ip,port)
					tcpCliSock.send(packData('login',exist))#回应登录情况
					if(exist=='1'): 
						username=List[1]
						clist[username]=tcpCliSock
					sendrentmessage(List[1],tcpCliSock,havedata2)
				elif(List[0]=='logout'):#命令为下线
					if(username!=''): 
						logout(username)
						clist.pop(username)
					tcpCliSock.close()
					return
				elif(List[0]=='getUserList'):#命令请求用户列表
					userList.append('getUserList')
					getUserList()
					tcpCliSock.send(listPackData(userList))#回应用户列表
				elif (List[0]=='sendMessage'):
					if(List[4]=='text'): sendmessage(List[2],List[3],ARGSPLIT+List[5],List[1])
					else:
						fileCodeTot += 1
						tempFileCode = '%d' % fileCodeTot
						(path1, fileName) = os.path.split(List[5])
						fileRecvList[tempFileCode] = {'srcUser':List[2], 'dstUser':List[1], 'time':List[3], 'fileName': fileName, 'fileSize': List[6], 'data':[], 'fileCode':tempFileCode}
						
						tcpCliSock.send(packData('sendFile', '1', tempFileCode))
				elif (List[0]== 'sendFile'):
					comNum = List[1]
					fileCode = List[2]
					if comNum == '1':
						fileRecvList[fileCode]['data'].append({'num':List[3], 'content': List[4]})
						
					elif comNum == '2':
						fileWrite(fileRecvList[fileCode])
						packet = packData('getMessage', fileRecvList[fileCode]['srcUser'], fileRecvList[fileCode]['time'], 'file', fileRecvList[fileCode]['fileName'], fileRecvList[fileCode]['fileSize']+'Bytes', fileCode)
						sendmessage(fileRecvList[fileCode]['srcUser'],fileRecvList[fileCode]['time'],'file'+ARGSPLIT+fileRecvList[fileCode]['fileName']+ARGSPLIT+fileRecvList[fileCode]['fileSize']+'Bytes'+ARGSPLIT+fileCode,fileRecvList[fileCode]['dstUser'])
				elif (List[0] == 'getFile'):
					sendFile(List[1], tcpCliSock)

if __name__ == '__main__':
	while True:
		print('waiting for connection...')
		tcpCliSock, addr = tcpSerSock.accept()
		print('...connected from:',addr)
		chat = threading.Thread(target = Deal, args = (tcpCliSock,addr[0],addr[1])) #创建新线程进行处理
		chat.start() #启动线程


	tcpSerSock.close()