# encoding:utf-8
import os

from flask import Blueprint, request, jsonify, send_file
from Godzilla import setting

get_set_anything = Blueprint("get_set_anything",__name__)


@get_set_anything.route("/get_cover/<image_name>")
def get_cover(image_name):
    """
    获取音乐的图片
    :param image_name: 图片名
    :return:
    """
    return send_file(os.path.join(setting.COVER_DIR,image_name))


@get_set_anything.route("/get_music/<music_name>")
def get_music(music_name):
    """
    获取音频文件
    :param music_name: 音频文件名称
    :return:
    """
    return send_file(os.path.join(setting.MUSIC_DIR,music_name))

@get_set_anything.route("/get_qr/<qr_img>")
def get_qr(qr_img):
    """
    获取二维码图片
    :param qr_img: 二维码图片名称
    :return:
    """
    return send_file(os.path.join(setting.QR_CODE_DIR,qr_img))


@get_set_anything.route("/get_chat/<chat_name>")
def get_chat(chat_name):
    """
    获得聊天文件
    :param chat_name: 聊天文件名称
    :return:
    """
    return send_file(os.path.join(setting.CHAT_DIR,chat_name))