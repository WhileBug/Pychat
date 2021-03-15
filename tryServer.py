#coding:utf-8

from socket import *
import threading
import time
import os
import re
import base64
import SETTINGS


pathFinderWindows = r'[^\\/:*?"<>|\r\n]+$'

HOST = SETTINGS.serverIP
PORT = SETTINGS.serverPort
ADDR = (HOST, PORT)
tcpCliSock = socket(AF_INET, SOCK_STREAM)

BUFSIZ = SETTINGS.bufferSize
FILESIZ = SETTINGS.fileReadSize

ARGSPLIT = SETTINGS.argSplit
PACKSPLIT = SETTINGS.packSplit

loginStatus = 2
signinStatus = 2
gotMessageList = []
gotUserList = []
ThisUsername = 'unauthorized'

fileRecvList = {}
fileCodeTot = SETTINGS.fileCodeStartAt
fileSavePath = SETTINGS.serverFileSavePath

sockets = {}

def Send(data): #发送消息
	tcpCliSock.send(data.encode())

 
def getUserListFirstChar(dic):
	return dic[username][0]

def getLocalTime():
	return time.asctime( time.localtime(time.time()) )

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
	#print('pack:',pack)
	return pack.encode()

def strToNum(str):
	num = 0
	for i in range(len(str)):
		num += (ord(str[i])-48) * (10**(len(str)-i-1))
	return num
	
def strToByte(str):
	return str
	
def getPackOrdList(num):
	n = strToNum(num)
	
	for i in range(n):
		yield str(i+1)

def getPackNum(dic):
	return strToNum(dic['num'])

def fileWrite(fileDic):

	global fileSavePath
	filePath = fileSavePath+'\\'+fileDic['fileCode']+fileDic['fileName']
	fileDic['data'].sort(key = getPackNum)
	with open(filePath, 'wb') as f:
		for block in fileDic['data']:
			#base64.b64decode(block['content'].decode())
			f.write(base64.b64decode(block['content'].encode()))
	print('file write end')

def sendFile(fileCode,sock):
	global fileSavePath
	global fileRecvList
	print('start send file')
	cutFile = []
	fileSize = 0
	
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
		sock.send(pack)
		
	pack = packData('getFile', '2', fileCode)
	sock.send(pack)
	
	
	return 'file send succeed'
	

def deal(socket, temptemp):
	global fileRecvList
	global fileCodeTot
	while True:
		data = socket.recv(BUFSIZ).decode()
		#print(data)
		packList = cutPack(data)
		for pack in packList:
			if(len(data)<1):
				print('data len error')
				return
			com = pack[0]
			if com == 'login':
				if(len(pack)<3):
					print('num of data error')
					return
				username = pack[1]
				password = pack[2]
				sockets[username] = socket
				
				socket.send(packData(pack[0], '1'))
			
			elif com == 'signin':
				if(len(pack)<3):
					print('num of data error')
					return
				username = pack[1]
				password = pack[2]
				
				
				socket.send(packData(pack[0],'1'))
			
			elif com == 'sendMessage':
				if(len(pack)<6):
					print('num of data error')
					return
				type = pack[4]
				print('type: ', type)
				if type == 'text':
					dstuser = pack[1]
					srcuser = pack[2]
					fucktime = pack[3]
					dadada = pack[5]
					
					print(packData('getMessage', srcuser, fucktime,pack[4], dstuser+dadada))
					socket.send(packData('getMessage', srcuser, fucktime,pack[4], dstuser+dadada))
				
				elif type == 'file':
					if len(pack)<7:
						print('num of data error')
						return
					print('get file header')
					fileCodeTot += 1
					tempFileCode = str(fileCodeTot)
					(path1, fileName) = os.path.split(pack[5])
					fileRecvList[tempFileCode] = {'srcUser':pack[2], 'dstUser':pack[1], 'time':pack[3], 'fileName': fileName, 'fileSize': pack[6], 'data':[], 'fileCode':tempFileCode}
					
					socket.send(packData('sendFile', '1', tempFileCode))
				
			elif com == 'getUserList':
				socket.send(packData('getUserList', 'fuckme', '1', 'fuckher', '2'))
			
			elif com == 'sendFile':
				if len(pack)<3:
					print('num of data error')
					return
				comNum = pack[1]
				fileCode = pack[2]
				if comNum == '1':
					if len(pack)<5:
						print('num of data error')
						return
					fileRecvList[fileCode]['data'].append({'num':pack[3], 'content': pack[4]})
					
				elif comNum == '2':
					fileWrite(fileRecvList[fileCode])
					packet = packData('getMessage', fileRecvList[fileCode]['srcUser'], fileRecvList[fileCode]['time'], 'file', fileRecvList[fileCode]['fileName'], fileRecvList[fileCode]['fileSize']+'Bytes', fileCode)
					socket.send(packet)
			
			elif com == 'getFile':
				if len(pack)<2:
					print('num of data error')
					return
				sendFile(pack[1], socket)
				
			
			elif com == 'logout':
				socket.close()
				return
			
			else:
				socket.send(packData('getMessage', 'me', getLocalTime(), 'text','wrong pack'))
		



tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)	


while True:
	print('waiting for connection...')
	tcpCliSock, addr = tcpSerSock.accept()
	print('...connected from:',addr)
	chat = threading.Thread(target = deal, args = (tcpCliSock, None)) #创建新线程进行处理
	chat.start() #启动线程
tcpSerSock.close()





