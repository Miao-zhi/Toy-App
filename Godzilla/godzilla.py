# encoding:utf-8
from flask import Flask,request,jsonify,render_template
from Godzilla.core import user,content,get_set_anything,qr,friend,ai
from Godzilla.setting import MONGO_DB

app = Flask(__name__)

app.debug = True

app.register_blueprint(user.user)
app.register_blueprint(content.content)
app.register_blueprint(get_set_anything.get_set_anything)

app.register_blueprint(qr.qr)       # 还得换名字
app.register_blueprint(friend.friend)
app.register_blueprint(ai.ai)


@app.route("/open_toy",methods=["POST"])
def open_toy():
    """
    玩具开机
    :return:
    """
    devices_obj = MONGO_DB.Devices.find_one(request.form.to_dict())

    print(devices_obj)

    if devices_obj: # 设备存在

        toy = MONGO_DB.Toys.find_one({"device_key":devices_obj.get("device_key")})

        if toy: # 玩具已经绑定
            ret =  {
                "code":0,
                "music":"Success.mp3",
                "toy_id":str(toy.get("_id")),
                "name":toy.get("toy_name")
            }
        else:
            ret ={
                "code":"0",
                "music":"Nobind.mp3",
            }
    else:
        ret = {
            "code": "1",
            "music": "Nolic.mp3",
        }

    return jsonify(ret)


@app.route("/web_toy")
def wb():
    return render_template("WebToy.html")


if __name__ == '__main__':
    app.run("0.0.0.0",9527)