#coding:utf-8

from socket import *
import threading
import time
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
thisUsername = 'unauthorized'

resLogin = 0
resSignin = 0
resUserList = 0

resFileCode = 0
fileCode = ''
fileSavePath = SETTINGS.cilentFileSavePath
fileCodeList = {}


TIMEOFFSET =  SETTINGS.timeOffset


def send(data): #发送消息
	tcpCliSock.send(data)

 
def Recv(sock, temptemp): #接收消息
	while True:
		data = tcpCliSock.recv(BUFSIZ).decode()
		packList = cutPack(data)
		for pack in packList:
			commandCheck(pack)

def initial():
	tcpCliSock.connect(ADDR)
	recver = threading.Thread(target = Recv, args = (tcpCliSock, None)) #创建接收信息线程
	recver.start()
	#cona = threading.Thread(target = C_O_N, args = (tcpCliSock, None)) #创建接收信息线程
	#cona.start()
	#cona.join()
	
def C_O_N(sock, temptemp):
	while True:
		global thisUsername
		com = input("command? > ")
		if com == 'login':
			username = input('username? > ')
			password = input('password? > ')
			res = logIn(username, password)
			if res == 1:
				thisUsername = username
				print('login success!')
			else:
				print('login failed, errorcode: ', res)
		
		elif com == 'logout':
			logOut()
		
		elif com == 'signin':
			username = input('username? > ')
			password = input('password? > ')
			res = signin(username, password)
			if res == 1:
				thisUsername = username
				print('signin success!')
			else:
				print('signin failed, errorcode: ', res)
		
		elif com == 'getUserList':
			print(getUserList())
		
		elif com == 'getMessage':
			print(getMessage())
			
		
		elif com == 'sendMessage':
			dst = input('to whom? > ')
			data = input('data? > ')
			sendMessage(dst, data)
		
		elif com == 'sendFile':
			dstUser = input('to whom? > ')
			src = input('where? > ')
			sendFile(dstUser, src)
			
		else:
			print("please use: \n\tlogin\n\tsignin\n\tgetUserList\n\tgetMessage\n\tsendMessage\n\tsendFile\nyour input was: ",com) 
			


def strToByte(str):
	return str

def getPackNum(dic):
	return strToNum(dic['num'])

def getUserListFirstChar(dic):
	return dic['username'][0]

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
	return pack.encode()

def strToNum(str):
	num = 0
	for i in range(len(str)):
		num += (ord(str[i])-48) * (10**(len(str)-i-1))
	return num
	
def listPackData(dataList):
	pack = ''
	for i in dataList:
		pack+=i
		pack+=ARGSPLIT
	pack+=PACKSPLIT
	return pack.encode()
 
def commandCheck(data):
	if(len(data)<1):
		print('data len error')
		return
	global resLogin
	global resSignin
	global resUserList
	global signinStatus
	global loginStatus
	global gotUserList
	global gotMessageList
	global resFileCode
	global fileCode
	global fileSavePath
	global fileCodeList
	
	global Max
	global testFile
	
	command = data[0]
	if command == 'login':
		if(len(data)<2):
			print('num of data error')
			return
		loginStatus = ord(data[1])-48
		resLogin = 1
	
	elif command == 'signin':
		if(len(data)<2):
			print('num of data error')
			return
		signinStatus = ord(data[1])-48
		resSignin = 1

	elif command == 'getUserList':
		
		for i in [data[1:][i:i +2] for i in range(0, len(data[1:]), 2)]:
			recv1 = i[0]
			if i[1]=='0': recv2 = '2'
			else: recv2 = i[1]
			if {'username':recv1, 'online':recv2} not in gotUserList:
				gotUserList.append({'username':recv1, 'online':recv2})
		gotUserList.sort(key = getUserListFirstChar)
		resUserList = 1
	
	elif command == 'getMessage':
		if len(data)<2:
			print('num of data error')
			return
		
		if data[3] == 'file':
			gotMessageList.append({'srcUsername':data[1], 'time':data[2], 'type':data[3], 'data':data[4]+' '+data[5]})
			if len(data)<7:
				print('num of data error')
				return
			fileCodeList[data[6]] = {'fileName':data[4], 'data':[], 'srcUsername':data[1], 'fileCode':data[6]}
			pack = packData('getFile', data[6])
			send(pack)
		else:
			gotMessageList.append({'srcUsername':data[1], 'time':data[2], 'type':data[3], 'data':data[4]})
		print(gotMessageList)
	
	
	elif command == 'sendFile':
		if len(data)<2:
			print('num of data error')
			return
		comNum = data[1]
		if comNum == '1':
			if len(data)<3:
				print('num of data error')
				return
			fileCode = data[2]
			resFileCode = 1
	
	elif command == 'getFile':
		if len(data)<3:
			print('num of data error')
			return
		comNum = data[1]
		if comNum == '1':
			if len(data)<5:
				print('num of data error')
				return
			fileCodeList[data[2]]['data'].append({'num':data[3], 'content': data[4]})
		elif comNum == '2':
			fileWrite(fileCodeList[data[2]])
			gotMessageList.append({'srcUsername':fileCodeList[data[2]]['srcUsername'], 'time':getLocalTime(), 'type':'file', 'data':'文件 '+fileCodeList[data[2]]['fileName']+' 收取完成，请到 '+fileSavePath+' 查看。'})
		
	
	else:
		print('error command: ',command, '\ndata: ', data)
			
		


def logIn(username, password):
	global resLogin
	requestData = packData('login', username, password)
	send(requestData)
	while resLogin == 0:
		time.sleep(TIMEOFFSET)
	resLogin = 0
	return loginStatus
	
def signin(username, password):
	global resSignin
	requestData = packData('signin', username, password)
	send(requestData)
	while resSignin == 0:
		time.sleep(TIMEOFFSET)
	resSignin = 0
	return signinStatus

def logOut():
	requestData = packData('logout')
	send(requestData)
	exit(0)
	
def getUserList():
	global resUserList
	requestData = packData('getUserList')
	send(requestData)
	while resUserList == 0:
		time.sleep(TIMEOFFSET)
	resUserList = 0
	return gotUserList

def sendMessage(dstUsername, data):
	requestData = packData('sendMessage', dstUsername, thisUsername, getLocalTime(), 'text', data)
	send(requestData)
	
def getMessage():
	temp = []
	temp.extend(gotMessageList)
	gotMessageList.clear()
	return temp

def fileWrite(fileDic):
	global fileSavePath
	filePath = fileSavePath+'\\'+fileDic['fileCode']+fileDic['fileName']
	fileDic['data'].sort(key = getPackNum)
	with open(filePath, 'wb') as f:
		for block in fileDic['data']:
			f.write(base64.b64decode(block['content'].encode()))
	
def sendFile(dstUsername, filePath):
	global fileCode
	global resFileCode
	global resFileSendEnd
	global lackFilePack

	cutFile = []
	fileSize = 0
	with open(filePath, "rb") as f:
		while True:
			block = f.read(FILESIZ)  # 每次读取固定长度到内存缓冲区
			if block:
				fileSize+=len(block)
				cutFile.append(base64.b64encode(block).decode())
			else:
				break  # 如果读取到文件末尾，则退出
	
	fileName = re.findall(pathFinderWindows, filePath)[0]
	pack = packData('sendMessage', dstUsername, thisUsername, getLocalTime(), 'file', fileName, str(fileSize), str(len(cutFile)))
	send(pack)
	while resFileCode == 0:
		time.sleep(TIMEOFFSET)
	resFileCode = 0
	
	tempFileCode = fileCode
	for th in range(len(cutFile)):
		time.sleep(TIMEOFFSET)
		pack = packData('sendFile', '1', tempFileCode, str(th), cutFile[th])
		send(pack)
		
	pack = packData('sendFile', '2', tempFileCode)
	send(pack)

if __name__ == '__main__':	
	initial()

