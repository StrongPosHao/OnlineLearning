#encoding: utf-8

from flask import Blueprint, redirect, render_template, url_for, request, g,session, flash
from exts import db
from models import *
from datetime import datetime
from decorators import login_required

couInfo = Blueprint('couInfo', __name__, static_folder='static')

@couInfo.route('/<courseId>')
@login_required
def courseInfo(courseId):
    r'''
    课程信息页面，对应课程大纲
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    chapters = ChapterInfo.query.filter(ChapterInfo.courseId == courseId).order_by('chapId')
    type = CourseType.query.filter(CourseType.typeId == course.typeId).first().typeName
    flag = False
    for std in course.stds.all():
        if std.userName == g.user.userName:
            flag = True
    return render_template('study-abstract.html', course = course, chapters = chapters, type = type, flag = flag)

@couInfo.route('/choose/<courseId>')
def chooseCourse(courseId):
    r'''
    选课功能
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    g.user.courseCount.append(course)

    db.session.add(g.user)
    db.session.commit()
    return redirect(url_for('couInfo.resourceInfo', _external=True, courseId = courseId))

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
    return render_template('study-resource.html', course = course, bigChapters = bigChapters)

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
    return render_template('study-video.html', video = video, course = course, pdf = pdf)

@couInfo.route('/discuss/<courseId>/<chapId>', methods = ['GET', 'POST'])
def discuss(courseId, chapId):
    r'''
    讨论区页面（章节）
    :param courseId:
    :param chapId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    comments = Comments.query.filter(Comments.courseId == courseId, Comments.rep_cmtId == None, Comments.chapId != None).order_by("-submitTime") #查找出最顶级的评论并按时间倒序排序
    chapter = ChapterInfo.query.filter(ChapterInfo.courseId == courseId, ChapterInfo.chapId == chapId).first()
    replyCountComments = []
    for comment in comments:
        replyCountComment = [comment, len(Comments.query.filter(Comments.rep_cmtId == comment.cmtId).all())]            #评论以及回复数绑定
        replyCountComments.append(replyCountComment)
    if request.method == 'GET':
        return render_template('study-discuss-chapter.html', replyCountComments = replyCountComments, course = course, chapter = chapter, comments = comments)
    else:
        commentContent = request.form.get('commentArea')
        if commentContent:
            comment = Comments(userName = g.user.userName, chapId = chapId, cmtContent = commentContent, submitTime = datetime.now(), courseId = courseId)
            db.session.add(comment)
            db.session.commit()
        return redirect(url_for('couInfo.discuss', _external=True, courseId=courseId, chapId=chapId))

@couInfo.route('/discuss/<courseId>', methods = ['GET', 'POST'])
def discussAll(courseId):
    r'''
    讨论区页面（全部）
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    comments = Comments.query.filter(Comments.courseId == courseId, Comments.rep_cmtId == None).order_by("-submitTime") #查找出最顶级的评论并按时间倒序排序
    replyCountComments = []
    for comment in comments:
        replyCountComment = [comment, len(Comments.query.filter(Comments.rep_cmtId == comment.cmtId).all())]            #评论以及回复数绑定
        replyCountComments.append(replyCountComment)
    if request.method == 'GET':
        return render_template('study-discuss.html', replyCountComments = replyCountComments, course = course)
    else:
        commentContent = request.form.get('commentArea')
        commentContent.replace('fuck', '****')
        commentContent.replace('shit', '****')
        commentContent.replace('motherfucker', '****')
        commentContent.replace('WTF', '***')
        if commentContent:
            comment = Comments(userName = g.user.userName, cmtContent = commentContent, submitTime = datetime.now(), courseId = courseId)
            db.session.add(comment)
            db.session.commit()
        return redirect(url_for('couInfo.discussAll', _external=True, courseId=courseId))

@couInfo.route('/details/<courseId>/<cmtId>', methods =['GET', 'POST'])
def commentDetail(cmtId, courseId):
    r'''
    评论详情(for 总讨论区)
    :param cmtId:
    :param courseId:
    :return:
    '''
    course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
    replys = Comments.query.filter(Comments.rep_cmtId == cmtId).all()  # 获取该条评论的所有回复
    reReplys = []  # 用来存储评论回复的所有回复
    comment = Comments.query.filter(Comments.cmtId == cmtId).first()  # 提取出特定评论
    for reply in replys:
        reReply = Comments.query.filter(Comments.rep_cmtId == reply.cmtId).all()
        reReply.append(reply)
        reReplys.append(reReply)
    if request.method == 'GET':
        return render_template('study-discuss-details2.html', comment = comment, replys = replys, replyCount = len(replys), reReplys = reReplys, course = course, chapter = None)
    else:
        replyContent = request.form.get('replyArea')
        if replyContent:
            replyComment = Comments(userName=g.user.userName, cmtContent=replyContent, submitTime=datetime.now(), courseId = courseId, rep_cmtId=cmtId)
            db.session.add(replyComment)
            db.session.commit()

        for reply in replys:
            content = request.form.get(str(reply.cmtId))
            if content:
                reReplyComment = Comments(userName = g.user.userName, cmtContent=content, submitTime=datetime.now(),
                                          courseId = courseId, rep_cmtId=reply.cmtId)
                db.session.add(reReplyComment)
                db.session.commit()
                return redirect(url_for('couInfo.commentDetail', _external=True, cmtId = cmtId, courseId = courseId))

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
    replys = Comments.query.filter(Comments.rep_cmtId == cmtId).all()  # 获取该条评论的所有回复
    reReplys = []  # 用来存储评论回复的所有回复
    comment = Comments.query.filter(Comments.cmtId == cmtId).first()  # 提取出特定评论
    for reply in replys:
        reReply = Comments.query.filter(Comments.rep_cmtId == reply.cmtId).all()
        reReply.append(reply)
        reReplys.append(reReply)
    if request.method == 'GET':
        return render_template('study-discuss-details2.html', comment = comment, replys = replys, replyCount = len(replys),
                               reReplys = reReplys, course = course, chapter = chapter)
    else:
        replyContent = request.form.get('replyArea')
        if replyContent:
            replyComment = Comments(userName=g.user.userName, cmtContent=replyContent, submitTime=datetime.now(),
                                    courseId = courseId, rep_cmtId=cmtId)
            db.session.add(replyComment)
            db.session.commit()

        for reply in replys:
            content = request.form.get(str(reply.cmtId))
            if content:
                reReplyComment = Comments(userName = g.user.userName, cmtContent=content, submitTime=datetime.now(),
                                         courseId = courseId, rep_cmtId=reply.cmtId)
                db.session.add(reReplyComment)
                db.session.commit()
                return redirect(url_for('couInfo.chapCommentDetail', _external=True, cmtId = cmtId, courseId = courseId, chapId = chapId))

    return redirect(url_for('couInfo.chapCommentDetail', _external=True, cmtId = cmtId, courseId = courseId, chapId = chapId))

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
        replyComment = Comments(userName=g.user.userName, cmtContent=replyContent, submitTime=datetime.now(), courseId = courseId)
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
        replyComment = Comments(userName=g.user.userName, cmtContent=replyContent, submitTime=datetime.now(), courseId = courseId, chapId = chapId)
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
