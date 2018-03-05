#encoding: utf-8

from flask import Flask, render_template, redirect, request,url_for, session, g, flash
import config
from models import *
from exts import db
from sqlalchemy import or_, not_
from datetime import datetime, timedelta
from decorators import login_required
from sysAdmin import sysAdmin
from courseAdmin import courseAdmin
from couInfo import couInfo
from leaderAdmin import leader
from flask_login import current_user
import socket
import jieba
from md5 import *


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
    types = CourseType.query.filter().all()
    subTypes1 = CourseType.query.filter(CourseType.Cou_typeId == types[0].typeId).all()
    subTypes2 = CourseType.query.filter(CourseType.Cou_typeId == types[1].typeId).all()
    coursesTemp1 = CourseInfo.query.filter(CourseInfo.typeId == types[0].typeId).all()
    coursesTemp2 = CourseInfo.query.filter(CourseInfo.typeId == types[1].typeId).all()
    courses1 = []
    courses2 = []
    for course in coursesTemp1:
        courses1.append([course, len(course.stds.all())])
    for course in coursesTemp2:
        courses2.append([course, len(course.stds.all())])
    return render_template('index.html', types = types, subTypes1 = subTypes1[1:], subTypes2 = subTypes2[1:], courses1 = courses1, courses2 = courses2)

@app.route('/visitors/')
def forVisitors():
    r'''
    为游客准备的主页页面入口
    :return:
    '''
    types = CourseType.query.filter().all()
    subTypes1 = CourseType.query.filter(CourseType.Cou_typeId == types[0].typeId).all()
    subTypes2 = CourseType.query.filter(CourseType.Cou_typeId == types[1].typeId).all()
    coursesTemp1 = CourseInfo.query.filter(CourseInfo.typeId == types[0].typeId).all()
    coursesTemp2 = CourseInfo.query.filter(CourseInfo.typeId == types[1].typeId).all()
    courses1 = []
    courses2 = []
    for course in coursesTemp1:
        courses1.append([course, len(course.stds.all())])
    for course in coursesTemp2:
        courses2.append([course, len(course.stds.all())])
    return render_template('index.html', types = types, subTypes1 = subTypes1[1:], subTypes2 = subTypes2[1:], courses1 = courses1, courses2 = courses2)

@app.route('/admins/', methods = ['GET', 'POST'])
def foradmins():
    r'''
    为管理员准备的登录入口
    :return:
    '''
    if request.method == 'GET':
        return render_template('admin-login.html')
    else:
        adminVerify = request.form.get('adminName')
        password = request.form.get('password')
        adminType = request.form.get('adminType')
        admin = Admin.query.filter(or_(Admin.adminEmail == adminVerify, Admin.adminName == adminVerify, Admin.adminPhone == adminVerify),
                                  Admin.adminPass == password, Admin.adminType == adminType).first()
        if admin:
            session['admin_name'] = admin.adminName
            session.permanenet = True
            admin.lastLogin = datetime.now()
            db.session.add(admin)
            db.session.commit()
            if admin.adminType == '1':
                return redirect(url_for('sysAdmin.sysAdminPage'))
            elif admin.adminType == '2':
                return redirect(url_for('courseAdmin.courseAdminPage'))
            else:
                return redirect(url_for('leader.leaderPage'))
        else:
            flash(('用户名或密码错误，请检查您的输入后重试。').decode('utf-8'))
            return redirect(url_for('foradmins'))

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
        if user:
            if user.frozenDuration > 0:
                flash(("您的账户因" + user.frozenReason.encode('utf-8') + "被冻结" + str(int(user.frozenDuration)) + "天. ").decode('utf-8'))
                return redirect(url_for('login'))
            else:
                session['user_name'] = user.userName
                session.permanenet = True
                user.lastLogin = datetime.now()
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('index'))
        else:
            flash(('用户名或密码错误，请检查您的输入后重试。').decode('utf-8'))
            return redirect(url_for('login'))

@app.route('/logout/')
def logout():
    r'''
    注销页面
    :return:
    '''
    session.clear()
    return redirect(url_for('login'))

@app.route('/adminLogout/')
def adminLogout():
    r'''
    管理员注销页面
    :return:
    '''
    session.clear()
    return redirect(url_for('foradmins'))

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
@login_required
def personalCenter():
    r'''
    个人中心页面
    :return:
    '''
    commentCount = Comments.query.filter(Comments.userName == g.user.userName).all()
    courses = []
    # enrolls = StudyProgress(userName = g.user.userName)
    enrolls = g.user.courseCount.all()
    for enroll in enrolls:
        userCount = len(enroll.stds.all())
        courses.append([CourseInfo.query.filter(CourseInfo.courseId == enroll.courseId).first(), userCount])
    return render_template('personal_center.html', commentCount = len(commentCount), courses = courses)

@app.route('/pcenter/discuss')
@login_required
def personalCenterDiscuss():
    r'''
    个人中心讨论页面
    :return:
    '''
    comments = Comments.query.filter(Comments.userName == g.user.userName, Comments.rep_cmtId == None).order_by("-submitTime")
    commentCount = len(Comments.query.filter(Comments.userName == g.user.userName).all())
    replyCountComments = []
    for comment in comments:
        replyCountComment = [comment, len(Comments.query.filter(Comments.rep_cmtId == comment.cmtId).all()),
                             CourseInfo.query.filter(CourseInfo.courseId == comment.courseId).first().courseTitle]
        replyCountComments.append(replyCountComment)
    return render_template('personal_center-discuss.html', replyCountComments = replyCountComments, commentCount = commentCount)

@app.route('/pcenter/reply')
@login_required
def personalCenterReply():
    r'''
    个人中心回复页面
    :return:
    '''
    commentCount = len(Comments.query.filter(Comments.userName == g.user.userName).all())
    replys = Comments.query.filter(Comments.userName == g.user.userName, Comments.rep_cmtId).order_by("-submitTime")
    detailedReplys = []
    for reply in replys:
        detailedReply = [reply, Comments.query.filter(Comments.cmtId == reply.rep_cmtId).first(),
                         CourseInfo.query.filter(CourseInfo.courseId == reply.courseId).first().courseTitle]
        detailedReplys.append(detailedReply)
    return render_template('personal_center-reply.html', detailedReplys = detailedReplys, commentCount = commentCount)

@app.route('/setting/', methods=['GET', 'POST'])
@login_required
def setting():
    r'''
    个人信息设置页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('setting-id.html')
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        phone =request.form.get('phone')
        g.user.userName = username
        g.user.userEmail = email
        g.user.userPhone = phone
        db.session.add(g.user)
        db.session.commit()
    return redirect(url_for('setting'))

@app.route('/setpassword/', methods=['GET', 'POST'])
@login_required
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
            db.session.commit()
            return redirect(url_for('success'))

@app.route('/success/', methods=['GET', 'POST'])
def success():
    r'''
    用于提示相关成功信息的页面
    :return:
    '''
    return render_template('success.html')

@app.route('/searchCourse/', methods=['GET', 'POST'])
def searchCourse():
    r'''
    搜索课程功能的接口
    :return:
    '''
    courseName = request.args.get('course')
    seg_list = jieba.cut_for_search(courseName)
    types = CourseType.query.filter(CourseType.typeId == CourseType.Cou_typeId).all()
    courses1 = []
    for seg in  seg_list:
        course = CourseInfo.query.filter(CourseInfo.courseTitle.contains(seg)).all()
        courses1 = list(set(courses1 + course))
        courses1.reverse()
    courses = []
    for c in courses1:
        courses.append([c, len(c.stds.all())])
    return render_template('course.html', types = types, courses = courses)

@app.route('/searchCourse/<typeId>', methods=['GET', 'POST'])
def searchCourseByType(typeId):
    r'''
    通过课程类型搜索课程的接口
    :param typeId:
    :return:
    '''
    courseName = request.args.get('course')
    courses = CourseInfo.query.filter(or_(CourseInfo.courseTitle == courseName, CourseInfo.typeId == typeId)).all()
    return render_template('course.html', courses = courses)


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
    types = CourseType.query.filter(CourseType.typeId == CourseType.Cou_typeId).all()
    courses1 = CourseInfo.query.filter().all()
    courses = []
    for course in courses1:
        courses.append([course, len(course.stds.all())])
    return render_template('course.html', types = types, courses = courses)

@app.route('/course/<typeId>')
def subCourse(typeId):
    r'''
    显示出子类型
    :return:
    '''
    typeName = CourseType.query.filter(CourseType.typeId == typeId).first().typeName
    types = CourseType.query.filter(CourseType.typeId == CourseType.Cou_typeId).all()
    subTypes = CourseType.query.filter(CourseType.Cou_typeId == typeId).all()
    courses1 = CourseInfo.query.filter(CourseInfo.typeId == typeId).all()
    courses = []
    for course in courses1:
        courses.append([course, len(course.stds.all())])
    return render_template('course-category-items.html', types = types, subTypes = subTypes[1:], courses = courses, typeName = typeName)

# @app.route('/courseAll/<typeId>')
# def courseAll(typeId):
#     type = CourseType.query.filter(CourseType.typeId == typeId).first()
#     types = CourseType.query.filter(CourseType.typeId == CourseType.Cou_typeId).all()
#     courses1 = CourseInfo.query.filter(or_(CourseInfo.typeId == typeId, CourseType.typeId == type.Cou_typeId)).all()
#     subTypes = CourseType.query.filter(CourseType.Cou_typeId == typeId).all()
#     courses = []
#     for course in courses1:
#         courses.append([course, len(course.stds.all())])
#     return render_template('course-category-items.html', types = types, subTypes = subTypes[1:], coures = courses, typeName = type.typeName)

@app.route('/help')
def help():
    r'''
    帮助信息页面
    :return:
    '''
    return render_template('helper-0.html')

@app.route('/help1')
def help1():
    r'''
    help1.html
    :return:
    '''
    return render_template('helper-1.html')

@app.route('/help2')
def help2():
    r'''
    help2.html
    :return:
    '''
    return render_template('helper-2.html')

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
    上下文处理器
    :return:
    '''
    user_name = session.get('user_name')
    admin_name = session.get('admin_name')
    if user_name:
        user = User.query.filter(User.userName == user_name).first()
        if user:
            return {'user': user}
    elif admin_name:
        admin = Admin.query.filter(Admin.adminName == admin_name).first()
        if admin:
            return {'admin' : admin}
    return {}

@app.before_request
def my_before_request():
    r'''
    请求上下文处理器
    :return:
    '''
    user_name = session.get('user_name')
    if user_name:
        user = User.query.filter(User.userName == user_name).first()
        if user:
            g.user = user

    admin_name = session.get('admin_name')
    if admin_name:
        admin = Admin.query.filter(Admin.adminName == admin_name).first()
        if admin:
            g.admin = admin




if __name__ == '__main__':
    # app.run(host=socket.gethostbyname(socket.gethostname()), port=5000)
    # from werkzeug.contrib.fixers import ProxyFix
    # app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=5000)