#encoding: utf-8

from flask import Blueprint, render_template, request, redirect, url_for
from models import User
from exts import db

sysAdmin = Blueprint('sysAdmin', __name__)

@sysAdmin.route('/')
def sysAdminPage():
    r'''
    系统管理员页面
    :return:
    '''
    return render_template('sysadmin-page.html')

@sysAdmin.route('/test1/')
def test():
    return 'test'

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
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('manageUser'))
