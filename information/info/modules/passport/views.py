import errno

from flask import request, current_app, make_response, jsonify

from . import passport_blu
from ... import redis_store, constants
from ...utils.captcha.captcha import captcha
from ...utils.response_code import RET


@passport_blu.route('/image_code')
def get_image_code():
    """
    获取图片验证码
    :return:
    """
    # 1. 获取到当前的图片编号id
    code_id = request.args.get('code_id')
    # 生成验证码
    name, text, image = captcha.generate_captcha()
    try:
        # 保存当前生成的图片验证码内容
        redis_store.setex('ImageCode_' + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg="保存图片验证码失败！"))
    resp = make_response(image)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp
