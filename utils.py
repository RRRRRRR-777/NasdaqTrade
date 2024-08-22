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
import mplfinance as mpf
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
# from selenium.webdriver.chrome.service import Service
import json
from logging import getLogger, config
import seaborn as sns


# loggerの設定
with open(os.getcwd()+'/log_config.json', 'r') as f:
    log_conf = json.load(f)
config.dictConfig(log_conf)
logger = getLogger(__name__)


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
        logger.info(f"remove {p}")
    except:
        pass
    os.mkdir(downloadDir)
    logger.info(f"mkdir {downloadDir}")

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

    try:
        driver = webdriver.Chrome(chromedriver, chrome_options=options)
    except Exception as e:
        logger.error(f"driver's exception \n{e}")

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
    logger.info(f"Donwload NASDAQ HistData (NasdaqHistDownload)")


"""
CSVデータに情報を加える
"""
def ProcessNASDAQ():
    # 各企業のヒストリカルデータを読み込む
    try:
        file = glob.glob(os.getcwd() + f"/NASDAQ_Trade/NASDAQData*/^IXIC.csv", recursive=True)[0]
    except Exception as e:
        logger.error(f"Not Exitst ^IXIC.csv \n{e}")

    # 入力CSV
    df = pd.read_csv(file)
    s = re.sub(r"/NASDAQ_Trade/NASDAQData[0-9]{6}/|.csv", "", file)

    # 追加する列
    # 10日移動平均線
    df['SMA10'] = df['Adj Close'].rolling(10).mean()
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
    logger.info(f"Complete {file} (ProcessNASDAQ)")


"""
Lineに送信する画像の生成
"""
def PlotImage():
    # チャートの保存先
    save_dir_chart = glob.glob(os.getcwd() + r"/NASDAQ_Trade/NASDAQData*", recursive=True)[0] + '/^IXIC_chart'
    # テーブルの保存先
    save_dir_table = glob.glob(os.getcwd() + r"/NASDAQ_Trade/NASDAQData*", recursive=True)[0] + '/^IXIC_table'
    # チャートとテーブルの結合画像の保存先
    save_dir_combine = glob.glob(os.getcwd() + r"/NASDAQ_Trade/NASDAQData*", recursive=True)[0] + '/^IXIC.jpg'

    # dfの設定
    try:
        file = glob.glob(os.getcwd() + "/NASDAQ_Trade/NASDAQData*/^IXIC.csv", recursive=True)[0]
    except Exception as e:
        logger.error(f"Not Exitst ^IXIC.csv \n{e}")
    df_chart = pd.read_csv(file)
    df_table = pd.read_csv(file)[-11:] # 表示は5日間だが、前日の値を参照するので最新6日間を引用する

    # チャート列の整形
    df_chart['Date'] = df_chart['Date'].astype('datetime64')
    df_chart = df_chart.set_index('Date')
    df_chart['Close'] = df_chart['Adj Close']
    df_chart_plot = df_chart[['Open', 'High', 'Low', 'Close', 'Volume']][-50:]

    # 追加するSMAの定義
    adds=[]
    adds.append(mpf.make_addplot(df_chart['SMA10'][-50:], color='gray', width=1.5, alpha=0.5))
    adds.append(mpf.make_addplot(df_chart['SMA50'][-50:], color='g', width=1.5, alpha=0.5))
    adds.append(mpf.make_addplot(df_chart['SMA150'][-50:], color='y', width=1.5, alpha=0.5))
    adds.append(mpf.make_addplot(df_chart['SMA200'][-50:], color='r', width=1.5, alpha=0.5))
    legend = ["SMA10", "SMA50", "SMA150", "SMA200"]

    # チャートの描画
    mpf.plot(
        df_chart_plot,
        type='candle',
        style='yahoo',
        figsize=(13.5, 10),
        tight_layout=True,
        ylim=((df_chart_plot['Close'].min()*1.0, df_chart_plot['Close'].max()*1.05)),
        datetime_format='%m/%d',
        addplot=adds,
        volume=True,
        title='NASDAQ(^IXIC)',
        savefig=save_dir_chart,
    )

    # テーブル列の整形
    df_table['Performance'] = ((df_table['Adj Close'] / df_table['Adj Close'].shift(1) -1) * 100).round(2)  # 前日の値と比較した列を作成
    df_table['U/D'] = df_table['U/D'].round(2) # 少数第二位までを表示する
    df_table['Adj Close'] = df_table['Adj Close'].round(2) # 少数第二位までを表示する
    df_table['Volume'] = df_table['Volume'].map('{:.2e}'.format) # 出来高列を指数表記する
    df_table = df_table[['Date', 'Adj Close', 'Performance', 'Volume', 'U/D', 'Total']][-10:]
    df_table = df_table.sort_values('Date', ascending=False)


    # テーブルの生成
    fig, ax = plt.subplots(figsize=(13, 12), dpi=100)
    ax.axis('off')
    ax.axis('tight')
    table = ax.table(cellText=df_table.values,
                    bbox=[0, 0, 1, 1])

    # 表のセルの背景色を透明にする
    for key, cell in table._cells.items():
        cell.set_alpha(0)

    # テキストを中央揃えにする
    for key, cell in table._cells.items():
        cell.set_text_props(ha='center', va='center', fontsize=60)

    table.set_fontsize(60)
    plt.savefig(save_dir_table, transparent=True)  # 透明な背景で保存


    """
    ヒートマップの作成
    """
    out_path = os.path.join(glob.glob(os.getcwd() + r"/NASDAQ_Trade/NASDAQData*", recursive=True)[0], 'heatmap.png')

    # データの作成
    data = [
        [df_table['Performance'].iloc[-10]],
        [df_table['Performance'].iloc[-9]],
        [df_table['Performance'].iloc[-8]],
        [df_table['Performance'].iloc[-7]],
        [df_table['Performance'].iloc[-6]],
        [df_table['Performance'].iloc[-5]],
        [df_table['Performance'].iloc[-4]],
        [df_table['Performance'].iloc[-3]],
        [df_table['Performance'].iloc[-2]],
        [df_table['Performance'].iloc[-1]],
    ]

    heatmap_df = pd.DataFrame(data=data)

    plt.figure(figsize=(13, 12))
    plt.axis("off")
    sns.heatmap(heatmap_df, cmap='RdYlGn', vmin=-3, vmax=3, cbar=False)
    # ヒートマップ画像の保存
    plt.savefig(out_path)


    """
    ヒートマップ画像とテーブル画像の結合
    """
    base_path = glob.glob(os.getcwd()+f"/NASDAQ_Trade/NASDAQData*/heatmap.png", recursive=True)[0] # ベース画像
    logo_path = glob.glob(os.getcwd()+f"/NASDAQ_Trade/NASDAQData*/^IXIC_table.png", recursive=True)[0] # 重ねる透過画像

    base = Image.open(base_path)
    logo = Image.open(logo_path)

    base.paste(logo, (0, 0), logo)
    base.save(out_path)


    """
    列名を追加する
    """
    # 画像を開く
    image = Image.open(glob.glob(os.getcwd()+"/NASDAQ_Trade/NASDAQData*/heatmap.png", recursive=True)[0])
    # 画像にテキストを挿入するためのImageDrawオブジェクトを作成
    draw = ImageDraw.Draw(image)
    # テキストを挿入する位置と内容を指定
    text = "Date          Adj Close  Performance  Volume         U/D            Total"
    position = (180, 80)  # テキストを挿入する位置 (x, y)
    # テキストのフォントとサイズを指定
    font_size = 32
    font = ImageFont.truetype(os.getcwd()+"/Arial Unicode.ttf", font_size)
    # テキストを画像に挿入
    draw.text(position, text, fill="black", font=font)

    # 画像を保存
    image.save(out_path)

    # チャート画像とヒートマップ画像の結合
    im1_dir = glob.glob(os.getcwd()+f"/NASDAQ_Trade/NASDAQData*/^IXIC_chart.png", recursive=True)[0]  # チャート画像
    im2_dir = glob.glob(os.getcwd()+f"/NASDAQ_Trade/NASDAQData*/heatmap.png", recursive=True)[0]  # ヒートマップ画像

    im1 = Image.open(im1_dir)
    im2 = Image.open(im2_dir)

    def get_concat(im1, im2):
        dst = Image.new('RGB', (im1.width, im1.height + im2.height))
        dst.paste(im1, (0, 0))
        dst.paste(im2, (0, im1.height))
        return dst

    get_concat(im1, im2).save(save_dir_combine)
    logger.info(f"Complete {save_dir_combine} (PlotImage)")


"""
LineNotifyに通知を送信する
"""
#APIのURLとトークン
url = "https://notify-api.line.me/api/notify"
access_token = os.getenv('LINE_NOTIFY')

def LineNotify():
    # 入力CSV
    try:
        file = glob.glob(os.getcwd() + "/NASDAQ_Trade/NASDAQData*/^IXIC.csv", recursive=True)[0]
    except Exception as e:
        logger.error(f"Not Exitst ^IXIC.csv \n{e}")
    df = pd.read_csv(file)
    # 入力画像
    try:
        image_dir = glob.glob(os.getcwd() + "/NASDAQ_Trade/NASDAQData*/^IXIC.jpg", recursive=True)[0]
    except Exception as e:
        logger.error(f"Not Exitst ^IXIC.jpg \n{e}")
    image = {'imageFile': open(image_dir, 'rb')}
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
    result = requests.post(url, headers=headers, data=send_data, files=image)

    logger.info(f"Send Line Message (LineNotify)\n{message}")