from paho.mqtt import client as mqtt
import json
import socket
from configparser import ConfigParser
import time

class MQTT_Pub():
    # MQTTのパブリッシャクラス
    def __init__(self):
        # 初期設定
        self.server = "192.168.1.1"
        self.port = 1883
        self.timeout = 60
        self.client_id = ""
        self.username = ""
        self.pw = ""
        self.topic = ""
        self.qos = 0
        self.client = None

    def read_config(self, config_file):
        # 設定ファイルの読み込み
        section = "MQTT"
        config = ConfigParser()
        config.read(config_file, encoding="utf-8")
        self.server = config.get(section, "server")
        self.port = int(config.get(section, "port"))
        self.timeout = int(config.get(section, "timeout"))
        self.client_id = config.get(section, "client_id")
        self.username = config.get(section, "username")
        self.pw = config.get(section, "pw")
        self.topic = config.get(section, "topic")
        self.qos = int(config.get(section, "qos"))

    def set_topic(self, topic):
        # トピックの設定
        self.topic = topic

    def set_client_id(self, client_id):
        # クライアントIDの設定
        self.client_id = client_id

    def on_connect(self, client, userdata, flags, rc):
        # 接続時のコールバック
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        # メッセージ受信時のコールバック
        print(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}'")

    def on_disconnect(self, client, userdata, rc):
        # 切断時のコールバック
        print(f"Disconnected with return code {rc}. Retrying...")
        while True:
            time.sleep(10)
            try:
                self.client.reconnect()
                print("Reconnected to MQTT Broker!")
                break
            except Exception as err:
                print(f"{err}. Reconnect failed. Retrying...")

    def connect_mqtt(self):
        # mqttクライアントの初期化
        self.client = mqtt.Client((self.client_id))
        self.client.username_pw_set(self.username, self.pw)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        # 接続試行
        while True:
            try:
                self.client.connect(self.server, self.port, self.timeout)
                break
            except Exception as err:
                print(f"{err}. Failed to connect. Retrying...")
                time.sleep(10)

        # 接続成功したら、ループスタート
        self.client.loop_start()

    def publish(self, payload):
        # データ送信
        payload_json = json.dumps(payload)
        result = self.client.publish(self.topic, payload_json, self.qos)
        status = result[0]
        if status != 0:
            print(f"Failed to send message to topic {self.topic}")

