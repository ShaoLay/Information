from flask import render_template, session, current_app, g, abort, request, jsonify

from . import news_blu
from ... import constants, db
from ...models import News, Comment, CommentLike
from ...utils.common import user_login_data
from ...utils.response_code import RET


@news_blu.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    news_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    click_news_list = []
    for news in news_list if news_list else []:
        click_news_list.append(news.to_basic_dict())
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
    # 判断是否收藏新闻, 默认值是false
    is_collected = False
    if g.user:
        if news in g.user.collection_news:
            is_collected = True

    # 获取当前新闻的评论
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comment_like_ids = []
    if g.user:
        # 如果当前用户已登录
        try:
            comment_ids = [comment.id for comment in comments]
            if len(comment_ids) > 0:
                # 取到当前用户在当前新闻的所有评论点赞的记录
                comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                         CommentLike.user_id == g.user.id).all()
                # 取出记录中所有的评论id
                comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)


    comment_list = []
    for item in comments if comments else []:
        comment_dict = item.to_dict()
        comment_dict['is_like'] = False
        # 判断用户是否点赞该评论
        if g.user and item.id in comment_like_ids:
            comment_dict['is_like'] = True
        comment_list.append(comment_dict)


    data = {
        "news": news.to_dict(),
        "user_info": g.user.to_dict() if g.user else None,
        'click_news_list':click_news_list,
        'is_collected': is_collected,
        'comments': comment_list,

    }
    return render_template('news/detail.html', data=data)

@news_blu.route("/news_collect", methods=['POST'])
@user_login_data
def news_collect():
    """
    新闻收藏
    :return:
    """
    user = g.user
    json_data = request.json
    news_id = json_data.get("news_id")
    action = json_data.get("action")

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录！")
    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误！")
    if action not in ("collect", "cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误！")
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败！")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在！")
    if action == "collect":
        user.collection_news.append(news)
    else:
        user.collection_news.remove(news)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存失败！")
    return jsonify(errno=RET.OK, errmsg="操作成功！")

@news_blu.route('/news_comment', methods=["POST"])
@user_login_data
def add_news_comment():
    """
    添加评论
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录！")
    # 获取参数
    data_dict = request.json
    news_id = data_dict.get("news_id")
    comment_str = data_dict.get("comment")
    parent_id = data_dict.get("parent_id")

    if not all([news_id, comment_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全！")
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败！")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在！")

    # 初始化模型, 保存数据
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str
    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存评论数据失败！")

    return jsonify(errno=RET.OK, errmsg="评论成功！", data=comment.to_dict())

@news_blu.route('/comment_like', methods=['POST'])
@user_login_data
def set_comment_like():
    """评论点赞"""
    if not g.user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 获取参数
    comment_id = request.json.get("comment_id")
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    if not all([comment_id, news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全！")

    if action not in ("add", "remove"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误！")

    # 查询评论数据
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败！")
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论数据不存在！")

    if action == 'add':
        comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
        if not comment_like:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = g.user.id
            db.session.add(comment_like)
            # 增加点赞条数
            comment.like_count += 1
        else:
            # 删除点赞数据
            comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
            if comment_like:
                db.session.delete(comment_like)
                comment.like_count -= 1
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollack()
            return jsonify(errno=RET.DBERR, errmsg="操作失败！")
        return jsonify(errno=RET.OK, errmsg="操作成功！")
