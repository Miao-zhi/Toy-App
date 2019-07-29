# encoding:utf-8
import requests
import time
import hashlib
import uuid
import os
from Godzilla import setting


def create_qr_code(num,li):
    """
    通过 'http://qr.liantu.com/api.php?text='  创建二维码信息
    :param num: 数量
    :param li: 存储列表
    :return:
    """
    for i in range(num):
        # 通过 时间戳 和 uuid 创建不同的二维码内容
        qr_code = "{}{}{}".format(time.time(),uuid.uuid4(),time.time()).encode("utf-8")
        # 将上者内容 md5 转换
        qr_code = hashlib.md5(qr_code).hexdigest()
        # 根据随机内容发送请求
        response = requests.get("http://qr.liantu.com/api.php?text={}".format(qr_code))
        # 将内容保存到本地. 并以 md5 值命名
        with open(os.path.join(setting.QR_CODE_DIR,qr_code+".jpg"),"wb") as qf:
            qf.write(response.content)

        dic = {"device_key":qr_code}
        li.append(dic)

if __name__ == '__main__':
    l = []
    create_qr_code(10,l)
    # 将构造信息插入到 "Devices" 表中
    setting.MONGO_DB["Devices"].insert_many(l)


