# encoding:utf-8
from bson import ObjectId
from flask import Blueprint, request, jsonify
from Godzilla import setting

from Godzilla.core import redis_ele

user = Blueprint('user', __name__)


@user.route("/reg", methods=["POST"])
def reg():
    """
    注册
    :return:
    """
    user_info = request.form.to_dict()
    user = setting.MONGO_DB["user"]

    response_data = setting.RESPONSE_DATA

    if user.find_one({"username": user_info.get("username")}):
        response_data["CODE"] = "1"
        response_data["MSG"] = "注册失败"
        response_data["DATA"] = {}
    else:
        user_info["avatar"] = "baba.jpg" if user_info.get("gender") == 2 else "mama.jpg"
        user_info["bind_toys"] = []
        user_info["friend_list"] = []
        user.insert_one(user_info)
        response_data["CODE"] = "0"
        response_data["MSG"] = "注册成功"
        response_data["DATA"] = {}

    return jsonify(response_data)


@user.route("/login", methods=["POST"])
def login():
    """
    登录
    :return:
    """
    response_data = setting.RESPONSE_DATA
    user_info = request.form.to_dict()

    # 根据 传来的{username,pwd} 去数据库中的查询 userinfo
    userinfo = setting.MONGO_DB.user.find_one(user_info)
    # userinfo 存在提示登录成功,不存在提示登陆失败
    if userinfo:
        userinfo["_id"] = str(userinfo.get("_id"))

        # 根据user_id,在redis 中查询有多少条未读消息
        chat_dic = redis_ele.get_redis_all(to_user=userinfo["_id"])

        userinfo["chat"] = chat_dic

        response_data["CODE"] = "0"
        response_data["MSG"] = "登录成功"
        response_data["DATA"] = userinfo
    else:
        response_data["CODE"] = "1"
        response_data["MSG"] = "登录失败"

    return jsonify(response_data)


@user.route("/auto_login", methods=["POST"])
def auto_login():
    """
    自动登陆
    :return:
    """
    response_data = setting.RESPONSE_DATA
    user_info = request.form.to_dict()

    user_ib = ObjectId(user_info.get("_id"))

    userinfo = setting.MONGO_DB.user.find_one({"_id": user_ib})

    userinfo["_id"] = str(userinfo.get("_id"))

    # 查询有多少条未读消息
    chat_dic = redis_ele.get_redis_all(to_user=userinfo["_id"])
    print("auto_login  (chat_dic):  ",chat_dic)
    userinfo["chat"] = chat_dic

    response_data["CODE"] = "0"
    response_data["MSG"] = "登录成功"
    response_data["DATA"] = userinfo

    return jsonify(response_data)
