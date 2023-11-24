import pandas as pd
import glob
import re

# VTのCSVを読み込む
VTdir = glob.glob('CompanyData*/VT.csv')[0]
# VTdir = glob.glob('CompanyData*/^IXIC.csv')[0]
df = pd.read_csv(VTdir)

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
# UpDownVolumeRatio
# 前日と比較し株価が上昇していた日の出来高を'Up'に、下落していた日の出来高を'Down'に格納する
df['Up'] = df.loc[df['Adj Close'].diff() > 0, 'Volume']
df['Down'] = df.loc[df['Adj Close'].diff() <= 0, 'Volume']
# 欠損値を0で埋める
df = df.fillna(0)
# 過去50営業日のうち株価が上昇した日の出来高を下落した日の出来高で割った数値
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
# 買い条件2
df['BuyFlg2'] = 0
df.loc[df['U/D'] >= 1, 'BuyFlg2'] = int(1)
# 買い条件3
df['BuyFlg3'] = 0
df.loc[(df['Total'] >= 5) & (df['No1'] == 1) & (df['No4'] == 1) & (df['No5'] == 1) & (df['No6'] == 1), 'BuyFlg3'] = int(1)
# 売り条件1
df['SellFlg1'] = 0
df.loc[df['Total'] <= 4, 'SellFlg1'] = int(1)
# 売り条件2
df['SellFlg2'] = 0
df.loc[df['Adj Close'] < df['SMA200'], 'SellFlg2'] = int(1)

# Totalの列をVT Totalに変更する
df.rename(columns={'Total': 'VT Total'}, inplace=True)
# Csvの書き出し
df.to_csv(VTdir, index=False)
s = re.sub(r"CompanyData[0-9]{6}/|.csv", "", VTdir)

print(f"{s}")