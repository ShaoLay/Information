from flask import g, render_template, request, jsonify, current_app, session
from sqlalchemy.sql.functions import user
from werkzeug.utils import redirect

from info import db
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


@profile_blu.route('/info')
@user_login_data
def get_user_info():
    """
    获取用户信息
    :return:
    """
    user = g.user
    if not user:
        return redirect('/')

    data = {
        "user_info": user.to_dict(),
    }
    # 渲染模板
    return render_template("news/user.html", data=data)

# @profile_blu.route('/base_info', methods=["GET", "POST"])
# @user_login_data
# def base_info():
#     """
#     用户基本信息
#     :return:
#     """
#     user = g.user
#     if request.method == "GET":
#         return render_template('news/user_base_info.html', data={"user_info":user.to_dict()})
#
#     data_dict = request.json
#     nick_name = data_dict.get("nick_name")
#     gender = data_dict.get("gender")
#     signature = data_dict.get("signature")
#     if not all([nick_name, gender, signature]):
#         return jsonify(errno=RET.PARAMERR, errmsg="缺少参数！")
#     if gender not in (['MAN'], 'WOMAN'):
#         return jsonify(errno=RET.PARAMERR, errmsg="参数有误！")
#
#     # 更新并保存参数
#     user.nick_name = nick_name
#     user.gender = gender
#     user.signature = signature
#     try:
#         db.session.commit()
#     except Exception as e:
#         current_app.logger.error(e)
#         db.session.rollback()
#         return jsonify(errno=RET.DBERR, errmsg="保存数据失败！")
#     # 将session中保存的数据进行实时更新
#     session["nick_name"] = nick_name
#
#     # 返回响应
#     return jsonify(errno=RET.OK, errmsg="更新成功！")
#
#
#     # return render_template('news/user_base_info.html', data={"user_info":user.to_dict()})
@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    """
    用户基本信息
    1. 获取用户登录信息
    2. 获取到传入参数
    3. 更新并保存数据
    4. 返回结果
    :return:
    """

    # 1. 获取当前登录用户的信息
    user = g.user
    if request.method == "GET":
        return render_template('news/user_base_info.html', data={"user_info": user.to_dict()})


    # 2. 获取到传入参数
    data_dict = request.json
    nick_name = data_dict.get("nick_name")
    gender = data_dict.get("gender")
    signature = data_dict.get("signature")
    if not all([nick_name, gender, signature]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    if gender not in(['MAN', 'WOMAN']):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 3. 更新并保存数据
    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 将 session 中保存的数据进行实时更新
    session["nick_name"] = nick_name

    # 4. 返回响应
    return jsonify(errno=RET.OK, errmsg="更新成功")