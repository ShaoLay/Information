import datetime
import random
import time

from flask import request, render_template, current_app, session, g, redirect, url_for, jsonify, abort

from info import user_login_data, db, constants
from info.models import User
from info.modules.admin import admin_blu
from info.modules.passport import passport_blu
from info.utils.response_code import RET
# from manage import app


@admin_blu.route('/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))
        return render_template("admin/login.html")

    # 取到登录的参数
    username = request.form.get('username')
    password = request.form.get('password')
    if not all([username, password]):
        return render_template('admin/login.html', errmsg="缺少参数！")

    try:
        user = User.query.filter(User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="用户名查询失败!")

    if not user:
        return render_template('admin/login.html', errmsg="用户名错误！")

    if user.password != password:
        return render_template('admin/login.html', errmsg="用户名或密码错误！")

    if not user.is_admin:
        return render_template('admin/login.html', errmsg="用户权限错误！")

    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    # session['mobile'] = mobile
    session['is_admin'] = True

    return redirect(url_for('admin.admin_index'))

@admin_blu.route('/index')
@user_login_data
def admin_index():
    user = g.user
    return render_template('admin/index.html', user=user.to_dict())

@passport_blu.route("logout", methods=['POST'])
def logout():
    """
    清除session中的对应登录之后保存的信息
    :return:
    """
    session.pop('user_id', None)
    session.pop('nick_name', None)
    # session.pop('mobile', None)
    session.pop('is_admin', None)

    return jsonify(errno=RET.OK, errmsg="OK！")

@admin_blu.route('/user_count')
def user_count():
    """用户量统计"""

    # 用户总数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 月新增数
    month_count = 0
    # 计算每月开始时间 比如：2018-06-01 00：00：00
    t = time.localtime()
    # 计算每月开始时间字符串
    month_begin = '%d-%02d-01' % (t.tm_year, t.tm_mon)
    # 计算每月开始时间对象
    month_begin_date = datetime.datetime.strptime(month_begin, '%Y-%m-%d')
    try:
        month_count = User.query.filter(User.is_admin==False,User.create_time>month_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 日新增数
    day_count = 0
    # 计算当天的开始时间 比如：2018-06-04 00：00：00
    t = time.localtime()
    day_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    day_begin_date = datetime.datetime.strptime(day_begin, '%Y-%m-%d')
    try:
        day_count = User.query.filter(User.is_admin==False,User.create_time>day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 每日的用户登录活跃量
    # 存放X轴的时间节点
    active_date = []
    # 存放Y轴的登录量的节点
    active_count = []

    # 查询今天开始的时间 06月04日 00:00:00
    # 获取当天开始时时间字符串
    today_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    # 获取当前开始时时间对象
    today_begin_date = datetime.datetime.strptime(today_begin, '%Y-%m-%d')

    for i in range(0, 15):
        # 计算一天开始
        begin_date = today_begin_date - datetime.timedelta(days=i)
        # 计算一天结束
        end_date = today_begin_date - datetime.timedelta(days=(i - 1))

        # 将X轴对应的开始时间记录
        # strptime : 将时间字符串转成时间对象
        # strftime : 将时间对象转成时间字符串
        active_date.append(datetime.datetime.strftime(begin_date, '%Y-%m-%d'))

        # 查询当天的用户登录量
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,User.last_login<end_date).count()
            active_count.append(count)
        except Exception as e:
            current_app.logger.error(e)

    # 反转列表：保证时间线从左到右递增
    active_date.reverse()
    active_count.reverse()

    context = {
        'total_count':total_count,
        'month_count':month_count,
        'day_count':day_count,
        'active_date':active_date,
        'active_count':active_count
    }

    return render_template('admin/user_count.html', context=context)

@admin_blu.route('/user_list')
def user_list():
    """用户列表"""

    # 1.接受参数
    page = request.args.get('p', '1')

    # 2.校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'

    # 3.分页查询用户列表。管理员除外
    users = []
    total_page = 1
    current_page = 1
    try:
        paginate = User.query.filter(User.is_admin==False).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT,False)
        users = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    user_dict_list = []
    for user in users:
        user_dict_list.append(user.to_admin_dict())

    # 4.构造渲染数据
    context = {
        'users':user_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }

    return render_template('admin/user_list.html',context=context)