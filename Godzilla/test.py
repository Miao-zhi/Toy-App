from xpinyin import Pinyin
# pin = Pinyin()
# test1 = pin.get_pinyin("132")   #默认分割符为-
# print(test1)
#
# test2 = pin.get_pinyin("大河向东流", "")
# print(test2)
# import requests

# url = "http://fjdx.sc.chinaz.net/Files/DownLoad/sound1/201406/4582.mp3"

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
# }
#
# response = requests.get(url, headers=headers)
#
# with open("send_sound_亲吻.mp3","wb") as f:
#     f.write(response.content)
# print(response.content)
from scipy.io import wavfile
import os

# filepath = r"D:\Python_test\studay\flask-web\Godzilla\Music\send_sound_正确的声音.wav"
# os.system(f"ffmpeg -y  -i {filepath}  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {filepath}.pcm")
# os.system(f"ffmpeg -i {filepath} {filepath}.wav")

# def ha(s,d):
#     da = wavfile.read(s)
#     wavfile.write(d,da[0],da[1]//3)
#     print("ok")
# ha(f"{filepath}","resu.wav")
#

