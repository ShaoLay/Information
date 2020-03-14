from flask import g, render_template
from werkzeug.utils import redirect

from info.modules.profile import profile_blu
from info.utils.common import user_login_data


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
    return render_template("news/user.html", data)
