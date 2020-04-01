from flask import request, render_template, current_app, session, g, redirect, url_for, jsonify

from info import user_login_data
from info.models import User
from info.modules.admin import admin_blu
from info.modules.passport import passport_blu
from info.utils.response_code import RET


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