#encoding: utf-8

from flask import Blueprint, render_template, request, redirect, url_for, session, g
from exts import db
from pyecharts import Bar, Pie
from models import *

leader = Blueprint('leader', __name__)

@leader.route('/', methods = ['GET', 'POST'])
def leaderPage():
    r'''
    公司领导页面
    :return:
    '''
    if request.method == 'GET':
        return render_template('leader-page.html', admin = g.admin)
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        g.admin.adminName = name
        g.admin.adminEmail = email
        g.admin.adminPhone = phone
        db.session.add(g.admin)
        db.session.commit()
        return redirect(url_for('leaderPage'))

@leader.route('/statistics')
def courseStatistics():
    r'''
    课程统计页面，使用pyecharts
    :return:
    '''
    types = CourseType.query.filter().all()
    attr = []
    data = []
    for type in types:
        attr.append(type.typeName)
        data.append(len(CourseInfo.query.filter(CourseInfo.typeId == type.typeId).all()))
    bar = Bar()
    bar.add("courseType", attr, data, is_random=True)

    #用户学习课程待完成
    courses = CourseInfo.query.filter().all()
    attr2 = []
    data2 = []
    for course in courses:
        attr2.append(course.courseTitle.encode('utf-8'))
        data2.append(len(course.stds.all()))
    pie = Pie()
    pie.add("", attr2, data2, is_label_show=True, is_random=True)
    return render_template("course-statistics.html", myechart1 = bar.render_embed(), myechart2 = pie.render_embed())

