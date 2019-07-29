# encoding:utf-8
from flask import Flask, request, jsonify
from geventwebsocket.websocket import WebSocket
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import json

demo = Flask(__name__)

# 玩具
toy_dict = {}

@demo.route("/toy/<toy_id>")
def toy(toy_id):
    """
    toy 登录上 webSocket
    :param toy_id:
    :return:
    """
    print("toy_id:"+toy_id)
    user_socket = request.environ.get("wsgi.websocket")
    toy_dict[toy_id] = user_socket
    while 1:
        msg = user_socket.receive()
        try:
            msg_dict = json.loads(msg)
        except Exception as e:
            print("格式化失败:",e)
            continue
        to_user_id = msg_dict.get("to_user")
        if toy_dict:
            to_socket = toy_dict.get(to_user_id)
            if to_socket:
                to_socket.send(json.dumps(msg_dict))
            else:
                print("没它")


@demo.route("/app/<user_id>")
def app(user_id):
    """
    user 登录上 webSocket
    :param user_id:
    :return:
    """
    print("user_id:"+user_id)
    user_socket = request.environ.get("wsgi.websocket")
    toy_dict[user_id] = user_socket
    while 1:
        msg = user_socket.receive()
        try:
            msg_dict = json.loads(msg)
        except Exception as e:
            print("格式化失败:",e)
            continue
        to_user_id = msg_dict.get("to_user")    # 得到 玩具 id
        if toy_dict:
            to_socket = toy_dict.get(to_user_id)
            if to_socket:
                to_socket.send(json.dumps(msg_dict))
            else:
                print("没它")




if __name__ == '__main__':
    server = WSGIServer(("0.0.0.0", 9528), demo, handler_class=WebSocketHandler)
    server.serve_forever()
