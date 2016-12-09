#!usr/bin/env python
#-*- coding: utf-8 -*-
import SocketServer
import time
import os
import os.path
import socket
import threading

'''
服务端
'''
#定义一个类
class FtpServer(SocketServer.BaseRequestHandler):

    def setthread(self,filename):
        thread = []
        fileSize = os.path.getsize(filename)
        baseOffset = 1024 * 1024 * 10  #文件超过10M就多线程发送
        numThread = fileSize / baseOffset
        while numThread > 20:  #20个socket封顶,不能无限增长
            baseOffset *= 2  #单个socket发送的字节数翻倍
            numThread = fileSize / baseOffset

        port = self.client_address[1]+1

        for i in range(numThread):
                t = threading.Thread(target=self.sendblock,args=(filename,baseOffset*i,baseOffset,port+i))
                thread.append(t)
        t = threading.Thread(target=self.sendblock,args=(filename,baseOffset*numThread,fileSize%baseOffset,port+numThread))
        thread.append(t)
        #发送ready信号
        self.request.send('ready %d %d %d' % (numThread, fileSize, port))
        return thread

    def sendblock(self,filename,offset,size,port):
        fp = open(filename,'rb')
        fp.seek(offset)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print (self.client_address[0],port)
        s.connect((self.client_address[0],port))
        count = 0
        while count < size:
            data = fp.read(4096)
            s.send(data)
            if not data:
                break
            count += 4096
        s.close()
        fp.close()

    #定义发送文件方法
    def sendfile(self, filename):
        print "starting send file!"
        thread = self.setthread(filename)
        reply = self.request.recv(4096)   #等待接收端创建好相应的线程
        print 'reply:',reply
        if reply == 'ready':
            for i in range(len(thread)):
                thread[i].start()
            for i in range(len(thread)):
                thread[i].join()
            print "send file success!"
        else:
            print 'error reply'

    #SocketServer的一个方法
    def handle(self):
        print "get connection from :",self.client_address
        while True:
            try:
                filename = self.request.recv(4096)
                print "get data:", filename
                if not filename:
                    print "break the connection!"
                    break
                else:
                    if os.path.exists(filename):
                        self.sendfile(filename)
                    else:
                        self.request.send('noexist 0 0 0')
                        continue
            except Exception,e:
                print "get error at:",e

def TCP_Server(host,port):
    s = SocketServer.ThreadingTCPServer((host, port), FtpServer)
    s.serve_forever()


'''
客户端
'''
class TCP_Client():
    def __init__(self,ip,port,remote_filename=None,local_filename=None):
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.remote_filename = remote_filename
        self.local_filename = local_filename

    def setthread(self, port,numThread,fileSize):
        thread = []
        baseOffset = 1024 * 1024 * 10  # 文件超过10M就多线程发送

        for i in range(numThread):
            t = threading.Thread(target=self.recvblock, args=(i,baseOffset, port + i))
            thread.append(t)
        t = threading.Thread(target=self.recvblock,
                             args=(numThread, fileSize % baseOffset, port + numThread))
        thread.append(t)
        self.s.send('ready')   #发送ready信号
        return thread

    def recvblock(self,i,size,port):
        filename = 'part_%d'%i
        fp = open(filename,'wb')
        temp_s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        temp_s.bind((self.ip,port))
        temp_s.listen(1)

        print 'waiting for connect...'
        tcpCliSock,addr = temp_s.accept()
        print '...connect from:',addr
        while True:
            data = tcpCliSock.recv(4096)
            if not data:
                break
            fp.write(data)
        tcpCliSock.close()
        temp_s.close()
        fp.close()

    def recvfile(self, client_command):
        self.s.send(client_command)
        data = self.s.recv(4096)
        status,numThread,fileSize,port = data.split()

        if status == 'ready':
            thread = self.setthread(int(port),int(numThread),int(fileSize))
            for i in range(len(thread)):
                thread[i].start()
            for i in range(len(thread)):
                thread[i].join()
            return  len(thread),int(fileSize)
        elif status == 'noexist':
            print u'该用户不存在此文件'
            return 0,0
        else:
            print u'未知错误'
            return 0,0

    def mergetempfile(self,num,filesize,filename):
        fp = open(filename,'wb')
        for i in range(num):
            f = open('part_%d'%i,'rb')
            while True:
                data = f.read(1024*16)
                if not data:
                    break
                fp.write(data)
            f.close()
            os.remove('part_%d'%i)
        fp.close()

    def run(self):
        try:
            status = 0
            self.s.connect((self.ip, self.port))
            client_command = self.remote_filename
            num,fileSize = self.recvfile(client_command)
            if num != 0 and fileSize != 0:
                self.mergetempfile(num, fileSize, self.local_filename)
                status = 1
                print 'success'
        except socket.error, e:
            print "get error as", e
        finally:
            self.s.close()
            return status,num