from flask import render_template, current_app, session

from . import index_blu
from ... import constants
from ...models import User, News, Category


@index_blu.route('/')
def index():
    """
    主页
    :return:
    """
    # 获取到当前登录用户的id
    user_id = session.get("user_id")
    # 通过id获取登录用户信息
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    news_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    click_news_list = []
    for news in news_list if news_list else []:
        click_news_list.append(news.to_basic_dict())
    # 新闻分类展示
    categories = Category.query.all()
    categories_dicts = []
    for category in categories:
        # 拼接内容
        categories_dicts.append(category.to_dict())

    data = {
        "user_info":user.to_dict() if user else None,
        "click_news_list": click_news_list,
        "categories": categories_dicts,
    }
    return render_template('news/index.html', data=data)

@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')