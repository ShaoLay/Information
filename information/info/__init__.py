import redis

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

from config import Config


db = SQLAlchemy()
redis_store = None

def create_app(config_name):
    """通过传入不通的配置名字, 初始化其对应的应用实例"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    global redis_store
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
    CSRFProtect(app)
    Session(app)
    return app
