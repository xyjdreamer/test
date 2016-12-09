#!usr/bin/env python
#-*- coding: utf-8 -*-
from sqlalchemy import create_engine,Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import  VARCHAR,INTEGER,CHAR
from sqlalchemy import and_,or_,not_
from flask import Flask,request,jsonify

engine = create_engine("mysql+mysqldb://root:mysql@localhost:3306/test")
DBSession = sessionmaker(bind=engine)
BaseModel = declarative_base()
class userInformation(BaseModel):
    __tablename__ = 'userinfo'
    username = Column(VARCHAR(20),primary_key=True)
    password = Column(VARCHAR(12))

class onLine(BaseModel):
    __tablename__ = 'online'
    username = Column(VARCHAR(20), primary_key=True)
    ip = Column(VARCHAR(15))

class fileInformation(BaseModel):
    __tablename__ = 'fileinfo'
    username = Column(VARCHAR(20))
    fileName = Column(VARCHAR(200),primary_key=True)
    fileSize = Column(INTEGER)
    filePath = Column(VARCHAR(500))


app = Flask(__name__)

@app.route('/login',methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        ip = request.remote_addr
        session = DBSession()
        user = session.query(userInformation).filter(and_(userInformation.username == username,
                                                          userInformation.password == password)
                                                     ).count()
        if user == 1:
            #没有在线
            if session.query(onLine).filter(onLine.username==username).count() == 0:
                newOnline = onLine(username=username,ip=ip)
                session.add(newOnline)
            #已在线，更新IP
            else:
                session.query(onLine).filter(onLine.username == username).update({onLine.ip:ip})
            session.commit()
            session.close()
            return u'登录成功'
        else:
            session.close()
            return u'登录失败'

@app.route('/loginout',methods=['POST'])
def loginout():
    if request.method == 'POST':
        username = request.form['username']
        session = DBSession()
        session.query(onLine).filter(onLine.username == username).delete()
        session.commit()
        session.close()
        return u'退出成功'


@app.route('/register',methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session = DBSession()
        user = session.query(userInformation).filter(userInformation.username == username).count()

        if user == 0:
            newUser = userInformation(username=username,password=password)
            session.add(newUser)
            session.commit()
            session.close()
            return u'注册成功'
        else:
            session.close()
            return u'注册失败，该用户名已经被注册'

@app.route('/update_file',methods=['POST'])
def update_file():
    if request.method == 'POST':
        username = request.form['username']
        fileName = request.form['filename']
        fileSize = int(request.form['filesize'])
        filePath = request.form['filepath']
        session = DBSession()
        newSharedFile = fileInformation(username=username,fileName=fileName,filePath=filePath,fileSize=fileSize)
        session.add(newSharedFile)
        session.commit()
        session.close()
        return u'共享文件信息已上传'

@app.route('/checkmyfile',methods=['POST'])
def check_my_file():
    if request.method == 'POST':
        username = request.form['username']
        session = DBSession()
        result = session.query(fileInformation).filter(fileInformation.username == username).all()
        session.close()
        data = {}
        for i,each in enumerate(result):
            data[i] = (each.fileName,each.fileSize,each.filePath)
        resp = app.make_response(jsonify(data))
        return resp

@app.route('/deletemyfile',methods=['POST'])
def delete_my_file():
    if request.method == 'POST':
        filename = request.form['filename']
        session = DBSession()
        session.query(fileInformation).filter(fileInformation.fileName == filename).delete()
        session.commit()
        session.close()
        return u'删除成功'

@app.route('/searchfile',methods=['POST'])
def serach_file():
    if request.method == 'POST':
        filename = request.form['filename']
        session = DBSession()
        if len(filename) == 0:
            result = session.query(fileInformation).all()
        else:
            result = session.query(fileInformation).filter(fileInformation.fileName == filename).all()

        session.close()
        data = {}
        for i, each in enumerate(result):
            userStatus = session.query(onLine).filter(onLine.username == each.username)
            if userStatus.count() == 0:
                data[i] = (each.username,each.fileName, each.fileSize, each.filePath,u'不在线','-')
            else:
                data[i] = (each.username,each.fileName, each.fileSize, each.filePath,u'在线',userStatus[0].ip)

        resp = app.make_response(jsonify(data))
        return resp

if __name__=='__main__':
    app.run(debug=True)