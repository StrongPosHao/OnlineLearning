#encoding: utf-8

from flask import Blueprint, render_template,request, redirect, url_for, g
from exts import db
from models import CourseInfo, ChapterInfo, CourseDoc, CourseVideo,CourseType
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from md5 import md5_file

courseAdmin = Blueprint('courseAdmin', __name__)

@courseAdmin.route('/', methods = ['GET', 'POST'])
def courseAdminPage():
    r'''
    课程管理员页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('courseadmin-page.html', admin = g.admin)
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        g.admin.adminName = name
        g.admin.adminEmail = email
        g.admin.adminPhone = phone
        db.session.add(g.admin)
        db.session.commit()
        return redirect(url_for('courseAdmin.courseAdminPage'))

@courseAdmin.route('/courseManage')
def manageCourse():
    r'''
    课程管理页面
    :return:
    '''
    courses = CourseInfo.query.filter().all()
    return render_template('course-manage.html', courses = courses, admin = g.admin)

@courseAdmin.route('/changeCourse/<courseId>', methods = ['GET', 'POST'])
def changeCourseInfo(courseId):
    r'''
    修改课程信息页面
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    typeName = CourseType.query.filter(CourseType.typeId == course.typeId).first().typeName
    if request.method == 'GET':
        return render_template('changeCourse.html', course = course, courseAbstract = course.courseAbstract.replace('\r\n', r'\r'), type = typeName, admin = g.admin)
    else:
        course.courseTitle = request.form.get('title')
        course.courseTeacher = request.form.get('teacher')
        course.coursePubTime = request.form.get('pubTime')
        course.courseAbstract = request.form.get('abstract')
        type_name = request.form.get('type')
        course.typeId = CourseType.query.filter(CourseType.typeName == type_name).first().typeId
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('courseAdmin.changeCourseInfo', _external=True, courseId = courseId))

@courseAdmin.route('/addCourse/', methods = ['GET', 'POST'])
def addCourse():
    r'''
    添加课程页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('addCourse.html', admin = g.admin)
    else:
        courseId = request.form.get('courseId')
        typeName = request.form.get('type')
        typeId = CourseType.query.filter(CourseType.typeName == typeName).first().typeId
        courseTitle = request.form.get('courseName')
        courseTeacher = request.form.get('courseTeacher')
        coursePubTime = request.form.get('coursePubTime')
        courseAbstract = request.form.get('courseAbstract')
        courseImage = request.form.get('courseImage')
        course = CourseInfo(courseId=courseId, typeId=typeId, courseTitle=courseTitle, courseTeacher=courseTeacher,
                            coursePubTime=coursePubTime, courseAbstract=courseAbstract, courseImage=courseImage)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('courseAdmin.manageCourse'))

@courseAdmin.route('/chapterManage/<courseId>')
def manageChapter(courseId):
    r'''
    章节管理页面
    :param courseId:
    :return:
    '''
    chapters = ChapterInfo.query.filter(ChapterInfo.courseId == courseId).all()
    return render_template('chapter-manage.html', chapters = chapters, courseId = courseId, admin = g.admin)

@courseAdmin.route('/changeChapter/<courseId>/<chapterId>', methods = ['GET', 'POST'])
def changeChapterInfo(courseId, chapterId):
    r'''
    修改章节信息页面
    :param courseId:
    :param chapterId:
    :return:
    '''
    chapter = ChapterInfo.query.filter(ChapterInfo.courseId == courseId, ChapterInfo.chapId == chapterId).first()
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    pdf = CourseDoc.query.filter(CourseDoc.courseId == courseId, CourseDoc.chapId == chapterId).first()
    video = CourseVideo.query.filter(CourseVideo.courseId == courseId, CourseVideo.chapId == chapterId).first()
    if request.method == 'GET':
        return render_template('changeChapter.html', chapter = chapter, course = course, pdf = pdf, video = video, admin = g.admin)
    else:
        chapter.chapName = request.form.get('chapName')
        chapter.chapLayer = request.form.get('chapLayer')
        db.session.add(chapter)


        # 获取视频文件并保存至uploadPath
        videoFile = request.files['videoFile']
        basePath = os.path.dirname(__name__)    #当前文件的文件目录
        videoUploadPath = os.path.join(r'D:\Programming\PyCharm workspace\OnlineLearning\static\video', secure_filename(videoFile.filename))
        # videoUploadPath = os.path.join(r'static\video', secure_filename(videoFile.filename))
        videoFile.save(videoUploadPath)

        videoName = videoFile.filename
        videoPath = 'video/' + videoName
        videoSize = round(os.path.getsize(videoUploadPath) / float(1024 * 1024), 2)
        videoDuration = 10

        videoPubTime = datetime.now()
        videoMD5 = md5_file(videoUploadPath)
        video = CourseVideo(MD5=videoMD5, chapId=chapterId, courseId=courseId, fileName=videoName, filePath=videoPath,
                            fileSize=videoSize, uploadTime=videoPubTime, fileExt='mp4', isDoc=0, videoDuration=videoDuration)
        db.session.add(video)

        #获取pdf文件并保存至pdfUploadPath
        pdfFile = request.files['pdfFile']
        pdfUploadPath = os.path.join(basePath, r'D:\Programming\PyCharm workspace\OnlineLearning\static\video', secure_filename(pdfFile.filename))
        pdfFile.save(pdfUploadPath)

        pdfName = pdfFile.filename
        pdfPath = 'pdf/' + pdfName
        pdfSize = round(os.path.getsize(pdfUploadPath) / float(1024 * 1024), 2)
        pdfUploadTime = datetime.now()
        pdfMD5 = md5_file(pdfUploadPath)

        pdf = CourseDoc(MD5=pdfMD5, chapId=chapterId, courseId=courseId, fileName=pdfName, filePath=pdfPath,
                        fileSize=pdfSize, uploadTime=pdfUploadTime, fileExt='pdf', isDoc=1)
        db.session.add(pdf)

        db.session.commit()
        return redirect(url_for('courseAdmin.manageChapter', _external=True, courseId = courseId, chapterId = chapterId))

@courseAdmin.route('/addChapter/<courseId>', methods = ['GET', 'POST'])
def addChapter(courseId):
    r'''
    增加章节页面
    :param courseId:
    :return:
    '''
    if request.method == 'GET':
        return render_template('addChapter.html', admin = g.admin)
    else:
        chapId = request.form.get('chapId')
        courseId = courseId
        chapName = request.form.get('chapName')
        chapLayer = request.form.get('chapLayer')
        chapter = ChapterInfo(chapId=chapId, courseId=courseId, chapName=chapName, chapLayer=chapLayer)
        db.session.add(chapter)

        videoMD5 = request.form.get('videoMD5')
        videoName = request.form.get('videoName')
        videoPath = request.form.get('videoPath')
        videoSize = request.form.get('videoSize')
        videoUploadTime = request.form.get('videoUploadTime')
        videoFileExt = 'mp4'
        videoIsDoc = '0'
        videoDuration = request.form.get('videoDuration')
        video = CourseVideo(MD5=videoMD5, chapId=chapId, courseId=courseId, fileName=videoName, filePath=videoPath, fileSize=videoSize,
                            uploadTime=datetime.now(), fileExt=videoFileExt, isDoc=videoIsDoc, videoDuration=videoDuration)
        db.session.add(video)

        pdfMD5 = request.form.get('pdfMD5')
        pdfName = request.form.get('pdfName')
        pdfPath = request.form.get('pdfPath')
        pdfSize = request.form.get('pdfSize')
        pdfFileExt = 'pdf'
        pdfIsDoc = 'pdf'
        pdf = CourseDoc(MD5=pdfMD5, chapId=chapId, courseId=courseId, fileName=pdfName, filePath=pdfPath,
                        fileSize=pdfSize, uploadTime=datetime.now(), fileExt=pdfFileExt, isDoc=pdfIsDoc)
        db.session.add(pdf)
        db.session.commit()
        return redirect(url_for('manageChapter'))
