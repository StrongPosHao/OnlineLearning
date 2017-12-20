#encoding: utf-8

from flask import Blueprint, redirect, render_template, url_for, request
from exts import db
from models import ChapterInfo, CourseType, CourseInfo, CourseVideo, CourseDoc, Comments
from datetime import datetime

couInfo = Blueprint('couInfo', __name__)

@couInfo.route('/<courseId>')
def courseInfo(courseId):
    r'''
    课程信息页面，对应课程大纲
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    type = CourseType.query.filter(CourseType.typeId == course.typeId).first()
    chapters = ChapterInfo.query.filter(ChapterInfo.courseId == courseId).order_by('chapId')
    return render_template('study-abstract2.html', course = course, chapters = chapters, type = type.typeName)

@couInfo.route('/resource/<courseId>')
def resourceInfo(courseId):
    r'''
    课程信息页面，对应学习区
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    chapters = ChapterInfo.query.filter(ChapterInfo.courseId == courseId).order_by('chapId').all()
    bigChapters = []
    bigChapter = []
    innerChapter = []
    chapId = '00001'
    i = 0
    for chapter in chapters:
        if chapter.chapId[:5] == chapId:
            bigChapter.append(chapter)
        else:
            chapId = chapter.chapId[:5]
            bigChapters.append(bigChapter)
            bigChapter = []
            bigChapter.append(chapter)
        if i == len(chapters) - 1:
            bigChapters.append(bigChapter)
        i += 1
    return render_template('study-resource2.html', course = course, bigChapters = bigChapters)

@couInfo.route('/video/<courseId>/<chapId>')
def video(courseId, chapId):
    r'''
    播放视频页面
    :param courseId:
    :param chapId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    video = CourseVideo.query.filter(CourseVideo.courseId == courseId, CourseVideo.chapId == chapId).first()
    pdf = CourseDoc.query.filter(CourseDoc.courseId == courseId, CourseDoc.chapId == chapId).first()
    return render_template('study-video2.html', video = video, course = course, pdf = pdf)

@couInfo.route('/discuss/<courseId>/<chapId>', methods = ['GET', 'POST'])
def discuss(courseId, chapId):
    r'''
    讨论区页面（章节）
    :param courseId:
    :param chapId:
    :return:
    '''
    if request.method == 'GET':
        comments = Comments.query.filter(Comments.courseId == courseId, Comments.chapId == chapId).all()
        return render_template('study-discuss.html', comments = comments)
    else:
        commentContent = request.form.get('commentArea')
        comment = Comments(userName = g.user.userName, chapId = chapId, cmtContent = commentContent, submitTime = datetime.now(), isVisible='11111', courseId = courseId)
        db.session.add(comment)
        db.session.commit()
        comments = Comments.query.filter(Comments.courseId == courseId, Comments.chapId == chapId).all()
        return render_template('study-discuss.html', comments = comments)

@couInfo.route('/discuss/<courseId>', methods = ['GET', 'POST'])
def discussAll(courseId):
    r'''
    讨论区页面（全部）
    :param courseId:
    :return:
    '''
    if request.method == 'GET':
        comments = Comments.query.filter(Comments.courseId == courseId).all()
        return render_template('study-discuss.html', comments = comments)
    else:
        commentContent = request.form.get('commentArea')
        comment = Comments(userName = g.user.userName, cmtContent = commentContent, submitTime = datetime.now(), isVisible='11111', courseId = courseId)
        db.session.add(comment)
        db.session.commit()
        comments = Comments.query.filter(Comments.courseId == courseId).all()
        return render_template('study-discuss.html', comments = comments)
