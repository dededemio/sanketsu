# sanketsu.py
# UD-CO2を使ってCO2濃度を取得しCSVで保存するプログラム
import os
import sys
import time
import datetime
import serial
import threading
import traceback

def receive(debug):
    cnt=0
    # 開始日を保存
    today = str(datetime.date.today())
    path = "./log/" + today + ".csv"
    num=0
    while(True):
        if os.path.exists(path):
            num = num + 1
            path = "./log/" + today +"_"+ str(num) +".csv"
        else:
            break
    
    with open(path, mode="a", encoding="utf_8_sig") as f: # utf-8 with BOMのCSVを追記モードで作成
        f.write("datetime, temperature, humidity, co2\n") # 先頭行

    while(1):
        try:
            line = recvdata_to_str(ser.readline())
            if(len(line)>0):
                if("OK" in line):   # OKの文字列はそのまま送出
                    print(line)
                if("NG" in line):
                    print(line)
                    ser.write("STA\r\n".encode())   # NGの場合はSTAコマンドを送り続ける
                if( ("CO2" in line) & ("HUM" in line) & ("TMP" in line) ):
                    cnt = cnt+1
                    # if(cnt %4 == 0): # 記録を間引く場合
                    with open(path, mode="a", encoding="utf_8_sig") as f:
                        f.write(recvdata_to_csv(line)+"\n")
                    if debug:
                        print(line)
        except Exception as e:
            print(f"Error occurred: {e}")
            traceback.print_exc()

        # 日付が変わったら終了
        if today != str(datetime.date.today()):
            f.close()
            break

        if(debug):
            if cnt>10:
                f.close()
                break

# シリアル受信データから改行コードを抜く
def recvdata_to_str(data):
    res = data.decode().replace("\r","").replace("\n","")
    if res=="":
        res="waiting..."
    return res

# シリアル受信データのうち、温湿度CO2データを所定書式にする
def recvdata_to_csv(data):
    # カンマで分離
    splitted = data.split(",")
    co2 = int(splitted[0].replace("CO2=",""))
    hum = float(splitted[1].replace("HUM=",""))
    tmp = float(splitted[2].replace("TMP=",""))
    new_tmp = tmp-4.5
    new_hum = calc_new_hum(tmp, new_tmp, hum)

    # 値を補正して時刻と一緒に格納
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    res = "{0}, {1:.1f}, {2:.1f}, {3}".format(now, new_tmp, new_hum, co2)
    return res

# 温度が変わった場合の相対湿度の再計算。絶対湿度の計算には、Arden Buckの式を使用
def calc_new_hum(tmp, new_tmp, hum):
    # 絶対湿度の計算
    abs_hum = 216.7 * (hum / 100 * 6.112 * pow(2.71828, (17.62 * tmp) / (243.12 + tmp))) / (273.15 + tmp)
    # 温度が変化した場合の相対湿度の計算
    new_hum = (abs_hum * (273.15 + new_tmp)) / (216.7 * 6.112 * pow(2.71828, (17.62 * new_tmp) / (243.12 + new_tmp))) * 100
    return new_hum


if __name__ == "__main__":
    # パラメータと初期値
    port = "/dev/ttyACM0"
    dir = "/home/pi/work"
    debug = False

    # 引数処理
    args = sys.argv
    if len(args)>=5:
        print("引数が長すぎます")
        sys.exit(-1)
    if len(args)>=2:
        port = args[1]
    if len(args)>=3:
        dir = args[2]
    if len(args)>=4:
        debug = bool(args[3])

    os.chdir(dir) # カレントディレクトリを移動する
    baud = '115200'

    # デバイスが見つからない場合は10秒毎にループする
    retry = True
    while(retry):
        try:
            ser = serial.Serial(port, baud, timeout=3)    # シリアルポートを開く
            retry = False
        except (serial.SerialException, serial.SerialTimeoutException):
            print("シリアルポートが開けません")
            retry = True
            time.sleep(10)
    
    # 成功したら最初のスレッドを用意
    thread = threading.Thread(target=receive, args=(debug,))

    # 最初のOK STA待ち
    print("Prepare device...")
    while(1):
        ser.write("STA\r\n".encode())
        result = recvdata_to_str(ser.read_all())
        print(result)
        time.sleep(1)
        if("OK" in result):
            break

    # 受信開始してスレッド終了を待機
    thread.start()
    thread.join()

    # スレッド終了時は計測停止してシリアルポートを閉じる
    ser.write("STP\r\n".encode())
    ser.close()
