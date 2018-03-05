#encoding: utf-8

from flask import Blueprint, render_template, request, redirect, url_for, session, g
from models import User, Admin, CourseType, CourseInfo
from exts import db

sysAdmin = Blueprint('sysAdmin', __name__)

@sysAdmin.route('/', methods = ['GET', 'POST'])
def sysAdminPage():
    r'''
    系统管理员页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('sysadmin-page.html', admin = g.admin)
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        phone =request.form.get('phone')
        g.admin.adminName = name
        g.admin.adminEmail = email
        g.admin.adminPhone = phone
        db.session.add(g.admin)
        db.session.commit()
        return redirect(url_for('sysAdmin.sysAdminPage'))

@sysAdmin.route('/userManage/')
def manageUser():
    r'''
    用户管理页面
    :return:
    '''
    users = User.query.filter().all()
    return render_template('user-manage.html', users = users)

@sysAdmin.route('/freezeUser/<userName>', methods = ['GET', 'POST'])
def freezeUser(userName):
    r'''
    冻结用户页面
    :param userName:
    :return:
    '''
    user = User.query.filter(User.userName == userName).first()
    if request.method == 'GET':
        return render_template('freezeUser.html', user = user)
    else:
        frozenDuration = request.form.get('frozenDuration')
        frozenReason = request.form.get('frozenReason')
        user.frozenDuration = frozenDuration
        user.frozenReason = frozenReason
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('sysAdmin.manageUser'))

@sysAdmin.route('/typeManage/')
def manageType():
    r'''
    课程类型管理页面
    :return:
    '''
    types = CourseType.query.filter().all()
    detailTypes = []
    for type in types:
        courseCount = len(CourseInfo.query.filter(CourseInfo.typeId == type.typeId).all())
        parentType = CourseType.query.filter(CourseType.typeId == type.Cou_typeId).first().typeName
        detailTypes.append([type, courseCount, parentType])
    return render_template('courseType-manage.html', types = detailTypes)

@sysAdmin.route('/changeType/<typeId>', methods = ['GET', 'POST'] )
def modifyCourseType(typeId):
    r'''
    类别信息修改页面
    :return:
    '''
    type = CourseType.query.filter(CourseType.typeId == typeId).first()
    courseCount = len(CourseInfo.query.filter(CourseInfo.typeId == type.typeId).all())
    parentType = CourseType.query.filter(CourseType.typeId == type.Cou_typeId).first().typeName
    if request.method == 'POST':
        typeName = request.form.get('typeName')
        typeId = int(request.form.get('typeId'))
        parentTypeId = CourseType.query.filter(CourseType.typeName == request.form.get('parentType')).first().typeId
        type.Cou_typeId = parentTypeId
        type.typeName = typeName
        db.session.add(type)
        db.session.commit()
    return render_template('modifyCourseType.html', type = type, courseCount = courseCount, parentType = parentType)

@sysAdmin.route('/addCourseType', methods = ['GET', 'POST'])
def addCourseType():
    r'''
    新增课程类型页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('addCourseType.html')
    else:
        typeName = request.form.get('typeName')
        parentTypeId = CourseType.query.filter(CourseType.typeName == request.form.get('parentType')).first().typeId
        type = CourseType(typeName = typeName, Cou_typeId = parentTypeId)
        db.session.add(type)
        db.session.commit()
    return redirect(url_for('sysAdmin.manageType'))

@sysAdmin.context_processor
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

@sysAdmin.before_request
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
