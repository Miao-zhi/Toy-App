# encoding:utf-8
import os
import time

import requests
from bson import ObjectId

from Godzilla import setting, public_app
from uuid import uuid4

# 百度AI ASR
def ai_asr(filePath):
    """
    识别音频
    :param filePath:
    :return:
    """
    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    # 识别本地文件
    result_dic = setting.AI_CLIENT.asr(get_file_content(f'{filePath}.pcm'), 'pcm', 16000, {
        'dev_pid': 1536,
    })
    if result_dic.get("result"):    # 未识别到内容，或者内容为空
        return result_dic.get("result")[0]
    else:
        return False


# NLP
def ai_NLP(content,toy_id=None):
    """
    自然语言处理
    :param content:
    :param toy_id:
    :return:
    """
    vedio_data = {
        "type":"",
        "filepath":"",
    }
    if "听" in content:     # 如果满足我想听什么
        title = content.split("听",1)[1]
        req_contents = public_app.get_content(title)
        print("contents:",req_contents)

        vedio_data["type"] = "music"
        vedio_data["filepath"] = req_contents.get("music")

    elif "联系" in content:     # 给 什么发消息
        to_user_nikename = content.split("联系",1)[1]
        print("to_user_nikename",to_user_nikename)
        # if to_user_nikename == "他爸爸":
        #     to_user_nikename = "他爸爸"
        # else:
        #     to_user_nikename = "迪迦"
        print("to_user_nikename", to_user_nikename)
        toy = setting.MONGO_DB.Toys.find_one({"_id": ObjectId(toy_id)})

        for friend in toy.get("friend_list"):
            # 将其转为 pinyin  原因是 处理 同音字
            _to_user_nikename = setting.PINYIN.get_pinyin(to_user_nikename)
            friend_nick = setting.PINYIN.get_pinyin(friend.get("friend_nick"))
            friend_remark = setting.PINYIN.get_pinyin(friend.get("friend_remark"))

            if _to_user_nikename in [friend_nick,friend_remark]:
                vedio_data["from_user"] = friend.get("friend_id")
                vedio_data["type"] = "chat"
                vedio_data["filepath"] = ai_TTS(f"与{to_user_nikename}连接成功，点击录音即可发送语音消息")
                break
        else:
            vedio_data["from_user"] = "ai"
            vedio_data["type"] = "chat"
            vedio_data["filepath"] = "no_know.mp3"



    else:   # 不满足，即使闲聊
        vedio_data["type"] = "chat"
        # content = to_tuling(Q)    #  图灵机器人
        # vedio_data["filepath"] = ai_TTS(content)
        vedio_data["filepath"] = "no_know.mp3"  # 需要换成 图灵机器人

    return vedio_data

# TTS
def ai_TTS(content):
    """
    合成语音
    :param content: 需要合成的文本内容
    :return: filename 合成语音
    """

    result = setting.AI_CLIENT.synthesis(content, 'zh', 1, {
        'vol': 5,
        "per": 4,
    })

    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    filename = None
    if not isinstance(result, dict):

        filename = f"{time.time()}.mp3"
        filepath = os.path.join(setting.CHAT_DIR, filename)

        with open(f'{filepath}', 'wb') as f:
            f.write(result)
    else:
        print("Error:", result)
    return f'{filename}'


def to_tuling(Q):
    """
    图灵机器人
    :param Q:
    :return:
    """
    data = {
        "perception": {
            "inputText": {
                "text": ""
            }
        },
        "userInfo": {
            "apiKey": "3091ace0a0ba4db5ac031c94da04b858",
            "userId": "464260"  # 用唯一标识
        }
    }

    data["perception"]["inputText"]["text"] = Q
    res = requests.post("http://openapi.tuling123.com/openapi/api/v2", json=data)
    res_dict = res.json()

    return res_dict.get("results")[0].get("values").get("text")
