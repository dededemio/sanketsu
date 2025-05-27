import time
from datetime import datetime, timedelta
import socket
import sys
import getpass
import os
import json
from mqtt_pub import MQTT_Pub # MQTTパブリッシャクラス

# プラットフォームを取得
def get_platform():
    if sys.platform == "win32" or sys.platform == "cygwin" or sys.platform == "msys":
        return "windows"
    if sys.platform.startswith("linux"):
        return "linux"

# ファイルから最新値の読み込み
def read_env_data():
    # プラットフォームの取得
    platform = get_platform()

    # 今日の日付を取得、0:00の場合まだファイル作成前なので前日にする
    today = datetime.now()
    if today.hour==0 and today.minute==0:
        today = today - timedelta(days=1)

    # WindowsでCO2換気モニターを使っている場合
    if platform=="windows":
        user = getpass.getuser()
        folder = os.path.join(r"C:\Users", user, r"AppData\Local\I-O_DATA\CO2換気モニター.exe_Url_flegl41yev3u0r0b0ykag1c51i0d412p\1.1.0.0\logs")
        filename = today.strftime("log%Y%m%d.txt")
        with open(os.path.join(folder, filename), "r") as f:
            last_line = f.readlines()[-1]
        values = last_line.strip().split(",")
        dt = values[0][0:19]
        co2 = int(values[2].split(":")[1].strip())
        temperature = float(values[3].split(":")[1].strip())
        humidity = float(values[4].split(":")[1].strip())

    # Raspberry Piでsanketsuを使っている場合
    else:
        folder = "./log"
        files = os.listdir(folder)
        newest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(folder, f)))
        with open(os.path.join(folder, newest_file), "r", encoding="utf_8_sig") as f:
            last_line = f.readlines()[-1]
        data = last_line.rstrip("\n").split(",")
        dt = data[0].replace("/", "-")
        temperature = float(data[1])
        humidity = float(data[2])
        co2 = int(data[3])

    return dt, temperature, humidity, co2

def init_mqtt(config_file):
    # MQTTの初期セットアップと接続
    client = MQTT_Pub()
    client.read_config(config_file)
    own_host = socket.gethostname().lower()
    client.set_client_id("co2meter" + "_" + own_host)
    client.set_topic("homeassistant/sensor/"+client.client_id)
    client.connect_mqtt()

    return client

def publish_config(client, room):
    # センサ情報を辞書リストにまとめる
    types = ["temperature", "humidity", "co2"]
    names = ["温度", "湿度", "CO2濃度"]
    units = ["°C", "%", "ppm"]
    precisions = [1, 1, 0]
    icons = ["mdi:thermometer", "mdi:water-percent", "mdi:molecule-co2"]
    sensors = [{"type":t, "name":n, "unit":u, "precision":p, "icon": i} for t, n, u, p, i in zip(types, names, units, precisions, icons)]
    device = {
        "identifiers": client.client_id,
        "manufacturer": "I-O DATA DEVICE, INC.",
        "model": "UD-CO2S",
        "name": room+"CO2センサ"
    }

    # センサのconfigurationの送信
    for sensor in sensors:
        payload = {"name": sensor["name"],
            "state_topic": client.topic,
            "value_template": "{{ value_json."+sensor["type"]+" }}",
            "unit_of_measurement": sensor["unit"],
            "unique_id": client.client_id+"_"+sensor["type"],
            "object_id": client.client_id+"_"+sensor["type"],
            "suggested_display_precision": sensor["precision"],
            "icon": sensor["icon"],
            "device": device
        }
        topic = "homeassistant/sensor/"+client.client_id+"_"+sensor["type"]+"/config"
        print(f"send payload{payload} to topic {topic}")
        client.client.publish(topic, json.dumps(payload), qos=1, retain=True).wait_for_publish()

# データのMQTTによる送信
def publish(client):
    base_minute = datetime.now().minute
    while True:
        time.sleep(1)
        # 1分毎にデータ取得->送信
        if base_minute != datetime.now().minute:
            # 最新値の取得
            dt, temperature, humidity, co2 = read_env_data()

            # 送信データの作成
            payload = {
                "time": dt,
                "temperature": temperature,
                "humidity": humidity,
                "co2": co2
            }
            client.publish(payload)
            base_minute = datetime.now().minute

def run(room, config_file):
    # ファイルのあるパスに現在ディレクトリを移動
    os.chdir(os.path.dirname(__file__))

    # MQTTの初期化
    client = init_mqtt(config_file)

    # config情報の送信
    publish_config(client, room)

    # センサ値の取得・送信の開始
    publish(client)

if __name__ == "__main__":
    # デフォルトの部屋名と設定ファイル
    room = "リビング"
    config_file = "./config_mqtt.ini"

    # 引数処理
    args = sys.argv
    if len(args)>=4:
        print("引数が長すぎます")
        sys.exit(-1)
    if len(args)<=1:
        print("引数が足りません")
        sys.exit(-1)
    if len(args)>=2:
        room = args[1]
    if len(args)==3:
        config_file = args[2]

    run(room, config_file)
