import datetime
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service as fs
import subprocess
import glob
import shutil
import pandas as pd
import numpy as np
import re
import requests
# from selenium.webdriver.chrome.service import Service



"""
NASDAQのヒストリカルデータをダウンロード
"""
def NasdaqHistDownload():
    # ChromeDriverの保存先
    chromedriver = os.getcwd() + r"/driver/chromedriver"
    # ダウンロードデータの保存先
    dt_now = datetime.datetime.now()
    date = dt_now.strftime('%y%m%d')
    downloadDir = os.getcwd() + r"/NASDAQ_Trade/NASDAQData" + date
    try:
        p = glob.glob(os.getcwd() + r"/NASDAQ_Trade/NASDAQData*", recursive=True)[0]
        shutil.rmtree(p)
    except:
        pass
    os.mkdir(downloadDir)

    # データ期間の指定（st:開始、ed:終了）
    st = datetime.date(1970, 1, 1)
    ed = datetime.date.today()
    dt = datetime.date(1970, 1, 1)
    st = st - dt
    ed = ed - dt
    st = (st.days) * 86400
    ed = (ed.days) * 86400

    # ドライバの設定
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--headless')
    options.add_experimental_option("prefs", {"download.default_directory": downloadDir })
    chrome_service = fs.Service(executable_path=chromedriver)
    driver = webdriver.Chrome(service=chrome_service, chrome_options=options)

    # headlessモードでファイルをダウンロードする際の追加設定
    driver.command_executor._commands["send_command"] = (
    'POST',
    '/session/$sessionId/chromium/send_command'
    )
    driver.execute(
        'send_command',
        params={
            'cmd': 'Page.setDownloadBehavior',
            'params': {'behavior': 'allow', 'downloadPath': downloadDir}
        }
    )

    # NASDAQのヒストリカルデータをダウンロード
    url = 'https://query1.finance.yahoo.com/v7/finance/download/^IXIC?period1='\
            + str(st)+'&period2='+str(ed)+'&interval=1d&events=history&includeAdjustedClose=true'

    #日足データのダウンロード
    driver.implicitly_wait(30)
    driver.get(url)
    #5秒間の一時停止
    time.sleep(5)


"""
CSVデータに情報を加える
"""
def ProcessNASDAQ():
    # 各企業のヒストリカルデータを読み込む
    file = glob.glob(os.getcwd() + f"/NASDAQ_Trade/NASDAQData*/^IXIC.csv", recursive=True)[0]

    # 入力CSV
    df = pd.read_csv(file)
    s = re.sub(r"/NASDAQ_Trade/NASDAQData[0-9]{6}/|.csv", "", file)

    # 追加する列
    # 50日移動平均線
    df['SMA50'] = df['Adj Close'].rolling(50).mean()
    # 150日移動平均線
    df['SMA150'] = df['Adj Close'].rolling(150).mean()
    # 200日移動平均線
    df['SMA200'] = df['Adj Close'].rolling(200).mean()
    # 200日移動平均線の20日平均値
    df['SMA200 mean 20days'] = df['SMA200'].rolling(20).mean()
    # 200日移動平均線の20日前の値
    df['SMA200 befor 20days'] = df['SMA200'].shift(20)
    # 200日移動平均線と現在の株価のギャップ
    df['SMA200 Gap'] = df['Adj Close'] / df['SMA200']
    # 52週最高値
    df['52W High'] = df['Adj Close'].rolling(260, min_periods=1).max() # min_periodsを使用して1つ以上のデータがあった場合の最大値を求める
    # 52週最高値の25%以内
    df['52W High*0.75'] = df['52W High']*0.75
    # 52週最安値
    df['52W Low'] = df['Adj Close'].rolling(260, min_periods=1).min() # min_periodsを使用して1つ以上のデータがあった場合の最小値を求める
    # 52週最安値の30%以上
    df['52W Low*1.3'] = df['52W Low']*1.3
    # UpDownVolumeRatio 過去50営業日のうち株価が上昇した日の出来高を下落した日の出来高で割った数値
    df['Up'] = df.loc[df['Adj Close'].diff() > 0, 'Volume'] # 前日と比較し株価が上昇していた日の出来高を'Up'
    df['Down'] = df.loc[df['Adj Close'].diff() <= 0, 'Volume'] # 前日と比較し株価が下落していた日の出来高を'Down'に格納する
    df = df.fillna(0) # 欠損値を0で埋める
    df['U/D'] = df['Up'].rolling(50).sum() / df['Down'].rolling(50).sum()

    # ミネルビィ二のトレンドテンプレートのNo1〜No7までの列を作成
    df[['No1', 'No2', 'No3', 'No4', 'No5', 'No6', 'No7']] = 0

    # No1 現在の株価が150日と200日の移動平均線を上回っている。
    df.loc[(df['Adj Close'] > df['SMA150']) & (df['Adj Close'] > df['SMA200']), 'No1'] = int(1)
    # No2 150日移動平均線は200日移動平均線を上回っている。
    df.loc[df['SMA150'] > df['SMA200'], 'No2'] = int(1)
    # No3 200日移動平均線は少なくとも1か月、上昇トレンドにある。
    df.loc[df['SMA200 mean 20days'] > df['SMA200 befor 20days'], 'No3'] = int(1)
    # No4 50日移動平均線は150日移動平均線と200日移動平均線を上回っている。
    df.loc[(df['SMA50'] > df['SMA150']) & (df['SMA50'] > df['SMA200']), 'No4'] = int(1)
    # No5 現在の株価は50日移動平均線を上回っている。
    df.loc[df['Adj Close'] > df['SMA50'], 'No5'] = int(1)
    # No6 現在の株価は52週安値よりも、少なくとも30％高い。
    df.loc[df['Adj Close'] > df['52W Low*1.3'], 'No6'] = int(1)
    # No7 現在の株価は52週高値から少なくとも25％以内にある。
    df.loc[df['Adj Close'] > df['52W High*0.75'], 'No7'] = int(1)
    # No1~No7の合計値
    df['Total'] = df['No1'] + df['No2'] + df['No3'] + df['No4'] + df['No5'] + df['No6'] + df['No7']


    # 買い条件1
    df['BuyFlg1'] = 0
    df.loc[df['Total'] >= 5, 'BuyFlg1'] = int(1)

    # 売り条件1
    df['SellFlg1'] = 0
    df.loc[df['Total'] <= 4, 'SellFlg1'] = int(1)
    # # 売り条件2
    df['SellFlg2'] = 0
    df.loc[df['Adj Close'] < df['SMA150'], 'SellFlg2'] = int(1)

    try:
        # 買っているフラッグ
        df['BuyingFlg'] = 0
        df.loc[df['BuyFlg1'] == 1, 'BuyingFlg'] = int(1)
        df.loc[df['BuyingFlg'].shift(1) == 1, 'BuyingFlg'] = int(0)
        # 売ったフラッグ
        df['SelledFlg'] = 0
        df.loc[(df['BuyingFlg'].cumsum() >= 1) & (df['SellFlg1'] == 1) | (df['SellFlg2']), 'SelledFlg'] = int(1) # 該当行より上の行でBuyingFlgが立っていれば立てる
        df.loc[df['SelledFlg'].shift(1) == 1, 'SelledFlg'] = int(0)

        # 'BuyingFlg'または'SelledFlg'が1のものを選出する
        df_trade = df[(df['BuyingFlg'] == 1) | (df['SelledFlg'] == 1)]
        # 'BuyingFlg'と'SelledFlg'各々の1が続く行をすべて0に変換する
        df_trade.loc[df_trade['BuyingFlg'].shift(1) == 1, 'BuyingFlg'] = int(0)
        df_trade.loc[df_trade['SelledFlg'].shift(1) == 1, 'SelledFlg'] = int(0)
        # 'BuyingFlg'または'SelledFlg'の値が1であるもののみを選出する
        df_trade = df_trade[(df_trade['BuyingFlg'] == 1) | (df_trade['SelledFlg'] == 1)]

        # dfの一番初めがSelledFlgで始まった場合はその行を消す
        if df_trade['SelledFlg'].iloc[0] == 1:
            df_trade = df_trade.iloc[1:]

        # 利益率
        df_trade['Earn'] = 0
        # df_trade.loc[df_trade['SelledFlg'] == 1, 'Earn'] = (df_trade['Adj Close'] / df_trade['Adj Close'].shift(1) - 1) * 100
        df_trade.loc[df_trade['SelledFlg'] == 1, 'Earn'] = df_trade['Adj Close'] / df_trade['Adj Close'].shift(1)

        # 元のBuyingFlgとSelledFlgをすべて0にする
        df[['BuyingFlg', 'SelledFlg']] = 0

        # 利益率をdfに追加するために結合
        #'Earn'列が複数結合されるのを防ぐため(本実装時には何度も当ファイルを実行されることが無いため当コードは不要と思う)
        if not 'Earn' in df.columns:
            # 入力CSVとdf_tradeのCSVを結合する
            df = pd.merge(df, df_trade[['Date', 'Earn']], on='Date', how='outer').fillna(0)

        # dfにBuyingFlgとSelledFlgの値を結合する
        df = pd.merge(df, df_trade[['Date', 'BuyingFlg', 'SelledFlg']], on='Date', how='outer')
        # 重複した列を削除し、列名を変更する
        df = df.drop(['BuyingFlg_x', 'SelledFlg_x'], axis=1).rename(columns={'BuyingFlg_y': 'BuyingFlg', 'SelledFlg_y': 'SelledFlg'})

        # 総利益率
        df['TotalEarn'] = np.cumprod(df[df['Earn'] != 0]['Earn'])
        # 0の箇所を前の値で埋める
        df['TotalEarn'] = df['TotalEarn'].fillna(method='pad')
        df = df.fillna(0)

        # 買い値
        df.loc[df['BuyingFlg'] == 1, 'BuyPrice'] = df['Adj Close']
        # 0の箇所を前の値で埋める
        df = df.fillna(method='pad')

        # 空白を0で埋める
        df = df.fillna(0)

    # 取引履歴がない場合Empty DataFrameエラーが発生するのでその場合は2つの列を追加する
    except:
        df[['Earn', 'TotalEarn']] = float(0)

    df.to_csv(file, index=False)


"""
LineNotifyに通知を送信する
"""
#APIのURLとトークン
url = "https://notify-api.line.me/api/notify"
access_token = os.getenv('LINE_NOTIFY')

def LineNotify():
    # 入力CSV
    file = glob.glob(os.getcwd() + "/NASDAQ_Trade/NASDAQData*/^IXIC.csv", recursive=True)[0]
    df = pd.read_csv(file)
    # 最新日の買いフラグと売りフラグを変数に設定
    today_df = df.iloc[-1][['Date', 'BuyingFlg', 'SelledFlg']]
    today = today_df['Date']
    today_buy = today_df['BuyingFlg']
    today_sell = today_df['SelledFlg']

    if today_buy==1:
        message = f'\n{today}\n!!!!! BUY NASDAQ !!!!!'
    elif today_sell==1:
        message = f'\n{today}\n?????? SELL NASDAQ ??????'
    else:
        message = f'\n{today}\nNo Trade'

    headers = {"Authorization": "Bearer " + access_token}
    send_data = {"message": message}

    #メッセージを送信
    result = requests.post(url, headers=headers, data=send_data)

    print(message)