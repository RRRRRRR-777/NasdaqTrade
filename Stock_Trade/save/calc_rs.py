import os
import glob
import pandas as pd
import time
import re

# プログラムの実行時間の計測
start = time.time()

# 関数の定義
# RSの素点を計算する関数
def period_perf(data, n):
    i = n
    # 現在の四半期の取引日数
    period = i*oneYear//4

    # 有効な価格データが見つからない場合は最も古いデータを使用する
    try:
        data.iloc[-period]
    except:
        period = 0

    period_price = data.iloc[-period] # 指定された期間の終値
    latest_price = data.iloc[-1] # 最新の終値
    # RSの素点の計算
    calc = ((latest_price - period_price) / period_price) * 100

    return calc

# RSのランキングを作成
def calculate_percentile_ranking(data):
    # 辞書の値をソートしてキーと共に取得
    sorted_data = sorted(data.items(), key=lambda x: x[1])
    n = len(sorted_data)
    rankings = {}
    rank = 1

    for i in range(n):
        key, value = sorted_data[i]
        if i > 0 and value != sorted_data[i - 1][1]:
            # 前のデータと値が異なる場合、新しいランクを設定
            rank = i + 1
        # ランキングを小数点として設定
        percentile_rank = (rank - 1) / (n - 1) * 99.99
        rankings[key] = round(percentile_rank, 2)  # ランクを小数点2桁まで丸める

    return rankings

# ディレクトリの定義
# input.txtのディレクトリ
inputDir = os.path.join(glob.glob(os.getcwd()+"/Stock_Trade/StockData*")[0], "input.txt")
# 個別株の終値データ
stock_dir  = glob.glob(os.getcwd()+"/Stock_Trade/StockData*/*.csv", recursive=True)
IXICdir = glob.glob(os.getcwd() + f"/Stock_Trade/StockData*/^IXIC.csv", recursive=True)[0] # IXICのファイルを除く
stock_dir.remove(IXICdir)
try:
    compdir = glob.glob(os.getcwd() + f"/Stock_Trade/StockData*/Comprehensive.csv", recursive=True)[0] # Comprehensiveのファイルを除く
    stock_dir.remove(compdir)
except:
    pass
# 出力先のディレクトリ
outputDir = os.path.join(glob.glob(os.getcwd()+"/Stock_Trade")[0], "Comprehensive.csv")

# テキストファイルをDataFrameに変換する
data = []

if os.path.exists(inputDir):
    with open(inputDir, 'r', encoding='shift-jis') as f:
        for line in f.readlines():
            toks = line.strip().split('~')
            data.append(toks)

df = pd.DataFrame(data, columns=["Ticker", "Company", "Sector", "Industry", "MarketCap", "P/E", "FwdP/E", "InsiderOwn", "EarningsDate", "Volume", "Price"])

# RSランキングを作成する
oneYear = 252 # 1年間の営業日
rs = {}
data = {} # 各銘柄のティッカーコードとRSの素点を格納する辞書型の変数
max_num = len(stock_dir) # 銘柄数の最大値
# col = ["Date", "ATH", "52W High", "U/D", "SMA10", "EMA21", "SMA50", "SMA200", "Volume SMA50", "BuyFlg1", "BuyFlg2", "BuyFlg3", "BuyFlg4", "BuyingFlg"] # 指定する列のリスト
col = ["Date", "ATH", "52W High", "U/D", "^IXIC Total", "Total", "Prev Total", "No1", "No4", "No5", "No6", "SMA10", "EMA8", "EMA21", "SMA50", "SMA200", "EMA8 Gap", "SMA200 Gap", "Volume SMA50", "BuyFlg1", "BuyFlg2", "BuyFlg4", "BuyingFlg"] # 指定する列のリスト

for i, stock_path in enumerate(stock_dir):
    stock_data = pd.read_csv(stock_path) # 銘柄を一つ選択
    ticker = re.sub(os.getcwd() + r"/Stock_Trade/StockData[0-9]{6}/|.csv", "", stock_path) # ティッカーコードを抽出

    # RSの素点を作成
    stock = stock_data['Adj Close']
    rs[ticker] = 2 * period_perf(stock, 1) + period_perf(stock, 2) + period_perf(stock, 3) + period_perf(stock, 4)

    # ヒストリカルデータから指定した列の最新の値をdataに格納する
    last_row = stock_data.iloc[-1]
    data[ticker] = last_row[col]

    print(f"{ticker} {i+1}/{max_num} ", end="\r")

rankings = calculate_percentile_ranking(rs)
df['RS'] = df['Ticker'].map(rankings)

hist_df = pd.DataFrame(data).T
hist_df.reset_index(inplace=True)
hist_df.columns = ["Ticker"] + col

df = pd.merge(df, hist_df, on="Ticker", how="left")
df.to_csv(outputDir, index=False)

# プログラムの実行時間の出力
print(time.time() - start)
