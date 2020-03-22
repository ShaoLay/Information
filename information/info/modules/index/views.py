from flask import render_template, current_app, session, request, jsonify, g

from . import index_blu
from ... import constants
from ...models import User, News, Category
from ...utils import response_code
from ...utils.common import user_login_data
from ...utils.response_code import RET


@index_blu.route('/')
@user_login_data
def index():
    """
    主页
    :return:
    """

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
        "user_info":g.user.to_dict() if g.user else None,
        "click_news_list": click_news_list,
        "categories": categories_dicts,
    }
    return render_template('news/index.html', data=data)

@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')

@index_blu.route('/newslist')
def index_news_list():
    """提供主页新闻列表数据
    """
    # 1.接受参数（分类id,要看第几页，每页几条数据）
    cid = request.args.get('cid', '1')
    page = request.args.get('p', '1')
    per_page = request.args.get('per_page', '10')

    # 2.校验参数 （判断以上参数是否为数字）
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    # 测试用: 添加已审核通过的条件
    # filters = [News.status == 0]
    # if cid != '0':
    #     filters.append(News.category_id == cid)


    # 3.根据参数查询用户想看的新闻列表数据
    if cid == 1:
        # 从所有的新闻中，根据时间倒叙，每页取出10条数据
        # paginate = [News,News,News,News,News,News,News,News,News,News]
        paginate = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
    else:
        # 从指定的分类中，查询新闻，根据时间倒叙，每页取出10条数据
        paginate = News.query.filter(News.category_id==cid).order_by(News.create_time.desc()).paginate(page, per_page, False)

    # 4.构造响应的新闻列表数据
    # news_list = [News,News,News,News,News,News,News,News,News,News]
    # 取出当前页的所有的模型对象
    news_list = paginate.items
    # 读取分页的总页数，将来在主页新闻列表上拉刷新时使用的
    total_page = paginate.pages
    # 读取当前是第几页，将来在主页新闻列表上拉刷新时使用的
    current_page = paginate.page

    # 将模型对象列表转成字典列表，让json在序列化时乐意认识
    # news_dict_list == [{"id":1,"mobile":"18511110000"},{"id":2,"mobile":"18511110001"},...]
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    # 构造响应给客户单的数据
    data = {
        'news_dict_list':news_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }

    # 5.响应新闻列表数据
    return jsonify(errno=response_code.RET.OK, errmsg='OK', data=data)
