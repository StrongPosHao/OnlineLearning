#encoding: utf-8

from flask import Blueprint, render_template, request, redirect, url_for, session, g
from models import User, Admin
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
