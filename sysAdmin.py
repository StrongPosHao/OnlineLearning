#encoding: utf-8

from flask import Blueprint, render_template, request, redirect, url_for, session, g
from models import User
from exts import db

sysAdmin = Blueprint('sysAdmin', __name__)

@sysAdmin.route('/', methods = ['GET', 'POST'])
def sysAdminPage():
    r'''
    系统管理员页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('sysadmin-page.html', user = g.user)
    else:
        # About admin
        # userName = request.form.get('username')
        # email = request.form.get('email')
        # phone = request.form.get('phone')
        pass

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
    user的上下文处理器
    :return:
    '''
    user_name = session.get('user_name')
    if user_name:
        user = User.query.filter(User.userName == user_name).first()
        if user:
            return {'user': user}
    return {}

@sysAdmin.before_request
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
