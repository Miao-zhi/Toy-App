# encoding:utf-8
from flask import Blueprint, request, jsonify

from bson import ObjectId
from Godzilla import setting
from Godzilla.core import redis_ele

friend = Blueprint("friend", __name__)


@friend.route("/friend_list", methods=["POST"])
def friend_list():
    """
    好友查询
    :return:
    """
    user_id = request.form.to_dict().get("_id")
    user_info = setting.MONGO_DB.user.find_one({"_id": ObjectId(user_id)})

    data = setting.RESPONSE_DATA
    data["CODE"] = "0"
    data["MSG"] = "好友查询"
    data["DATA"] = user_info.get("friend_list")

    return jsonify(data)


@friend.route("/chat_list", methods=["POST"])
def chat_list():
    """
    查看聊天记录
    :return:
    """
    chat_info = request.form.to_dict()
    chat_id = chat_info.get("chat_id")
    to_user = chat_info.get("to_user")  # 接收消息方Id
    from_user = chat_info.get("from_user")  # toy 用户Id
    # 查询聊天记录
    chat_db = setting.MONGO_DB.Chats.find_one({"_id": ObjectId(chat_id)})

    # 存到数据库后就像 redis 中存一条消息记录
    redis_ele.set_redis_app(from_user=from_user, to_user=to_user)

    # 发送数据
    data = setting.RESPONSE_DATA
    data["CODE"] = "0"
    data["MSG"] = "查询聊天记录"
    data["DATA"] = chat_db.get("chat_list")

    return jsonify(data)


@friend.route("/add_req", methods=["POST"])
def add_req():
    """
    添加好友请求成功
    :return:
    """
    """

    {
	"add_user" : "5ca17c7aea512d26281bcb8d", // 发起好友申请方
	"toy_id" : "5ca17f85ea512d215cd9b079", // 收到好友申请方
	"add_type" : "toy", // 发起方的用户类型 app/toy
	"req_info" : "我是仇视单", // 请求信息
	"remark" : "园园", // 发起方对接收方的好友备注


	"avatar" : "toy.jpg", // 发起方的头像
	"nickname" : "背背", // 发起方的名称
	"status" : 1, // 请求状态 1同意 0未处理 2拒绝
	"toy_name" : "圆圆" // 接收方的名称
}


    """
    # 根据接受的request.form, 来拼接 request 表中的内容（add_user 等同于 发送好友方，，，toy_id 等同于 接收方）
    request_info = request.form.to_dict()

    # 发送方
    add_user_id = request_info.get("add_user")
    # print(add_user_id)
    # 接收方
    toy_id = request_info.get("toy_id")
    # nickname 就是 发起方的名称
    add_user_obj = setting.MONGO_DB.Toys.find_one({"_id": ObjectId(add_user_id)})
    # print(add_user_obj)

    if add_user_obj:
        # 如果是 toy
        request_info["nickname"] = add_user_obj.get("baby_name")
    else:
        request_info["nickname"] = setting.MONGO_DB.user.find_one({"_id": ObjectId(add_user_id)}).get("nickname")
    # toy_name 就是接收方的名称
    request_info["toy_name"] = setting.MONGO_DB.Toys.find_one({"_id": ObjectId(toy_id)}).get("baby_name")
    request_info["avatar"] = add_user_obj.get("avatar")
    request_info["status"] = 0

    # 将 信息添加到 Requests 数据库当中
    setting.MONGO_DB.Requests.insert_one(request_info)

    data = setting.RESPONSE_DATA
    data["CODE"] = "0"
    data["MSG"] = "添加好友请求成功"
    data["DATA"] = {}

    return jsonify(data)


@friend.route("/req_list", methods=["POST"])
def req_list():
    """
    查询好友请求
    :return:
    """

    # 获取 用户的 user_id
    user_id = request.form.to_dict().get("user_id")
    print(user_id)
    bind_toys_list = setting.MONGO_DB.user.find_one({"_id": ObjectId(user_id)}).get("bind_toys")
    print(bind_toys_list)
    req_li = list(setting.MONGO_DB.Requests.find({"toy_id": {"$in": bind_toys_list},"status": 0}))
    print(req_li)
    for index, item in enumerate(req_li):
        req_li[index]["_id"] = str(item.get("_id"))

    data = setting.RESPONSE_DATA
    data["CODE"] = "0"
    data["MSG"] = "查询好友请求"
    data["DATA"] = req_li

    return jsonify(data)


@friend.route("/acc_req", methods=["POST"])
def acc_req():
    """
    同意添加好友
    :return:
    """

    req_id = request.form.get("req_id")     # 好友请求信息Id
    friend_remark = request.form.get("remark")  # 为请求方添加备注名称

    # 根据 添加人 id  去 requests 表中
    requests_info = setting.MONGO_DB.Requests.find_one({"_id": ObjectId(req_id)})

    # 得到 toy_id， 也就是被动添加者
    toy_id = requests_info.get("toy_id")
    # 主动发起方的 id   添加人的id ,也就是主动发起方的 id
    add_user = requests_info.get("add_user")

    # 根据 toy_id,req_id  查询到 chat_obj
    chats_info = {
        "user_list": [add_user, toy_id],  # 用户列表 数据此聊天窗口的用户
        "chat_list": [],
    }
    chats_obj = setting.MONGO_DB.Chats.insert_one(chats_info)

    # 将双方添加到通讯论中
    # 向 主动发起方 添加。   由于是主动添加 ，所以知道 对方一定的 玩具   ---- 主动方需要 被动方的 信息，所以这里查询被动方的信息，添加到主动方的 friend_list 中
    toy_info = setting.MONGO_DB.Toys.find_one({"_id": ObjectId(toy_id)})
    friend_dict = {
        "friend_id": toy_id,
        "friend_nick": toy_info.get("baby_name"),
        "friend_remark": requests_info.get("remark"),
        "friend_avatar": toy_info.get("avatar"),
        "friend_chat": str(chats_obj.inserted_id),
        "friend_type": "toy",
    }
    # 查询出 主动添加者
    add_user_info = setting.MONGO_DB.Toys.find_one({"_id": ObjectId(add_user)})
    add_user_info.get("friend_list").append(friend_dict)
    # 更新 主动方的 好友
    setting.MONGO_DB.Toys.update_one({"_id": ObjectId(add_user)}, {'$set': add_user_info})


    # 添加被请求方的 好友        # 需要主动方的信息
    req_toy_info = add_user_info    # 添加者 可能是 toy ,也可能是 user
    print("req_toy_info",req_toy_info)

    req_user_info = setting.MONGO_DB.user.find_one({"_id": ObjectId(add_user)})
    print("req_user_info", req_user_info)

    friend_dict = {
        "friend_id": add_user,
        "friend_nick": req_toy_info.get("baby_name") if req_toy_info else req_user_info.get("nickname"),
        "friend_remark": friend_remark,
        "friend_avatar": req_toy_info.get("avatar") if req_toy_info else req_user_info.get("avatar"),
        "friend_chat": str(chats_obj.inserted_id),
        "friend_type": "toy" if req_toy_info else "app",
    }
    # 更新 被动方的 好友    # 查询被动方
    toy_obj_info = toy_info
    # if req_toy_info:
    #     print("我是玩具",req_toy_info)
    toy_obj_info["friend_list"].append(friend_dict)
    setting.MONGO_DB.Toys.update_one({"_id": ObjectId(toy_id)}, {'$set': toy_obj_info})
    # else:
    #     print("我不是玩具", req_toy_info)
    #     req_user_info["friend_list"].append(friend_dict)
    #     setting.MONGO_DB.user.update_one({"_id": ObjectId(toy_id)}, {'$set': toy_obj_info})

    # 将 请求状态改为 1
    setting.MONGO_DB.Requests.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": 1}})
    data = setting.RESPONSE_DATA
    data["CODE"] = "0"
    data["MSG"] = "同意添加好友"
    data["DATA"] = {}

    return jsonify(data)


@friend.route("/ref_req", methods=["POST"])
def ref_req():
    """
    拒绝添加好友
    :return:
    """

    # 根据 req_id ,将 status 改为 2
    req_id = request.form.get("req_id")
    setting.MONGO_DB.Requests.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": 2}})

    data = setting.RESPONSE_DATA
    data["CODE"] = "0"
    data["MSG"] = "拒绝添加好友"
    data["DATA"] = {}

    return jsonify(data)
