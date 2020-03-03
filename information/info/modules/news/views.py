from flask import render_template, session, current_app, g

from . import news_blu
from ...models import User
from ...utils.common import user_login_data


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    data = {
        "user_info":g.user.to_dict() if g.user else None,
    }
    return render_template('news/detail.html', data=data)
