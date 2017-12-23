#encoding: utf-8

from flask import Blueprint, redirect, render_template, url_for, request, g,session, flash
from exts import db
from models import ChapterInfo, CourseType, CourseInfo, CourseVideo, CourseDoc, Comments, User
from datetime import datetime

couInfo = Blueprint('couInfo', __name__, static_folder='static')

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
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    chapter = ChapterInfo.query.filter(ChapterInfo.chapId == chapId).first()
    if request.method == 'GET':
        comments = Comments.query.filter(Comments.courseId == courseId, Comments.chapId == chapId, Comments.rep_cmtId == None).order_by("-submitTime")
        return render_template('study-discuss.html', comments = comments, course = course, chapName = chapter.chapName)
    else:
        commentContent = request.form.get('commentArea')
        comment = Comments(userName = g.user.userName, chapId = chapId, cmtContent = commentContent, submitTime = datetime.now(), isVisible='11111', courseId = courseId)
        db.session.add(comment)
        db.session.commit()
        comments = Comments.query.filter(Comments.courseId == courseId, Comments.chapId == chapId).order_by("-submitTime")
        return render_template('study-discuss.html', comments = comments, course = course)

@couInfo.route('/discuss/<courseId>', methods = ['GET', 'POST'])
def discussAll(courseId):
    r'''
    讨论区页面（全部）
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    comments = Comments.query.filter(Comments.courseId == courseId, Comments.rep_cmtId == None).order_by("-submitTime")
    replyCountComments = []
    for comment in comments:
        replyCountComment = [comment, len(Comments.query.filter(Comments.rep_cmtId == comment.cmtId).all())]
        replyCountComments.append(replyCountComment)
    if request.method == 'GET':
        return render_template('study-discuss.html', replyCountComments = replyCountComments, course = course)
    else:
        commentContent = request.form.get('commentArea')
        if commentContent == '':
            return redirect(url_for('couInfo.discussAll', _external=True, courseId = courseId))
        comment = Comments(userName = g.user.userName, cmtContent = commentContent, submitTime = datetime.now(), isVisible='11111', courseId = courseId)
        db.session.add(comment)
        db.session.commit()
        return render_template('study-discuss.html', replyCountComments = replyCountComments, course = course)

@couInfo.route('/details/<courseId>/<cmtId>', methods =['GET', 'POST'])
def commentDetail(cmtId, courseId):
    r'''
    评论详情(for 总讨论区)
    :param cmtId:
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()

    if request.method == 'GET':
        replys = Comments.query.filter(Comments.rep_cmtId == cmtId).all()  #获取该条评论的所有回复
        reReplys = []                                                      #用来存储评论回复的所有回复
        comment = Comments.query.filter(Comments.cmtId == cmtId).first()   #提取出特定评论
        for reply in replys:
            reReply = Comments.query.filter(Comments.rep_cmtId == reply.cmtId).all()
            reReply.append(reply)
            reReplys.append(reReply)
        return render_template('study-discuss-details.html', comment = comment, replys = replys, replyCount = len(replys), reReplys = reReplys, course = course, chapter = None)
    else:
        replyContent = request.form.get('replyArea')
        replyComment = Comments(userName=g.user.userName, cmtContent=replyContent, submitTime=datetime.now(), isVisible='11111', courseId = courseId, rep_cmtId=cmtId)
        db.session.add(replyComment)
        db.session.commit()
    return redirect(url_for('couInfo.commentDetail', _external=True, cmtId = cmtId, courseId = courseId))

@couInfo.route('/details/<courseId>/<chapId>/<cmtId>', methods =['GET', 'POST'])
def chapCommentDetail(cmtId, courseId, chapId):
    r'''
    评论详情(for 章节讨论区)
    :param cmtId:
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    chapter = ChapterInfo.query.filter(ChapterInfo.chapId == chapId).first()
    if request.method == 'GET':
        replys = Comments.query.filter(Comments.rep_cmtId == cmtId).all()  #获取该条评论的所有回复
        reReplys = []                                                      #用来存储评论回复的所有回复
        comment = Comments.query.filter(Comments.cmtId == cmtId).first()   #提取出特定评论
        for reply in replys:
            reReply = Comments.query.filter(Comments.rep_cmtId == reply.cmtId).all()
            reReply.append(reply)
            reReplys.append(reReply)
        return render_template('study-discuss-details.html', comment = comment, replys = replys, replyCount = len(replys),
                               reReplys = reReplys, course = course, chapter = chapter)
    else:
        replyContent = request.form.get('replyArea')
        replyComment = Comments(userName=g.user.userName, cmtContent=replyContent, submitTime=datetime.now(),
                                isVisible='11111', courseId = courseId, rep_cmtId=cmtId)
        db.session.add(replyComment)
        db.session.commit()
    return redirect(url_for('couInfo.chapCommentDetail'))

@couInfo.route('/details/<courseId>/<reviewId>/<cmtId>', methods = ['GET', 'POST'])
def replyDetailAll(cmtId, courseId, reviewId):
    r'''
    在总讨论区评论的回复详情
    :param cmtId:
    :param courseId:
    :param reviewId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    if request.method == 'GET':
        replys = Comments.query.filter(Comments.rep_cmtId == cmtId).all()  #获取该条评论的所有回复
        reReplys = []                                                      #用来存储评论回复的所有回复
        comment = Comments.query.filter(Comments.cmtId == cmtId).first()   #提取出特定评论
        review = Comments.query.filter(Comments.cmtId == reviewId).first()
        for reply in replys:
            reReply = Comments.query.filter(Comments.rep_cmtId == reply.cmtId).all()
            reReply.append(reply)
            reReplys.append(reReply)
        return render_template('study-reply-details.html', comment = comment, replys = replys, replyCount = len(replys), reReplys = reReplys, review = review, course = course)
    else:
        replyContent = request.form.get('replyArea')
        replyComment = Comments(userName=g.user.userName, cmtContent=replyContent, submitTime=datetime.now(), isVisible='11111', courseId = courseId)
        db.session.add(replyComment)
        db.session.commit()
    return redirect(url_for('replyDetailAll', _external=True, courseId = courseId, reviewId = reviewId))

@couInfo.route('/details/<courseId>/<chapId>/<reviewId>/<cmtId>', methods = ['GET', 'POST'])
def replyDetail(cmtId, courseId, chapId, reviewId):
    r'''
    在指定章节评论的回复详情
    :param cmtId:
    :param courseId:
    :param chapId:
    :param reviewId:
    :return:
    '''
    chapter = ChapterInfo.query.filter(ChapterInfo.chapId == chapId).first()
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    if request.method == 'GET':
        replys = Comments.query.filter(Comments.rep_cmtId == cmtId).all()  #获取该条评论的所有回复
        reReplys = []                                                      #用来存储评论回复的所有回复
        comment = Comments.query.filter(Comments.cmtId == cmtId).first()   #提取出特定评论
        review = Comments.query.filter(Comments.cmtId == reviewId).first()
        for reply in replys:
            reReply = Comments.query.filter(Comments.rep_cmtId == reply.cmtId).all()
            reReply.append(reply)
            reReplys.append(reReply)
        return render_template('study-reply-details.html', comment = comment, replys = replys, replyCount = len(replys), reReplys = reReplys, review = review, chapter = chapter, course = course)
    else:
        replyContent = request.form.get('replyArea')
        replyComment = Comments(userName=g.user.userName, cmtContent=replyContent, submitTime=datetime.now(), isVisible='11111', courseId = courseId, chapId = chapId)
        db.session.add(replyComment)
        db.session.commit()
    return redirect(url_for('replyDetail'))

@couInfo.context_processor
def my_context_processor():
    r'''
    user的上下文处理器
    :return:
    '''
    user_name = session.get('user_name')
    if user_name:
        user = User.query.filter(User.userName == user_name).first()
        if user:
            return {'user': user}
    return {}

@couInfo.before_request
def my_before_request():
    r'''
    user的请求上下文处理器
    :return:
    '''
    user_name = session.get('user_name')
    if user_name:
        user = User.query.filter(User.userName == user_name).first()
        if user:
            g.user = user
