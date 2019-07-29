# encoding:utf-8
from pymongo import MongoClient
from aip import AipSpeech,AipNlp

# Mongodb 数据库配置
MONGOCLIENT = MongoClient("127.0.0.1", 27017)
MONGO_DB = MONGOCLIENT["godzilla"]

from redis import Redis
# redis 缓存配置
REDIS_DB = Redis("127.0.0.1",6379,db=7)


RESPONSE_DATA = {
    "CODE": 0,
    "MSG": "",
    "DATA": {}
}


MUSIC_DIR = "Music"
COVER_DIR = "Cover"
QR_CODE_DIR = "Qrcode"
CHAT_DIR = "Chat"
PARTS_DIR = "Parts"     # 固定文件，


APP_ID = '16523814'
API_KEY = 'etju95SSryWpnWqhvAXXKSB6'
SECRET_KEY = '8vjuvGKZCkgi4ripxDQhqi6QGL1p70yl'

AI_CLIENT = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
NLP_CLIENT = AipNlp(APP_ID, API_KEY, SECRET_KEY)

from xpinyin import Pinyin
PINYIN = Pinyin()
