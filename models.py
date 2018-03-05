#encoding: utf-8

from exts import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

Enroll = db.Table('Enroll', db.Column('userName', db.Unicode(20), db.ForeignKey('User.userName'), primary_key=True),
                            db.Column('courseId', db.CHAR(8), db.ForeignKey('CourseInfo.courseId'), primary_key=True),
                        )

class User(db.Model):
    __tablename__ = 'User'
    userName = db.Column(db.Unicode(20), primary_key=True)
    userEmail = db.Column(db.Unicode(64), nullable=False)
    userPhone = db.Column(db.CHAR(11), nullable=False)
    userPass = db.Column(db.Unicode(100), nullable=False)
    signUpDate = db.Column(db.DateTime, default=datetime.now() ,nullable=False)
    lastLogin = db.Column(db.DateTime, nullable=False)
    studyDuration = db.Column(db.Float, nullable=False)
    frozenDuration = db.Column(db.Float, nullable=False)
    frozenReason = db.Column(db.Text)
    courseCount = db.relationship('CourseInfo', secondary = Enroll, backref = db.backref('stds', lazy = 'dynamic'), lazy = 'dynamic')

class Admin(db.Model):
    __tablename__ = 'Admin'
    adminName = db.Column(db.Unicode(20), primary_key=True)
    adminEmail = db.Column(db.Unicode(64), nullable=False)
    adminPhone = db.Column(db.CHAR(11), nullable=False)
    adminPass = db.Column(db.CHAR(40), nullable=False)
    adminType = db.Column(db.CHAR(6), nullable=False)
    lastLogin = db.Column(db.DateTime, nullable=False)

class UserLog(db.Model):
    __tablename__ = 'UserLog'
    logId = db.Column(db.CHAR(40), primary_key=True)
    userName = db.Column(db.Unicode(20), db.ForeignKey('User.userName'), nullable=False)
    logTime = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    logContent = db.Column(db.Text, nullable=False)

class AdminLog(db.Model):
    __tablename__ = 'AdminLog'
    logId = db.Column(db.CHAR(40), primary_key=True)
    adminName = db.Column(db.Unicode(20), db.ForeignKey('Admin.adminName'), nullable=False)
    logTime = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    logContent = db.Column(db.Text, nullable=False)

class CourseInfo(db.Model):
    __tablename__ = 'CourseInfo'
    courseId = db.Column(db.CHAR(8), primary_key=True)
    typeId = db.Column(db.Integer, db.ForeignKey('CourseType.typeId'), nullable=False)
    courseTitle = db.Column(db.Unicode(64), nullable=False)
    courseTeacher = db.Column(db.Unicode(20), nullable=False)
    coursePubTime = db.Column(db.DateTime, nullable=False)
    courseAbstract = db.Column(db.Text, nullable=False)
    courseImage = db.Column(db.Unicode(256), nullable=False)

class CourseType(db.Model):
    __tablename__ = 'CourseType'
    typeId = db.Column(db.Integer, primary_key=True)
    Cou_typeId = db.Column(db.Integer, db.ForeignKey('CourseType.typeId'), nullable=False)
    typeName = db.Column(db.Unicode(20), nullable=False)

class ChapterInfo(db.Model):
    __tablename__ = 'ChapterInfo'
    chapId = db.Column(db.CHAR(15), primary_key=True)
    courseId = db.Column(db.CHAR(8), db.ForeignKey('CourseInfo.courseId'), primary_key=True,  nullable=False)
    chapName = db.Column(db.Unicode(64), nullable=False)
    chapLayer = db.Column(db.SmallInteger, nullable=False)

class Comments(db.Model):
    __tablename__ = 'Comments'
    cmtId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rep_cmtId = db.Column(db.Integer, db.ForeignKey('Comments.cmtId'), nullable=True)
    userName = db.Column(db.Unicode(20), db.ForeignKey('User.userName'), nullable=False)
    chapId = db.Column(db.CHAR(15), db.ForeignKey('ChapterInfo.chapId'), nullable=True)
    courseId = db.Column('courseId', db.CHAR(8), db.ForeignKey('CourseInfo.courseId'), nullable=False)
    cmtContent = db.Column(db.Text, nullable=False)
    submitTime = db.Column(db.DateTime, nullable=False)

class CourseRsc(db.Model):
    __tablename__ = 'CourseRsc'
    MD5 = db.Column(db.CHAR(40), primary_key=True)
    chapId = db.Column(db.CHAR(15), db.ForeignKey('ChapterInfo.chapId'), nullable=False)
    courseId = db.Column(db.CHAR(8), db.ForeignKey('CourseInfo.courseId'), nullable=False)
    fileName = db.Column(db.Unicode(256), nullable=False)
    filePath = db.Column(db.Unicode(256), nullable=False)
    fileSize = db.Column(db.Integer, nullable=False)
    uploadTime = db.Column(db.DateTime, nullable=False)
    fileExt = db.Column(db.CHAR(4), nullable=False)
    isDoc = db.Column(db.Boolean, nullable=False)

class CourseDoc(db.Model):
    __tablename__ = 'CourseDoc'
    MD5 = db.Column(db.CHAR(40), primary_key=True)
    chapId = db.Column(db.CHAR(15), db.ForeignKey('ChapterInfo.chapId'), nullable=False)
    courseId = db.Column(db.CHAR(8), db.ForeignKey('CourseInfo.courseId'), nullable=False)
    fileName = db.Column(db.Unicode(256), nullable=False)
    filePath = db.Column(db.Unicode(256), nullable=False)
    fileSize = db.Column(db.Integer, nullable=False)
    uploadTime = db.Column(db.DateTime, nullable=False)
    fileExt = db.Column(db.CHAR(4), nullable=False)
    isDoc = db.Column(db.Boolean, nullable=False)

class CourseVideo(db.Model):
    __tablename__ = 'CourseVideo'
    MD5 = db.Column(db.CHAR(40), primary_key=True)
    chapId = db.Column(db.CHAR(15), db.ForeignKey('ChapterInfo.chapId'), nullable=False)
    courseId = db.Column(db.CHAR(8), db.ForeignKey('CourseInfo.courseId'), nullable=False)
    fileName = db.Column(db.Unicode(256), nullable=False)
    filePath = db.Column(db.Unicode(256), nullable=False)
    fileSize = db.Column(db.Integer, nullable=False)
    uploadTime = db.Column(db.DateTime, nullable=False)
    fileExt = db.Column(db.CHAR(4), nullable=False)
    isDoc = db.Column(db.Boolean, nullable=False)
