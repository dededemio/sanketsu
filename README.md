# sanketsu

- [アイ・オー・データ UD-CO2S](https://www.iodata.jp/product/tsushin/iot/ud-co2s/index.htm)と通信し、温度、湿度、CO2 濃度を CSV ファイルとして出力する(sanketsu.py)
- sanketsu.py の出力の最新値を MQTT で Home Assistant 等に送信するスクリプト(sanketsu_publish.py)

# 動作環境

- Python 3.9.7
- pyserial 3.5b0
- paho-mqtt < 2.0.0

# 実行方法

- `pip install -r requirements.txt`で上記パッケージをインストール

## sanketsu.py

- Raspberry Pi 等に UD-CO2S を接続
- `python sanketsu.py`を実行
- オプション
  - 第一引数: ポート番号（デフォルト`/dev/ttyACM0`）
  - 第二引数: 作業ディレクトリ（デフォルト`/home/pi/work`）

## sanketsu_publish.py

- MQTT ブローカーの設定ファイル（例: `config_mqtt.ini`）を用意
  - サンプルファイル `config_mqtt_example.ini` を参考
- `python sanketsu_publish.py "<部屋名>" [configファイルパス]`を実行
  - 第一引数: 部屋名（デフォルト`リビング`）
  - 第二引数: configファイルパス（デフォルト`./config_mqtt.ini`）
  - 例: `python sanketsu_publish.py "書斎"`

# sanketsu.py の出力 CSV ファイルの仕様

- 出力ファイル名
  - 作業ディレクトリからの相対パスで`./log/yyyy-mm-dd.csv`
- 出力データ
  ```csv
  datetime, temperature, humidity, co2
  2024/01/12 00:00:03, 22.6, 46.8, 1010
  2024/01/12 00:00:07, 22.6, 46.6, 1010
  ```

# 参考

- [Raspberry Pi を使った温湿度 CO2 濃度ロガーの製作 - 白旗製作所](https://dededemio.hatenablog.jp/entry/2024/03/13/012629)
