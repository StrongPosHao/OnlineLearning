#encoding: utf-8

from flask import Blueprint, render_template, request, redirect, url_for, session, g
from exts import db
from pyecharts import Bar
from models import CourseInfo

leader = Blueprint('leader', __name__)

@leader.route('/')
def leaderPage():
    r'''
    公司领导页面
    :return:
    '''
    return render_template('leader-page.html')

@leader.route('/statistics')
def courseStatistics():
    r'''
    课程统计页面，使用pyecharts
    :return:
    '''
    attr = [u'计算机', u'经济管理', u'软件工程']
    computer = CourseInfo.query.filter(CourseInfo.typeId == 1).all()
    economic = CourseInfo.query.filter(CourseInfo.typeId == 2).all()
    se = CourseInfo.query.filter(CourseInfo.typeId == 11).all()
    data = [len(computer), len(economic), len(se)]
    bar = Bar('Course statistics', "Based on course type.")
    bar.add("courseType", attr, data)

    #用户学习课程待完成

    return render_template("course-statistics.html", myechart1 = bar.render_embed())

