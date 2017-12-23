#encoding: utf-8

from flask import Flask, render_template, redirect, request,url_for, session, g
import config
from models import *
from exts import db
from sqlalchemy import or_
from datetime import datetime, timedelta
from decorators import login_required
from sysAdmin import sysAdmin
from courseAdmin import courseAdmin
from couInfo import couInfo
from leaderAdmin import leader
from hashlib import md5
from flask_login import current_user
import socket

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

app.register_blueprint(sysAdmin, url_prefix = '/sysAdmin')
app.register_blueprint(courseAdmin, url_prefix = '/courseAdmin')
app.register_blueprint(couInfo, url_prefix = '/couInfo')
app.register_blueprint(leader, url_prefix = '/leader')

@app.route('/test/')
def test():
    r'''
    用于测试界面能否正常显示
    '''
    pass

@app.route('/')
@login_required
def index():
    r'''
    主页页面
    '''
    return render_template('index.html')

@app.route('/visitors/')
def forVisitors():
    r'''
    为游客准备的主页页面入口
    :return:
    '''
    return render_template('index.html')

@app.route('/admins/')
def foradmins():
    r'''
    为管理员准备的登录入口
    :return:
    '''
    return render_template('admin-login.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    r'''
    登录页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('login.html')
    else:
        userVerify = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter(or_(User.userEmail == userVerify, User.userName == userVerify, User.userPhone == userVerify),
                                     User.userPass == password).first()
        print password
        if user:
            session['user_name'] = user.userName
            session.permanenet = True
            user.lastLogin = datetime.now()
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return render_template('fail.html')

@app.route('/logout/')
def logout():
    r'''
    注销页面
    :return:
    '''
    session.clear()
    return redirect(url_for('login'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    r'''
    注册页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('Register.html')
    else:
        email = request.form.get("email")
        phone = request.form.get("phone")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        signUpdate = datetime.now()
        lastLogin = datetime.now()
        # validate password and password2
        if (not (email and phone and username and password1)):
            return redirect(url_for('register'))
        user = User(userEmail=email, userName=username, userPass=password1, userPhone = phone, signUpDate = signUpdate, lastLogin = lastLogin, studyDuration = 0, frozenDuration = 0)
        db.session.add(user)
        db.session.commit()
        # if user register successfully, redirect to log-in page.
        return redirect(url_for('login'))

@app.route('/forget/', methods=['GET', 'POST'])
def forgetPassword():
    r'''
    忘记密码页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('forget_password.html')
    else:
        email = request.form.get('email')
        phone = request.form.get('phone')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter(User.userEmail == email, User.userPhone == phone).first()
        if user:
            user.userPass = password2
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return "该用户不存在！请检查您所输入的邮箱和手机号是否正确。"

@app.route('/pcenter/')
def personalCenter():
    r'''
    个人中心页面
    :return:
    '''
    commentCount = Comments.query.filter(Comments.userName == g.user.userName).all()
    return render_template('personal_center.html', commentCount = len(commentCount))

@app.route('/pcenter/discuss')
def personalCenterDiscuss():
    r'''
    个人中心讨论页面
    :return:
    '''
    comments = Comments.query.filter(Comments.userName == g.user.userName).order_by("-submitTime")
    replyCountComments = []
    for comment in comments:
        replyCountComment = [comment, len(Comments.query.filter(Comments.rep_cmtId == comment.cmtId).all()),
                             CourseInfo.query.filter(CourseInfo.courseId == comment.courseId).first().courseTitle]
        replyCountComments.append(replyCountComment)
    return render_template('personal_center-discuss.html', replyCountComments = replyCountComments, commentCount = len(comments))

@app.route('/pcenter/reply')
def personalCenterReply():
    r'''
    个人中心回复页面
    :return:
    '''
    replys = Comments.query.filter(Comments.userName == g.user.userName, Comments.rep_cmtId).order_by("-submitTime")
    detailedReplys = []
    for reply in replys:
        detailedReply = [reply, Comments.query.filter(Comments.cmtId == reply.rep_cmtId).first().cmtContent,
                         CourseInfo.query.filter(CourseInfo.courseId == reply.courseId).first().courseTitle]
        detailedReplys.append(detailedReply)
    return render_template('personal_center-reply.html', detailedReplys = detailedReplys)

@app.route('/setting/', methods=['GET', 'POST'])
def setting():
    r'''
    个人信息设置页面
    :return:
    '''
    username = request.form.get('username')
    email = request.form.get('email')
    phone =request.form.get('phone')
    user = User.query.filter(User.userPhone == phone)
    return render_template('setting-id.html')

@app.route('/setpassword/', methods=['GET', 'POST'])
def setPassword():
    r'''
    修改密码页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('setting-pwd.html')
    else:
        oldPassword = request.form.get('password1')
        newPassword1 = request.form.get('password2')
        newPassword2 = request.form.get('password3')
        user = User.query.filter(User.userPass == oldPassword, User.userName == g.user.userName).first()
        if not user:
            return '原密码错误，请重新输入！'
        elif newPassword1 != newPassword2:
            return '新密码两次输入不一致，请检查后再输入！'
        else:
            user.userPass = newPassword1
            db.session.commit()
            return redirect(url_for('success'))

# @app.route('/courseInfo/<courseId>')
# def courseInfo(courseId):
#     r'''
#     课程信息页面，对应课程大纲
#     :param courseId:
#     :return:
#     '''
#     course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
#     type = CourseType.query.filter(CourseType.typeId == course.typeId).first()
#     chapters = ChapterInfo.query.filter(ChapterInfo.courseId == courseId).order_by('chapId')
#     return render_template('study-abstract2.html', course = course, chapters = chapters, type = type.typeName)

# @app.route('/resource/<courseId>')
# def resourceInfo(courseId):
#     r'''
#     课程信息页面，对应学习区
#     :param courseId:
#     :return:
#     '''
#     course = CourseInfo.query.filter(CourseInfo.courseId == courseId).first()
#     chapters = ChapterInfo.query.filter(ChapterInfo.courseId == courseId).order_by('chapId').all()
#     bigChapters = []
#     bigChapter = []
#     innerChapter = []
#     chapId = '00001'
#     i = 0
#     for chapter in chapters:
#         if chapter.chapId[:5] == chapId:
#             bigChapter.append(chapter)
#         else:
#             chapId = chapter.chapId[:5]
#             bigChapters.append(bigChapter)
#             bigChapter = []
#             bigChapter.append(chapter)
#         if i == len(chapters) - 1:
#             bigChapters.append(bigChapter)
#         i += 1
#     return render_template('study-resource2.html', course = course, bigChapters = bigChapters)

@app.route('/success/', methods=['GET', 'POST'])
def success():
    r'''
    用于提示相关成功信息的页面
    :return:
    '''
    return render_template('success.html')

@app.route('/searchCourse/', methods=['GET', 'POST'])
def searchCourse(typeId):
    r'''
    搜索课程功能的接口
    :return:
    '''
    courseName = request.args.get('course')
    courses = CourseInfo.query.filter(or_(CourseInfo.courseTitle == courseName, CourseInfo.typeId == typeId)).all()
    return render_template('course.html', courses = courses)

@app.route('/searchCourse/', methods=['GET', 'POST'])
def searchCourseByType(typeId):
    r'''
    通过课程类型搜索课程的接口
    :param typeId:
    :return:
    '''



@app.route('/searchUser/', methods = ['GET', 'POST'])
def searchuser():
    r'''
    搜索用户的接口
    :return:
    '''
    pass

@app.route('/course/')
def course():
    r'''
    显示对应课程信息的页面
    :return:
    '''
    courses = CourseInfo.query.filter().all()
    return render_template('course.html', courses = courses)

@app.route('/help/')
def help():
    r'''
    帮助信息页面
    :return:
    '''
    pass

@app.route('/leader/')
def leaderPage():
    return render_template('leader-page.html')

@app.route('/courseStatics/')
def courseStatics():
    r'''
    课程统计页面 使用pyecharts
    :return:
    '''
    return render_template('course-statistics.html')



@app.context_processor
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

@app.before_request
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

if __name__ == '__main__':
    # app.run(host=socket.gethostbyname(socket.gethostname()), port=5000)
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=5000)