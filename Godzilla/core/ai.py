# encoding:utf-8
import time
import os
from uuid import uuid4
from bson import ObjectId
from Godzilla import setting
from Godzilla import setting_ai
from Godzilla.core import redis_ele
from flask import Blueprint, request, jsonify

from Godzilla.setting_ai import ai_TTS

ai = Blueprint("ai", __name__)


@ai.route("/ai_uploader", methods=["POST"])
def ai_uploader():
    """
    toy 录制语音上传
    :return:
    """
    toy_id = request.form.to_dict().get("toy_id")
    file = request.files.to_dict().get("reco")
    # 设置文件名
    filename = f'{uuid4()}.wav'
    filepath = os.path.abspath(os.path.join(setting.CHAT_DIR, filename))
    file.save(filepath)

    os.system(f"ffmpeg -y  -i {filepath}  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {filepath}.pcm")
    os.remove(filepath)

    # 百度AI ASR  # 识别音频内容
    content = setting_ai.ai_asr(filepath)
    print("content:", content)
    if content:
        # NLP   # 相对应的内容转换为音频,并返回其文件名
        vedio_data = setting_ai.ai_NLP(content, toy_id)
        print("vedio_data:  ", vedio_data)
    else:
        vedio_data = {
            "filepath":"no_know.mp3"
        }

    # 返回语音消息  返回音乐
    if vedio_data.get("from_user"):
        # 如果存在即属于 玩具主动发起 聊天
        data = {
            "from_user": vedio_data.get("from_user"),
            "chat": vedio_data.get("filepath"),
        }

    elif vedio_data.get("type") == "music":
        # 如果存在即属于 玩具主动发起 听音乐
        data = {
            "from_user": "ai",
            "music": vedio_data.get("filepath"),
        }
    else:
        # 都不属于 就是闲聊
        data = {
            "from_user": "ai",
            "chat": vedio_data.get("filepath"),
        }

    return jsonify(data)


@ai.route("/app_uploader", methods=["POST"])
def app_uploader():
    """
    上传 app 命令
    :return:
    """
    re_info = request.form.to_dict()
    file = request.files.to_dict().get("reco_file")
    # 将其命令语音文件都保存到 chat 文件夹中
    filepath = os.path.join(setting.CHAT_DIR, file.filename)
    # 保存文件
    file.save(filepath)

    # 将文件转为 MP3 格式
    os.system(f"ffmpeg -i {filepath} {filepath}.mp3")
    # 删除原文件
    os.remove(filepath)

    # 将文件信息 以及接收者和发送者等 保存到 Chats 数据库中
    to_user = re_info.get("to_user")  # 接收者
    from_user = re_info.get("user_id")  # 发送者
    # 更新到数据库
    chat_dic = {
        "from_user": from_user,
        "to_user": to_user,
        "chat": f"{file.filename}.mp3",
        "createTime": time.time()
    }

    chat_obj = setting.MONGO_DB.Chats.find_one({"user_list": {"$all": [to_user, from_user]}})
    chat_obj["chat_list"].append(chat_dic)
    setting.MONGO_DB.Chats.update({"_id": chat_obj.get("_id")}, {"$set": chat_obj})

    # 存到数据库后就向 redis 中增加一条消息记录
    redis_ele.set_redis(from_user, to_user)

    """返回的数据不直接读取，返回一条 提示消息"""
    filename = create_vedio(from_user, to_user)

    # 返回数据
    data = setting.RESPONSE_DATA
    data["CODE"] = 0,
    data["MSG"] = "上传成功",
    data["DATA"] = {
        "filename": f"{filename}",  # 提示音
        "friend_type": "app",
    }

    return jsonify(data)


def create_vedio(from_user, to_user):
    # 根据 toy_id  找到 firend_list 中与 from_id 相符合的 昵称  # 注意一下注释是为了测试快，
    friend_remark = "未知"
    toys = setting.MONGO_DB.Toys.find_one({"_id": ObjectId(to_user)})
    print("toys",toys)
    # if toys:
    for friend in toys.get("friend_list", ""):
        # print(friend)
        if friend["friend_id"] == from_user:  # 匹配，合成提示音
            friend_remark = friend["friend_remark"]
    content = f"宝贝，你有一条来自{friend_remark}的消息"
    filename = setting_ai.ai_TTS(content)
    # else:
    #     filename = "msg_tips.mp3"


    return filename


@ai.route("/toy_uploader", methods=["POST"])
def toy_uploader():
    """
    toy 回复语音
    :return:
    """
    to_user = request.form.get("to_user")  # 发送对象
    from_user = request.form.get("user_id")  # 发送者

    # 根据 to_user 和 from_user 查询 Chats
    chat_obj = setting.MONGO_DB.Chats.find_one({"user_list": {"$all": [to_user, from_user]}})

    if not chat_obj:  # 没有这个聊天窗口
        return

    file = request.files.to_dict().get("reco")
    file_path = os.path.join(setting.CHAT_DIR, file.filename)
    # 保存文件
    file.save(file_path)
    # 由于穿过的文件名固定为 board ,所以需要利用时间戳确定文件名
    filename = str(time.time())
    new_filepath = os.path.join(setting.CHAT_DIR, filename)
    os.system(f"ffmpeg -i {file_path} {new_filepath}.mp3")
    os.remove(file_path)

    # 更新到数据库
    chat_dic = {
        "from_user": from_user,
        "to_user": to_user,
        "chat": f"{filename}.mp3",
        "createTime": time.time()
    }

    chat_obj["chat_list"].append(chat_dic)
    setting.MONGO_DB.Chats.update({"_id": chat_obj.get("_id")}, {"$set": chat_obj})

    # 存到数据库后就像 redis 中存一条消息记录
    redis_ele.set_redis(from_user, to_user)

    filename = create_vedio(from_user, to_user)

    data = setting.RESPONSE_DATA
    data["CODE"] = 0,
    data["MSG"] = "上传成功",

    # 返回数据
    data["DATA"] = {
        "filename": f"{filename}",
        "friend_type": "app",
        "code": 0,  # 播放发送成功的声音
    }

    return jsonify(data)


@ai.route("/recv_msg", methods=["POST"])
def recv_msg():
    """
    未读消息存储
    :return:
    """
    # 查询Chats
    from_user = request.form.get("from_user")
    to_user = request.form.get("to_user")

    # 获取共有多少条未读消息,并且将未读消息数量设为0
    from_user, count = redis_ele.get_redis(from_user, to_user)

    chat = setting.MONGO_DB.Chats.find_one({"user_list": {"$all": [from_user, to_user]}})
    print("count :  ", count)

    chat_list = []
    if count != 0:
        # 判断是 玩具给 app 发送 还是 app 给玩具发送
        chat_li = chat.get("chat_list")
        index = 0
        while len(chat_list) != count:
            new_chat = chat_li[len(chat_li) - 1 - index]
            index += 1
            if new_chat.get("from_user") == from_user:  # 不接受自己发送给别人的消息
                chat_list.append(new_chat)
        # 根据 to_user ,寻找 from_user 与 friend_list 中相等 ，将昵称 和 数量 合成一个提示音
        friend_list = setting.MONGO_DB.Toys.find_one({"_id": ObjectId(to_user)}).get("friend_list", "")
        for friend in friend_list:
            if friend.get("friend_id") == from_user:
                tip_dic = {
                    "from_user": "ai",
                    "chat": ai_TTS(f"以下是来自{friend.get('friend_remark')}的{count}条消息"),
                    "create_time": str(time.time())
                }
                chat_list.append(tip_dic)
        """
            这里可以做转换，添加第几条消息
        """
    else:
        chat_list = [
            {
                "from_user": "ai",
                "chat": "no_unread_message.mp3",
                "create_time": str(time.time())
            }
        ]
    print("chat_list:  ", chat_list)

    msg = {
        "from_user":from_user,
        "data": chat_list,
        "from_user_type":"app" if setting.MONGO_DB.user.find_one({"_id":ObjectId(from_user)}) else "toy",
    }


    return jsonify(msg)
