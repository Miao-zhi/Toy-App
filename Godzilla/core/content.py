# encoding:utf-8
import os

from flask import Blueprint, request, jsonify, send_file
from Godzilla import setting

content = Blueprint("content", __name__)


@content.route("/content_list", methods=["POST"])
def content_list():
    """
    获取内容
    :return:
    """
    """ 内容 """
    content_list = list(setting.MONGO_DB.Content.find())

    for index,item in enumerate(content_list):
        content_list[index]["_id"] = str(item["_id"])

    RESPONSE_DATA = setting.RESPONSE_DATA

    RESPONSE_DATA["MSG"] = "获取内容资源列表"
    RESPONSE_DATA["DATA"] = content_list[0:10]

    return jsonify(RESPONSE_DATA)
