#------------------------ALL--------------------------------#
# 服务器地址
serverIP = '127.0.0.1'

# 服务器开放的端口
serverPort = 7777

# 每次最多接收多大的TCP包
bufferSize = 65536

# 每次读文件读多少字节
fileReadSize = 1024

# 参数之间的间隔符
argSplit = '\x07\x07'

# 包末尾的结束符
packSplit = '\x07\x08'

# 发文件时每个包之间的时间间隔
timeOffset = 0.005

#------------------------server--------------------------------#

# 服务器将文件存到哪
serverFileSavePath = r'L:\!!Files\workzone\191216\ServerFile'

# 最多同时与几个客户端维持会话
serverListenNumber = 10

# 文件编号开始于
fileCodeStartAt = 11


# SQL数据库地址
sqlIP = "localhost"

# SQL用户名
sqlUsername = "pythonuse"

# SQL密码
sqlPassword = "Pyth0NUs3"

# SQL库名
sqlDB = "pythonuse"

#------------------------cilent--------------------------------#

# 客户端将文件存在哪
cilentFileSavePath = r'L:\!!Files\workzone\191216\CilentFiles'
