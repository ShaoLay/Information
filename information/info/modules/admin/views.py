from flask import request, render_template, current_app, session

from info.models import User
from info.modules.admin import admin_blu


@admin_blu.route('/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
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

    return "登录成功, 需要跳转到主页！"
