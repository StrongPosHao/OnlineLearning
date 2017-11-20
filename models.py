#encoding: utf-8

from exts import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

class User(db.Model):
    __tablename__ = 'User'
    userName = db.Column(db.String(20), primary_key=True)
    userEmail = db.Column(db.String(64), nullable=False)
    userPhone = db.Column(db.CHAR(11), nullable=False)
    userPass = db.Column(db.CHAR(40), nullable=False)
    signUpDate = db.Column(db.DateTime, default=datetime.now() ,nullable=False)
    lastLogin = db.Column(db.DateTime, nullable=False)
    studyDuration = db.Column(db.Integer, nullable=False)
    frozenDuration = db.Column(db.Integer, nullable=False)

class Admin(db.Model):
    __tablename__ = 'Admin'
    adminName = db.Column(db.String(20), primary_key=True)
    adminEmail = db.Column(db.String(64), nullable=False)
    adminPhone = db.Column(db.CHAR(11), nullable=False)
    adminPass = db.Column(db.CHAR(40), nullable=False)
    adminType = db.Column(db.CHAR(6), nullable=False)
    lastLogin = db.Column(db.DateTime, nullable=False)

class Log(db.Model):
    __tablename__ = 'Log'
    logId = db.Column(db.CHAR(40), primary_key=True)
    logTime = db.Column(db.DateTime, nullable=False)
    logContent = db.Column(db.String(5), nullable=False)

class UserLog(db.Model):
    __tablename__ = 'UserLog'
    logId = db.Column(db.CHAR(40), primary_key=True)
    userName = db.Column(db.String(20), db.ForeignKey('User.userName'), nullable=False)
    logTime = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    logContent = db.Column(db.String(5), nullable=False)

class AdminLog(db.Model):
    __tablename__ = 'AdminLog'
    logId = db.Column(db.CHAR(40), primary_key=True)
    adminName = db.Column(db.String(20), db.ForeignKey('Admin.adminName'), nullable=False)
    logTime = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    logContent = db.Column(db.String(5), nullable=False)

class CourseInfo(db.Model):
    __tablename__ = 'CourseInfo'
    courseId = db.Column(db.CHAR(8), primary_key=True)
    typeId = db.Column(db.Integer, db.ForeignKey('CourseType.typeId'), nullable=False)
    courseTitle = db.Column(db.String(64), nullable=False)
    courseTeacher = db.Column(db.String(20), nullable=False)
    coursePubTime = db.Column(db.DateTime, nullable=False)
    courseAbstract = db.Column(db.Text, nullable=False)

class CourseType(db.Model):
    __tablename__ = 'CourseType'
    typeId = db.Column(db.Integer, primary_key=True)
    Cou_typeId = db.Column(db.Integer, db.ForeignKey('CourseType.typeId'), nullable=False)
    typeName = db.Column(db.String(20), nullable=False)

class ChapterInfo(db.Model):
    __tablename__ = 'ChapterInfo'
    chapId = db.Column(db.CHAR(15), primary_key=True)
    courseId = db.Column(db.CHAR(8), db.ForeignKey('CourseInfo.courseId'), nullable=False)
    chapName = db.Column(db.String(64), nullable=False)
    chapLayer = db.Column(db.SmallInteger, nullable=False)

StudyProgress = db.Table('StudyProgress', db.Column('userName', db.String(20), db.ForeignKey('User.userName'), primary_key=True),
                                          db.Column('chapId', db.CHAR(15), db.ForeignKey('ChapterInfo.chapId'), primary_key=True)
                        )

class Comments(db.Model):
    __tablename__ = 'Comments'
    cmtId = db.Column(db.CHAR(10), primary_key=True)
    userName = db.Column(db.String(20), db.ForeignKey('User.userName'), nullable=False)
    chapId = db.Column(db.CHAR(15), db.ForeignKey('ChapterInfo.chapId'), nullable=False)
    cmtContent = db.Column(db.Text, nullable=False)
    submitTime = db.Column(db.DateTime, nullable=False)
    isVisible = db.Column(db.CHAR(5), nullable=False)

class CourseRsc(db.Model):
    __tablename__ = 'CourseRsc'
    MD5 = db.Column(db.CHAR(40), primary_key=True)
    chapId = db.Column(db.CHAR(15), db.ForeignKey('ChapterInfo.chapId'), nullable=False)
    fileName = db.Column(db.String(64), nullable=False)
    filePath = db.Column(db.String(256), nullable=False)
    fileSize = db.Column(db.Integer, nullable=False)
    uploadTime = db.Column(db.DateTime, nullable=False)
    fileExt = db.Column(db.CHAR(4), nullable=False)
    isDoc = db.Column(db.Boolean, nullable=False)

class CourseDoc(db.Model):
    __tablename__ = 'CourseDoc'
    MD5 = db.Column(db.CHAR(40), primary_key=True)
    chapId = db.Column(db.CHAR(15), db.ForeignKey('ChapterInfo.chapId'), nullable=False)
    fileName = db.Column(db.String(64), nullable=False)
    filePath = db.Column(db.String(256), nullable=False)
    fileSize = db.Column(db.Integer, nullable=False)
    uploadTime = db.Column(db.DateTime, nullable=False)
    fileExt = db.Column(db.CHAR(4), nullable=False)
    isDoc = db.Column(db.Boolean, nullable=False)

class CourseVideo(db.Model):
    __tablename__ = 'CourseVideo'
    MD5 = db.Column(db.CHAR(40), primary_key=True)
    chapId = db.Column(db.CHAR(15), db.ForeignKey('ChapterInfo.chapId'), nullable=False)
    fileName = db.Column(db.String(64), nullable=False)
    filePath = db.Column(db.String(256), nullable=False)
    fileSize = db.Column(db.Integer, nullable=False)
    uploadTime = db.Column(db.DateTime, nullable=False)
    fileExt = db.Column(db.CHAR(4), nullable=False)
    isDoc = db.Column(db.Boolean, nullable=False)
    videoDuration = db.Column(db.Integer, nullable=False)
