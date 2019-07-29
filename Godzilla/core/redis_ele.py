# encoding:utf-8
import json
from bson import ObjectId
from Godzilla import setting
from Godzilla.setting import REDIS_DB

"""
场景1：u向i发送3条语音消息
u:{}
i:{u:3}

场景2：i读取了u的消息
u:{}
i:{u:0}

场景3：u向i发送3条语音消息,t向i发送了2条语音消息
u:{}
t:{}
i:{u:3,t:2}

场景4：i读取了u的消息
u:{}
t:{}
i:{u:0,t:2}

将未读消息使用字典的形式：
to_user : {from_user1:1,from_user2:3}
存放在Redis中
"""


def set_redis(from_user, to_user):
    """
    设置未读消息
    :param from_user: app
    :param to_user: toy
    :return:
    """
    print(from_user, to_user)  # 5d01fce97a2e4d9c00b61c6d 5d020262969d398f4d5f6126

    to_user_msg = REDIS_DB.get(to_user)
    print("to_user_msg::", to_user_msg)

    if to_user_msg:
        # 存在，即 toy 有值，判断是否有 from_user 的未读消息，若没有，储存值为一，若有，值加一再保存
        to_user_msg = json.loads(to_user_msg)
        if to_user_msg.get(from_user, ""):
            to_user_msg[from_user] += 1
        else:
            to_user_msg[from_user] = 1
        REDIS_DB.set(to_user, json.dumps(to_user_msg))
    else:
        # 不存在，即设置新值
        REDIS_DB.set(to_user, json.dumps({from_user: 1}))


def set_redis_app(from_user, to_user):
    """
    设置未读消息
    :param from_user:  发送者
    :param to_user: 接收者  也是查看者
    :return:
    """

    print(from_user, to_user)  # 5d020262969d398f4d5f6126 5d01fce97a2e4d9c00b61c6d

    to_user_msg = REDIS_DB.get(to_user)

    if to_user_msg:
        # 存在，即 toy 有值，由于无论 以 from_user 为键 是否有值,都设为 0
        to_user_msg = json.loads(to_user_msg)
        to_user_msg[from_user] = 0
        REDIS_DB.set(to_user, json.dumps(to_user_msg))
    else:
        # 不存在，即设置新址
        REDIS_DB.set(to_user, json.dumps({from_user: 0}))


def get_redis(from_user, to_user):
    """
    toy 查询未读消息
    :param from_user:
    :param to_user:
    :return: 未读消息的数量
    """
    print(from_user, to_user)

    to_user_msg = REDIS_DB.get(to_user)

    user_count = 0
    if to_user_msg:
        to_user_msg = json.loads(to_user_msg)

        # toy_id 存在，判断 from_user 是否存在
        from_user_count = to_user_msg.get(from_user)
        if from_user_count:
            user_count = from_user_count  # 该用户的未读数量
        else:
            # 如果这个用户没有未读数量，则去查询其他的是否还有未读消息
            for _from_user,count in to_user_msg.items():
                if count:   # 不为空
                    from_user = _from_user
                    user_count = count

        to_user_msg[from_user] = 0
        REDIS_DB.set(to_user, json.dumps(to_user_msg))
    else:
        REDIS_DB.set(to_user, json.dumps({from_user: 0}))

    print(from_user,user_count)
    return from_user,user_count


def get_redis_all(to_user):
    """
    app 查询 所有的未读消息
    :param to_user:
    :return:    格式:{"u_1":1,"u_2":2,"count":3} 或 {"count":0}
    """
    to_user_msg = REDIS_DB.get(to_user)
    if to_user_msg:
        # 如果有值, 给其 添加一个 count 键值对
        to_user_msg = json.loads(to_user_msg)
        to_user_msg["count"] = sum(to_user_msg.values())
    else:
        to_user_msg = {"count": 0}

    return to_user_msg
