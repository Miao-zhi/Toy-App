# encoding:utf-8
import os
import time

from Godzilla import setting
import requests
from uuid import uuid4

url = "https://www.ximalaya.com/revision/play/album?albumId=424529&pageNum=1&sort=1&pageSize=10"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
}

response = requests.get(url, headers=headers)
# 获得到需要的数据信息
response = response.json()
# 得到内容列表
content_list = response.get("data").get("tracksAudioPlay")

content_li = []

for content in content_list:
    title = content.get("trackName")

    music_str = content.get("src")

    cover_str = "http:{}".format(content.get("trackCoverPath"))
    # 根据 uuid.uuid4() 来创建文件名
    base_filename = str(uuid4())

    music_filename = base_filename + ".mp3"
    cover_filename = base_filename + ".jpg"

    # 将 音乐信息 和 音乐图片消息保存到本地
    with open(os.path.join("Music",music_filename), "wb") as mf:
        mf.write(requests.get(music_str).content)

    with open(os.path.join("Cover",cover_filename), "wb") as cf:
        cf.write(requests.get(cover_str).content)

    dic = {
        "music": music_filename,
        "cover": cover_filename,
        "title": title,
    }

    content_li.append(dic)

    time.sleep(0.5)
# 统一插入到数据中
setting.MONGO_DB["Content"].insert_many(content_li)

print("采集完成")

