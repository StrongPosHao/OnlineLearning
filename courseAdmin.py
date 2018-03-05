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
    courseInfos = []
    for course in courses:
        courseInfos.append([course, CourseType.query.filter(CourseType.typeId == course.typeId).first().typeName])
    return render_template('course-manage.html', courses = courseInfos, admin = g.admin)

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

        image = request.files['imageFile']
        if image.filename:
            imageUploadpath = os.path.join(r'D:\Programming\PyCharm workspace\OnlineLearning\static\image', secure_filename(image.filename))
            image.save(imageUploadpath)

            course.courseImage = imagePath = 'image/' + image.filename

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

        image = request.files['imageFile']
        imageUploadpath = os.path.join(r'D:\Programming\PyCharm workspace\OnlineLearning\static\image', secure_filename(image.filename))
        image.save(imageUploadpath)

        imagePath = 'image/' + image.filename

        course = CourseInfo(courseId=courseId, typeId=typeId, courseTitle=courseTitle, courseTeacher=courseTeacher,
                            coursePubTime=coursePubTime, courseAbstract=courseAbstract, courseImage=imagePath)
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
    courseTitle = CourseInfo.query.filter(CourseInfo.courseId == courseId).first().courseTitle
    return render_template('chapter-manage.html', chapters = chapters, courseId = courseId, admin = g.admin, courseTitle = courseTitle)

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
        firstId = int(chapter.chapId[:5])
        secondId = int(chapter.chapId[5:10])
        thirdId = int(chapter.chapId[10:15])
        return render_template('changeChapter.html', chapter = chapter, course = course, pdf = pdf, video = video,
                               admin = g.admin, firstId = firstId, secondId = secondId, thirdId = thirdId)
    else:
        chapter.chapName = request.form.get('chapName')
        chapter.chapLayer = request.form.get('chapLayer')

        firstId = request.form.get('firstLayer')
        secondId = request.form.get('secondLayer')
        thirdId = request.form.get('thirdLayer')
        firstId = (5-len(firstId))*'0' + firstId
        secondId = (5-len(secondId))*'0' + secondId
        thirdId = (5-len(thirdId))*'0' + thirdId
        chapId = firstId + secondId + thirdId
        chapter.chapId = chapId
        db.session.add(chapter)
        db.session.commit()

        # 获取视频文件并保存至uploadPath
        videoFile = request.files['videoFile']
        if videoFile.filename:
            basePath = os.path.dirname(__name__)    #当前文件的文件目录
            videoUploadPath = os.path.join(r'D:\Programming\PyCharm workspace\OnlineLearning\static\video', videoFile.filename)
            # videoUploadPath = os.path.join(r'static\video', secure_filename(videoFile.filename))
            videoFile.save(videoUploadPath)

            videoName = videoFile.filename.encode('utf-8')
            videoPath = 'video/' + videoName
            videoSize = round(os.path.getsize(videoUploadPath) / float(1024 * 1024), 2)
            if videoSize == 0:
                videoSize = 1

            videoPubTime = datetime.now()
            videoMD5 = md5_file(videoUploadPath)
            video = CourseVideo(MD5=videoMD5, chapId=chapId, courseId=courseId, fileName=videoName, filePath=videoPath,
                                fileSize=videoSize, uploadTime=videoPubTime, fileExt='mp4', isDoc=0)
            db.session.add(video)

        #获取pdf文件并保存至pdfUploadPath
        pdfFile = request.files['pdfFile']
        if pdfFile.filename:
            pdfUploadPath = os.path.join(r'D:\Programming\PyCharm workspace\OnlineLearning\static\pdf', secure_filename(pdfFile.filename))
            pdfFile.save(pdfUploadPath)

            pdfName = pdfFile.filename
            pdfPath = 'pdf/' + pdfName
            pdfSize = round(os.path.getsize(pdfUploadPath) / float(1024 * 1024), 2)
            if pdfSize == 0:
                pdfSize = 1
            pdfUploadTime = datetime.now()
            pdfMD5 = md5_file(pdfUploadPath)

            pdf = CourseDoc(MD5=pdfMD5, chapId=chapId, courseId=courseId, fileName=pdfName, filePath=pdfPath,
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
    courseTitle = CourseInfo.query.filter(CourseInfo.courseId == courseId).first().courseTitle
    if request.method == 'GET':
        return render_template('addChapter.html', admin = g.admin, courseTitle = courseTitle)
    else:
        firstId = request.form.get('firstLayer')
        secondId = request.form.get('secondLayer')
        thirdId = request.form.get('thirdLayer')
        firstId = (5-len(firstId))*'0' + firstId
        secondId = (5-len(secondId))*'0' + secondId
        thirdId = (5-len(thirdId))*'0' + thirdId
        chapId = firstId + secondId + thirdId
        chapName = request.form.get('chapName')
        chapLayer = request.form.get('chapLayer')
        chapter = ChapterInfo(chapId=chapId, courseId=courseId, chapName=chapName, chapLayer=chapLayer)
        db.session.add(chapter)
        db.session.commit()

        # 获取视频文件并保存至uploadPath
        videoFile = request.files['videoFile']
        if videoFile.filename:
            basePath = os.path.dirname(__name__)  # 当前文件的文件目录
            videoUploadPath = os.path.join(r'D:\Programming\PyCharm workspace\OnlineLearning\static\video',
                                           secure_filename(videoFile.filename))
            # videoUploadPath = os.path.join(r'static\video', secure_filename(videoFile.filename))
            videoFile.save(videoUploadPath)

            videoName = videoFile.filename.encode('utf-8')
            videoPath = 'video/' + videoName
            videoSize = round(os.path.getsize(videoUploadPath) / float(1024 * 1024), 2)
            if videoSize == 0:
                videoSize = 1

            videoPubTime = datetime.now()
            videoMD5 = md5_file(videoUploadPath)
            video = CourseVideo(MD5=videoMD5, chapId=chapId, courseId=courseId, fileName=videoName, filePath=videoPath,
                                fileSize=videoSize, uploadTime=videoPubTime, fileExt='mp4', isDoc=0
                                )
            db.session.add(video)

        # 获取pdf文件并保存至pdfUploadPath
        pdfFile = request.files['pdfFile']
        if pdfFile.filename:
            pdfUploadPath = os.path.join(r'D:\Programming\PyCharm workspace\OnlineLearning\static\pdf',
                                         secure_filename(pdfFile.filename))
            pdfFile.save(pdfUploadPath)

            pdfName = pdfFile.filename.encode('utf-8')
            pdfPath = 'pdf/' + pdfName
            pdfSize = round(os.path.getsize(pdfUploadPath) / float(1024 * 1024), 2)
            if pdfSize == 0:
                pdfSize = 1
            pdfUploadTime = datetime.now()
            pdfMD5 = md5_file(pdfUploadPath)

            pdf = CourseDoc(MD5=pdfMD5, chapId=chapId, courseId=courseId, fileName=pdfName, filePath=pdfPath,
                            fileSize=pdfSize, uploadTime=pdfUploadTime, fileExt='pdf', isDoc=1)
            db.session.add(pdf)

            db.session.commit()
        return redirect(url_for('courseAdmin.addChapter', _external=True, courseId = courseId, courseTitle = courseTitle))

@courseAdmin.route('/delete/<courseId>')
def deleteCourse(courseId):
    r'''
    删除课程
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('courseAdmin.manageCourse'))

@courseAdmin.route('/delete/<courseId>/<chapterId>')
def deleteChapter(courseId, chapterId):
    r'''
    删除章节
    :param courseId, chapterId:
    :return:
    '''
    chapter = ChapterInfo.query.filter(ChapterInfo.courseId == courseId, ChapterInfo.chapId == chapterId).first()
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('courseAdmin.manageChapter', _external=True, courseId = courseId))