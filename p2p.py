#!usr/bin/env python
#-*- coding: utf-8 -*-


import os
import wx
import wx.grid
import requests
from grid import SimpleGrid
import p2p_file_transport
import threading

global flag,name

class EntryFrame(wx.Frame):
    def __init__(self,parent=None,id=-1):
        wx.Frame.__init__(self,parent,id,title=u'P2P下载器',size=(400,220))
        panel = wx.Panel(self)

        self.TextFieldsData = ((u'用户名', (60, 50),wx.TE_LEFT),
                                (u'密码', (60, 80),wx.TE_PASSWORD))
        self.textFields = {}  # 字典类型
        self.CreateTextFields(panel)
        self.CreateButtonBar(panel)

    def CreateButtonBar(self,panel):
        button1 = wx.Button(parent=panel,id=-1,label=u'登录',pos=(100,110))
        font = wx.Font(14,wx.DEFAULT, wx.NORMAL, wx.BOLD)
        button1.SetFont(font)
        self.Bind(wx.EVT_BUTTON,self.LogIn,button1)
        button2 = wx.Button(parent=panel,id=-1,label=u'注册',pos=(100+button1.GetSize().width,110))
        button2.SetFont(font)
        self.Bind(wx.EVT_BUTTON,self.Register,button2)

    def CreateTextFields(self,panel):
        for eachLabel,eachPos,style in self.TextFieldsData:
            self.CreateText(eachLabel,eachPos,style,panel)

    def CreateText(self,label,pos,style,parent):
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        static = wx.StaticText(parent=parent,label=label,id=-1,pos=pos,
                               style=wx.ALIGN_CENTER)
        static.SetFont(font)
        static.SetSize((100,-1))

        textPos = (pos[0] + static.GetSize().width, pos[1])
        self.textFields[label] = wx.TextCtrl(parent=parent,id=-1,
                                             size=(150,-1),pos=textPos,style=style)

    def LogIn(self,event):
        username = self.textFields[u'用户名'].GetValue()
        password = self.textFields[u'密码'].GetValue()
        if len(username) == 0 or len(password) == 0:
            wx.MessageBox(message=u'用户名或密码不能为空',caption=u'警告',style=wx.OK)
        else:
            url = 'http://127.0.0.1:5000/login'
            params = {
                'username': username,
                'password': password
            }
            response = requests.post(url=url, data=params)
            if response.text == u'登录成功':
                #wx.MessageBox(message=u'登录成功',caption=u'提示',style=wx.OK)
                global flag,name
                flag = 1
                name = username
                self.CloseWindow()
            else:
                wx.MessageBox(message=u'登录失败', caption=u'提示', style=wx.OK)

    def Register(self,event):
        username = self.textFields[u'用户名'].GetValue()
        password = self.textFields[u'密码'].GetValue()
        if len(username) == 0 or len(password) == 0:
            wx.MessageBox(message=u'用户名或密码不能为空',caption=u'警告',style=wx.OK)
        else:
            url = 'http://127.0.0.1:5000/register'
            params = {
                'username': username,
                'password': password
            }
            response = requests.post(url=url, data=params)
            if response.text ==u'注册成功':
                wx.MessageBox(message=u'注册成功',caption=u'提示',style=wx.OK)
            else:
                wx.MessageBox(message=u'注册失败', caption=u'提示', style=wx.OK)

    def CloseWindow(self):
        self.Destroy()


class MainFrame(wx.Frame):
    def __init__(self,parent=None,id=-1):
        wx.Frame.__init__(self,parent,id,title=u'P2P下载器 (%s)'%name,size=(1500,600))
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.grid = self.grid_Text = self.grid_staticText = self.grid_button = None
        self.panel = wx.Panel(self)

        button1 = wx.Button(parent=self.panel,label=u'我要共享文件',id=-1,pos=(0,0))
        button1.SetFont(font)
        button1.SetSize((200, -1))
        self.Bind(wx.EVT_BUTTON,self.SelectFile,button1)

        button2 = wx.Button(parent=self.panel,label=u'查看我的共享文件',id=-1,pos=(button1.GetSize().width,0))
        button2.SetFont(font)
        button2.SetSize((200, -1))
        self.Bind(wx.EVT_BUTTON,self.CheckMyFile,button2)

        pos = (button1.GetSize().width+button2.GetSize().width+50,0)
        self.searchText = wx.TextCtrl(parent=self.panel,id=-1,size=(300,-1),pos=pos)

        pos = (button1.GetSize().width+button2.GetSize().width+self.searchText.GetSize().width+50,0)
        button3 = wx.Button(parent=self.panel,label=u'搜索',id=-1,pos=pos)
        button3.SetFont(font)
        self.Bind(wx.EVT_BUTTON,self.Search,button3)


    def SelectFile(self,event):
        import os
        filePath = fileName = ''
        dialog = wx.FileDialog(self,u'选择共享文件',os.getcwd(),'','All File(*.*)|*.*',wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            filePath = dialog.GetPath()
            fileName = dialog.GetFilename()
        dialog.Destroy()
        self.UpdateFileInfo(filePath,fileName)

    def UpdateFileInfo(self,filePath,fileName):
        import os.path
        global name
        fileSize = os.path.getsize(filePath)
        username = name
        url = 'http://127.0.0.1:5000/update_file'
        params = {
            'username': username,
            'filesize': fileSize,
            'filename': fileName,
            'filepath': filePath
        }
        response = requests.post(url=url, data=params)
        if response.text == u'共享文件信息已上传':
            wx.MessageBox(message=u'共享成功', caption=u'提示', style=wx.OK)
        else:
            wx.MessageBox(message=u'未知错误，共享失败', caption=u'提示', style=wx.OK)

    def CheckGrid(self):
        if self.grid :
            self.grid.Destroy()
        if self.grid_Text and self.grid_staticText and self.grid_button:
            self.grid_staticText.Destroy()
            self.grid_Text.Destroy()
            self.grid_button.Destroy()

    def CheckMyFile(self,event):
        self.CheckGrid()
        global name
        url = 'http://127.0.0.1:5000/checkmyfile'
        params = {
            'username': name,
        }
        response = requests.post(url=url, data=params)  #此处返回json数据
        data = response.json()
        if len(data) == 0:
            wx.MessageBox(message=u'对不起！没有共享文件信息\n你可能还没有共享过文件', caption=u'提示', style=wx.OK)
        else:
            showData = []
            for i in range(len(data)):
                showData.append(data[str(i)])
            colLabels = (u'文件名', u'文件大小(字节)',u'文件路径')
            rowLabels = [i for i in range(len(showData))]
            self.grid = SimpleGrid(self.panel,showData,rowLabels,colLabels,pos=(0,50))
            self.grid.SetColSize(col=0, width=200)
            self.grid.SetColSize(col=1, width=200)
            self.grid.SetColSize(col=2,width=300)
            self.grid.SetSize((900,50+18*len(showData)))
            self.grid_staticText = wx.StaticText(self.panel,id=-1,label=u'索引',size=(50,-1),pos=(50,100+18*len(showData)))
            self.grid_Text = wx.TextCtrl(self.panel,id=-1,size=(50,-1),pos=(100,100+18*len(showData)))
            self.grid_button = wx.Button(self.panel,id=-1,pos=(150,100+18*len(showData)),label=u'删除该元数据')
            self.Bind(wx.EVT_BUTTON,self.Delete,self.grid_button)

    def Delete(self,event):
        text = self.grid_Text.GetValue()
        value = self.grid.GetCellValue(row=int(text),col=0)
        url = 'http://127.0.0.1:5000/deletemyfile'
        params = {
            'filename': value
        }
        response = requests.post(url=url, data=params)
        if response.text == u'删除成功':
            wx.MessageBox(message=u'删除元数据成功', caption=u'提示', style=wx.OK)
            self.CheckMyFile(event=None)

    def Search(self,event):
        filename = self.searchText.GetValue()
        url = 'http://127.0.0.1:5000/searchfile'
        params = {
            'filename': filename
        }
        response = requests.post(url=url, data=params)
        data = response.json()
        if len(data) == 0:
            wx.MessageBox(message=u'对不起！没有该文件信息的共享', caption=u'提示', style=wx.OK)
        else:
            self.CheckGrid()
            showData = []
            for i in range(len(data)):
                showData.append(data[str(i)])
            colLabels = (u'共享者', u'文件名', u'文件大小(字节)', u'文件路径',u'状态','IP')
            rowLabels = [i for i in range(len(showData))]
            self.grid = SimpleGrid(self.panel, showData, rowLabels, colLabels, pos=(0, 50))
            self.grid.SetColSize(col=1, width=200)
            self.grid.SetColSize(col=2, width=200)
            self.grid.SetColSize(col=3, width=300)
            self.grid.SetSize((1200, 50 + 18 * len(showData)))
            self.grid_staticText = wx.StaticText(self.panel, id=-1, label=u'索引', size=(50, -1),
                                                 pos=(50, 100 + 18 * len(showData)))
            self.grid_Text = wx.TextCtrl(self.panel, id=-1, size=(50, -1), pos=(100, 100 + 18 * len(showData)))
            self.grid_button = wx.Button(self.panel, id=-1, pos=(150, 100 + 18 * len(showData)), label=u'点击下载')
            self.Bind(wx.EVT_BUTTON, self.Download, self.grid_button)

    def Download(self,event):
        text = self.grid_Text.GetValue()
        filename = self.grid.GetCellValue(row=int(text), col=3)
        destionationIP = self.grid.GetCellValue(row=int(text), col=5)
        if destionationIP == '-':
            wx.MessageBox(message=u'该用户不在线，无法下载', caption=u'提示', style=wx.OK)
        else:
            import os
            local_filename = ''
            dialog = wx.FileDialog(self,u'选择存储路径',os.getcwd(), style=wx.SAVE | wx.OVERWRITE_PROMPT)
            if dialog.ShowModal() == wx.ID_OK:
                local_filename = dialog.GetPath()
            dialog.Destroy()
            if not local_filename :
                wx.MessageBox(message=u'输入文件名', caption=u'提示', style=wx.OK)
            client = p2p_file_transport.TCP_Client(destionationIP,8888,filename,local_filename)
            status,numThread = client.run()
            if status == 1:
                wx.MessageBox(message=u'下载成功\n共创建%d个线程'%numThread, caption=u'提示', style=wx.OK)
            else:
                wx.MessageBox(message=u'下载失败', caption=u'提示', style=wx.OK)

def createTCPServer(ip,port):
    p2p_file_transport.TCP_Server(ip,port)

def createMainFrame():
    app_main = wx.PySimpleApp()
    frame_main = MainFrame()
    frame_main.Show()
    app_main.MainLoop()
    # 退出
    url = 'http://127.0.0.1:5000/loginout'
    params = {
        'username': name,
    }
    response = requests.post(url=url, data=params)
    print response.text


if __name__=='__main__':
    global flag
    flag = 0
    app_entry = wx.PySimpleApp()
    frame_entry = EntryFrame()
    frame_entry.Show()
    app_entry.MainLoop()

    if flag == 1:
        thread = []
        t = threading.Thread(target=createTCPServer,args=('localhost',8888))
        thread.append(t)
        t = threading.Thread(target=createMainFrame,args=())
        thread.append(t)
        thread[0].setDaemon(1)

        for i in range(len(thread)):
            thread[i].start()
    else:
        print u'没有进入主窗口'




