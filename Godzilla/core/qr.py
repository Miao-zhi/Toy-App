# encoding:utf-8
from bson import ObjectId
from flask import Blueprint, request, jsonify
from Godzilla import setting

qr = Blueprint("qr", __name__)


@qr.route("/scan_qr", methods=["POST"])
def scan_qr():
    """
    扫描二维码
    :return:
    """
    # 获得device_key
    device_key = request.form.to_dict().get("device_key")
    # 根据 device_key 去数据库 Devices 中查询获得 device_info
    devices_info = setting.MONGO_DB.Devices.find_one({"device_key": device_key})

    ret = setting.RESPONSE_DATA
    # 存在
    if devices_info:
        # 存在二维码 是否绑定 去 toy 表中进行查询,存在即绑定,不存在即未绑定
        toy = setting.MONGO_DB.Toys.find_one({"device_key": device_key})
        if toy:
            # 存在在 toys 表中即绑定成功

            ret["CODE"] = 2
            ret["MSG"] = "二维码扫描成功"
            ret["DATA"] = {
                "toy_id": str(toy.get("_id"))
            }
        else:

            ret["CODE"] = 0
            ret["MSG"] = "二维码扫描成功"
            ret["DATA"] = {
                "device_key": device_key
            }


    else:
        ret["CODE"] = 1
        ret["MSG"] = "请扫描玩具二维码"
        ret["DATA"] = {}

    return jsonify(ret)


@qr.route("/bind_toy", methods=["POST"])
def bind_toy():
    """
    绑定玩具
    :return:
    """
    toy_info = request.form.to_dict()
    # print("toy_info",toy_info)
    # user_id
    user_id = toy_info.get("user_id")
    # 根据 user_id 查询出来 用户
    user_obj = setting.MONGO_DB.user.find_one({"_id": ObjectId(user_id)})

    # 创建一个聊天窗口
    chats_info = {
        "user_list": [],  # 用户列表 数据此聊天窗口的用户
        "chat_list": [],
    }
    # 将 聊天窗口 添加到数据库 获得到其 对象
    chars_obj = setting.MONGO_DB.Chats.insert_one(chats_info)       # pymongo.results.InsertOneResult

    # 构建 toy_info
    toy_info["avatar"] = "toy.jpg"
    toy_info["bind_user"] = user_id
    toy_info["friend_list"] = []
    # 构建 玩具的 friend_list 中的信息
    friend_dict = {
        "friend_id": user_id,
        "friend_nick": user_obj.get("nickname"),
        "friend_remark": toy_info.get("remark"),
        "friend_avatar": user_obj.get("avatar"),
        "friend_chat": str(chars_obj.inserted_id),
        "friend_type": "app",
    }
    # 给 玩具添加 app 朋友
    toy_info["friend_list"].append(friend_dict)
    # 创建 toy
    toys_obj = setting.MONGO_DB.Toys.insert_one(toy_info)

    # 构建用户 app 的 friend_list 的信息
    user_friend_dic = {
        "friend_id": str(toys_obj.inserted_id),
        "friend_nick": toy_info.get("toy_name"),
        "friend_remark": toy_info.get("baby_name"),
        "friend_avatar": toy_info.get("avatar"),
        "friend_chat": str(chars_obj.inserted_id),
        "friend_type": "toy"
    }

    # 给 app 中的 bind_toys(绑定信息) 添加 toy 的 _id
    user_obj["bind_toys"].append(str(toys_obj.inserted_id))
    # 添加到 friend_list 中
    user_obj["friend_list"].append(user_friend_dic)
    # 通过 "user._id"  更新 user 表
    setting.MONGO_DB.user.update_one({"_id":ObjectId(user_id)},{'$set': user_obj})


    # 聊天窗口 添加 用户信息
    chats_info["user_list"].append(user_id)
    chats_info["user_list"].append(str(toys_obj.inserted_id))

    # 更新 chats 表
    setting.MONGO_DB.Chats.update_one({"_id": chats_info.get("_id")}, {'$set': chats_info})

    # 返回数据
    ret = setting.RESPONSE_DATA
    ret["CODE"] = 0
    ret["MSG"] = "绑定完成"
    ret["DATA"] = {}

    return jsonify(ret)


@qr.route("/toy_list", methods=["POST"])
def toy_list():
    """
    展示toy
    :return:
    """
    # 根据 user_id 查询出 toys 表中 满足 bind_user == user_id 的所有 toys
    user_id = request.form.to_dict().get("_id")
    toys_li = list(setting.MONGO_DB.Toys.find({"bind_user": user_id}))

    for index,toys in enumerate(toys_li):
        toys_li[index]["_id"] = str(toys.get("_id"))

    ret = setting.RESPONSE_DATA
    ret["CODE"] = 0
    ret["MSG"] = "获取Toy列表"
    ret["DATA"] = toys_li

    return jsonify(ret)
