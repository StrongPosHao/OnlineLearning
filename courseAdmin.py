#encoding: utf-8

from flask import Blueprint, render_template,request, redirect, url_for
from exts import db
from models import CourseInfo, ChapterInfo, CourseDoc, CourseVideo
from datetime import datetime

courseAdmin = Blueprint('courseAdmin', __name__)

@courseAdmin.route('/')
def courseAdminPage():
    r'''
    课程管理员页面
    :return:
    '''
    return render_template('courseadmin-page.html')

@courseAdmin.route('/courseManage')
def manageCourse():
    r'''
    课程管理页面
    :return:
    '''
    courses = CourseInfo.query.filter().all()
    return render_template('course-manage.html', courses = courses)

@courseAdmin.route('/changeCourse/<courseId>', methods = ['GET', 'POST'])
def changeCourseInfo(courseId):
    r'''
    修改课程信息页面
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    return render_template('changeCourse.html', course = course, courseAbstract = course.courseAbstract.replace('\r\n', r'\r'))

@courseAdmin.route('/addCourse/', methods = ['GET', 'POST'])
def addCourse():
    r'''
    添加课程页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('addCourse.html')
    else:
        courseId = request.form.get('courseId')
        typeId = request.form.get('typeId')
        courseTitle = request.form.get('courseName')
        courseTeacher = request.form.get('courseTeacher')
        coursePubTime = request.form.get('coursePubTime')
        courseAbstract = request.form.get('courseAbstract')
        courseImage = request.form.get('courseImage')
        course = CourseInfo(courseId=courseId, typeId=typeId, courseTitle=courseTitle, courseTeacher=courseTeacher,
                            coursePubTime=coursePubTime, courseAbstract=courseAbstract, courseImage=courseImage)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('manageCourse'))

@courseAdmin.route('/chapterManage/<courseId>')
def manageChapter(courseId):
    r'''
    章节管理页面
    :param courseId:
    :return:
    '''
    chapters = ChapterInfo.query.filter(ChapterInfo.courseId == courseId).all()
    return render_template('chapter-manage.html', chapters = chapters, courseId = courseId)

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
        return render_template('changeChapter.html', chapter = chapter, course = course, pdf = pdf, video = video)
    else:
        chapName = request.form.get('chapName')
        chapLayer = request.form.get('chapLayer')
        chapter = ChapterInfo(chapId = chapterId, courseId = courseId, chapName = chapName, chapLayer=chapLayer)
        db.session.add(chapter)

        videoPath = request.form.get('videoPath')
        videoName = request.form.get('videoName')
        videoSize = request.form.get('videoSize')
        videoDuration = request.form.get('videoDuration')
        videoPubTime = request.form.get('videoPubTime')
        videoMD5 = request.form.get('videoMD5')
        video = CourseVideo(MD5=videoMD5, chapId=chapterId, courseId=courseId, fileName=videoName, filePath=videoPath,
                            fileSize=videoSize, uploadTime=videoPubTime, fileExt='mp4', isDoc=0, videoDuration=videoDuration)
        db.session.add(video)

        pdfPath = request.form.get('pdfPath')
        pdfName = request.form.get('pdfName')
        pdfSize = request.form.get('pdfSize')
        pdfUploadTime = request.form.get('pdfPubTime')
        pdfMD5 = request.form.get('pdfMD5')
        pdf = CourseDoc(MD5=pdfMD5, chapId=chapterId, courseId=courseId, fileName=pdfName, filePath=pdfPath,
                        fileSize=pdfSize, uploadTime=pdfUploadTime, fileExt='pdf', isDoc=1)
        db.session.add(pdf)

        db.session.commit()
        return redirect(url_for('manageChapter'))

@courseAdmin.route('/addChapter/<courseId>', methods = ['GET', 'POST'])
def addChapter(courseId):
    r'''
    增加章节页面
    :param courseId:
    :return:
    '''
    if request.method == 'GET':
        return render_template('addChapter.html')
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
