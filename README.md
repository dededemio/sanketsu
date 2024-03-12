# sanketsu
* [アイ・オー・データUD-CO2S](https://www.iodata.jp/product/tsushin/iot/ud-co2s/index.htm)と通信し、温度、湿度、CO2濃度をCSVファイルとして出力するスクリプト

# 動作環境
* Python 3.9.7
* pyserial 3.5b0

# 実行方法
* Raspberry Pi等にUD-CO2Sを接続する
* `python sanketsu.py`を実行する
* オプション
  - 第一引数: ポート番号（デフォルト`/dev/ttyACM0`）
  - 第二引数: 作業ディレクトリ（デフォルト`/home/pi/work`）

# 出力CSVファイルの仕様
* 出力ファイル名
  - 作業ディレクトリからの相対パスで`./log/yyyy-mm-dd.csv`
* 出力データ
    ```csv
    datetime, temperature, humidity, co2
    2024/01/12 00:00:03, 22.6, 46.8, 1010
    2024/01/12 00:00:07, 22.6, 46.6, 1010
    ```

# 参考
* [Raspberry Piを使った温湿度CO2濃度ロガーの製作 - 白旗製作所](https://dededemio.hatenablog.jp/entry/2024/03/13/012629)