from flask import render_template, session, current_app, g, abort

from . import news_blu
from ... import constants, db
from ...models import News
from ...utils.common import user_login_data


@news_blu.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    # 查询新闻详情
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    if not news:
        # 返回数据未找到的页面
        abort(404)
    # 累加点击量
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
    data = {
        "news": news.to_dict(),
        "user_info": g.user.to_dict() if g.user else None,
        'news_clicks':news_clicks,
    }
    return render_template('news/detail.html', data=data)