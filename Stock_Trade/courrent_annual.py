import re
import os
import glob
import time
import yahoo_fin.stock_info as si
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


start = time.time()

# 関数の定義
# アナリスト情報を取得
def analyst_info(ticker):
    try:
        analysts = si.get_analysts_info(ticker)
        eps = analysts['EPS Trend'].iloc[0]
        revenue = analysts['Revenue Estimate'].iloc[1]
        analyst_data.append([ticker, eps.iloc[1], eps.iloc[2], eps.iloc[3], eps.iloc[4], revenue.iloc[1], revenue.iloc[2], revenue.iloc[3], revenue.iloc[4]])
    except:
        analyst_data.append([ticker, "", "", "", "", "", "", "", ""])
        print(f"Failed to fetch the page for {ticker} AnalystInfo.")
# 過去の情報を取得
def previous_info(ticker):
    # スクレイピング対象のURL
    eps_url = f"https://www.macrotrends.net/stocks/charts/{ticker}/{ticker}/eps-earnings-per-share-diluted" # EPS取得のURL
    revenue_url = f"https://www.macrotrends.net/stocks/charts/{ticker}/{ticker}/revenue" # Revenue取得のURL
    # headerの指定
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}
    # EPSの値を取得
    # ページのHTMLを取得
    response = requests.get(eps_url, headers=headers)
    # ステータスコードが200 (成功) でない場合、エラーを表示
    if response.status_code != 200:
        print(f"Failed to fetch the page for {ticker} PreviousInfo EPS URL.")
    else:
        # ページのHTMLをBeautiful Soupで解析
        soup = BeautifulSoup(response.text, 'html.parser')
        # 年次EPSデータの表を取得
        annual_eps_table = soup.find('table', {'class': 'historical_data_table'})
        # 四半期EPSデータの表を取得
        quarter_eps_table = soup.find_all('table', {'class': 'historical_data_table'})[1]

        # 年次EPSデータを取得してDataFrameに追加
        for row in annual_eps_table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                year = cols[0].text
                eps = cols[1].text
                if eps != 'N/A':
                    eps = eps.replace("$", "")
                previous_data.append([ticker, year, eps, None, None, None, None])

        # 四半期EPSデータを取得
        for row in quarter_eps_table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                date = cols[0].text
                eps = cols[1].text
                if eps != 'N/A':
                    eps = eps.replace("$", "")
                previous_data.append([ticker, None, None, None, date, eps, None])


    # Revenueの値を取得
    response = requests.get(revenue_url, headers=headers)
    # ステータスコードが200 (成功) でない場合、エラーを表示
    if response.status_code != 200:
        print(f"Failed to fetch the page for {ticker} PreviousInfo Revenue URL.")
    else:
        # ページのHTMLをBeautiful Soupで解析
        soup = BeautifulSoup(response.text, 'html.parser')
        annual_revenue_table = soup.find('table', {'class': 'historical_data_table'})
        quarter_revenue_table = soup.find_all('table', {'class': 'historical_data_table'})[1]

        # 年次Revenueデータを取得してDataFrameに追加
        for row in annual_revenue_table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                year = cols[0].text
                revenue = cols[1].text
                if revenue != 'N/A':
                    revenue = revenue.replace("$", "")
                previous_data.append([ticker, year, None, revenue, None, None, None])
        # 四半期Revenueデータを取得
        for row in quarter_revenue_table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                date = cols[0].text
                revenue = cols[1].text
                if revenue != 'N/A':
                    revenue = revenue.replace("$", "")
                previous_data.append([ticker, None, None, None, date, None, revenue])

    time.sleep(1.0) # 1秒間間隔を空ける

# データが存在しないときの関数
def try_exist_index(data, index):
    try:
        if 0 <= index < len(data):
            return data.iloc[index]
        else:
            return np.nan
    except (ValueError, TypeError, IndexError):
        return np.nan
# 浮動小数に変換できない場合の関数
def try_float_data(data):
    try:
        tmp = float(data)
    except:
        tmp = np.nan
    return tmp
# 2つの値のパフォーマンスを計算する関数
def calculate(num1, num2):
    if num2 == 0:
        tmp = np.nan
    else:
        try:
            tmp = round(((num1 - num2) / num2) * 100, 1)
        except:
            tmp = np.nan
    return tmp


# 個別株の終値データ
stock_dir  = glob.glob(os.getcwd()+"/Stock_Trade/StockData*/*.csv", recursive=True)
IXICdir = glob.glob(os.getcwd() + f"/Stock_Trade/StockData*/^IXIC.csv", recursive=True)[0] # IXICのファイルを除く
stock_dir.remove(IXICdir)
compdir = glob.glob(os.getcwd() + f"/Stock_Trade/StockData*/Comprehensive.csv", recursive=True)[0] # Comprehensiveのファイルを除く
stock_dir.remove(compdir)

# 配列の定義
analyst_data = []
previous_data = []

print("START Getting Data")

# EPSとREVENUEを取得
for i, stock_path in enumerate(stock_dir):
    ticker = re.sub(os.getcwd() + r"/Stock_Trade/StockData[0-9]{6}/|.csv", "", stock_path) # ティッカーコードを抽出
    analyst_info(ticker)
    previous_info(ticker)

    print(f"{i+1}/{len(stock_dir)} ", end="\r")

# dfの作成
analyst_df = pd.DataFrame(analyst_data)
col = ["Ticker", "CQ_EPS", "NQ_EPS", "CY_EPS", "NY_EPS", "CQ_Rev", "NQ_Rev", "CY_Rev", "NY_Rev"]
analyst_df.columns = col

previous_df = pd.DataFrame(previous_data)
col = ["Ticker", "Year", "Annual EPS", "Annual Revenue","Date", "Quarter EPS", "Quarter Revenue"]
previous_df.columns = col

df = pd.concat([analyst_df, previous_df], axis=0, ignore_index=True)

# 値を変換
def convert_value(value):
    if pd.isna(value):
        return value
    elif 'k' in value:
        return float(value.replace('k', '')) * 0.001
    elif 'M' in value:
        return float(value.replace('M', ''))
    elif 'B' in value:
        return float(value.replace('B', '')) * 1000
    else:
        return None

# 'CQ_Rev'列の各セルに対して変換関数を適用
df['CQ_Rev'] = df['CQ_Rev'].apply(convert_value)
df['NQ_Rev'] = df['NQ_Rev'].apply(convert_value)
df['CY_Rev'] = df['CY_Rev'].apply(convert_value)
df['NY_Rev'] = df['NY_Rev'].apply(convert_value)

# 空の文字列をNaNに変換
df = df.replace('', np.nan)


# 各値のYoYパフォーマンスの列を作成する
ticker_list = df["Ticker"].drop_duplicates() # すべてのティッカーを格納
data = [] # 作成データを格納するリスト

print("START Calculating Data")

for i, ticker in enumerate(ticker_list):
    ticker_df = df[df["Ticker"]==ticker]

    # 四半期EPSを設定
    quarter_eps = ticker_df[pd.notna(ticker_df["Date"])].groupby("Date").nth(0).sort_values("Date", ascending=False)["Quarter EPS"]
    quarter_eps = quarter_eps.str.replace(",", "").astype(float) # 浮動小数点に変換
    previous_quarter_eps_6 = try_exist_index(quarter_eps, 5) # 6期前
    previous_quarter_eps_5 = try_exist_index(quarter_eps, 4) # 5期前
    previous_quarter_eps_4 = try_exist_index(quarter_eps, 3) # 4期前
    previous_quarter_eps_3 = try_exist_index(quarter_eps, 2) # 3期前
    previous_quarter_eps_2 = try_exist_index(quarter_eps, 1) # 2期前
    previous_quarter_eps = try_exist_index(quarter_eps, 0) # 1期前
    current_quarter_eps = try_float_data(ticker_df["CQ_EPS"].dropna()) # 今期
    next_quarter_eps = try_float_data(ticker_df["NQ_EPS"].dropna()) # 来期
    # 各四半期EPSのパフォーマンスを計算
    perf_previous_quarter_eps_2 = calculate(previous_quarter_eps_2, previous_quarter_eps_6)
    perf_previous_quarter_eps = calculate(previous_quarter_eps, previous_quarter_eps_5)
    perf_courrent_quarter_eps = calculate(current_quarter_eps, previous_quarter_eps_4)
    perf_next_quarter_eps = calculate(next_quarter_eps, previous_quarter_eps_3)

    # 年度EPSを設定
    annual_eps = ticker_df[pd.notna(ticker_df["Year"])].groupby("Year").nth(0).sort_values("Year", ascending=False)["Annual EPS"]
    annual_eps = annual_eps.str.replace(",", "").astype(float) # 浮動小数点に変換
    previous_annual_eps_3 = try_exist_index(annual_eps, 2) # 3年前
    previous_annual_eps_2 = try_exist_index(annual_eps, 1) # 2年前
    previous_annual_eps = try_exist_index(annual_eps, 0) # 1年前
    current_annual_eps = try_float_data(ticker_df["CY_EPS"].dropna()) # 今年
    next_annual_eps = try_float_data(ticker_df["NY_EPS"].dropna()) # 来年
    # 年度EPSのパフォーマンスを計算
    perf_previous_annual_eps_2 = calculate(previous_annual_eps_2, previous_annual_eps_3)
    perf_previous_annual_eps = calculate(previous_annual_eps, previous_annual_eps_2)
    perf_courrent_annual_eps = calculate(current_annual_eps, previous_annual_eps)
    perf_next_quarter_eps = calculate(next_annual_eps, current_annual_eps)

    # 四半期Revenueを設定
    quarter_revenue = ticker_df[pd.notna(ticker_df["Date"])].groupby("Date").nth(1).sort_values("Date", ascending=False)["Quarter Revenue"]
    quarter_revenue = quarter_revenue.str.replace(",", "").astype(float) # カンマを取り除き浮動小数点に変換
    previous_quarter_revenue_6 = try_exist_index(quarter_revenue, 5) # 6期前
    previous_quarter_revenue_5 = try_exist_index(quarter_revenue, 4) # 5期前
    previous_quarter_revenue_4 = try_exist_index(quarter_revenue, 3) # 4期前
    previous_quarter_revenue_3 = try_exist_index(quarter_revenue, 2) # 3期前
    previous_quarter_revenue_2 = try_exist_index(quarter_revenue, 1) # 2期前
    previous_quarter_revenue = try_exist_index(quarter_revenue, 0) # 1期前
    current_quarter_revenue = try_float_data(ticker_df["CQ_Rev"].dropna()) # 今期
    next_quarter_revenue = try_float_data(ticker_df["NQ_Rev"].dropna()) # 来期
    # 各四半期Revenueのパフォーマンスを計算
    perf_previous_quarter_revenue_2 = calculate(previous_quarter_revenue_2, previous_quarter_revenue_6)
    perf_previous_quarter_revenue = calculate(previous_quarter_revenue, previous_quarter_revenue_5)
    perf_courrent_quarter_revenue = calculate(current_quarter_revenue, previous_quarter_revenue_4)
    perf_next_quarter_revenue = calculate(next_quarter_revenue, previous_quarter_revenue_3)

    # 年度Revenueを設定
    annual_revenue = ticker_df[pd.notna(ticker_df["Year"])].groupby("Year").nth(1).sort_values("Year", ascending=False)["Annual Revenue"]
    annual_revenue = annual_revenue.str.replace(",", "").astype(float) # カンマを取り除き浮動小数点に変換
    previous_annual_revenue_3 = try_exist_index(annual_revenue, 2) # 3年前
    previous_annual_revenue_2 = try_exist_index(annual_revenue, 1) # 2年前
    previous_annual_revenue = try_exist_index(annual_revenue, 0) # 1年前
    current_annual_revenue = try_float_data(ticker_df["CY_Rev"].dropna()) # 今年
    next_annual_revenue = try_float_data(ticker_df["NY_Rev"].dropna()) # 来年
    # 年度Revenueのパフォーマンスを計算
    perf_previous_annual_revenue_2 = calculate(previous_annual_revenue_2, previous_annual_revenue_3)
    perf_previous_annual_revenue = calculate(previous_annual_revenue, previous_annual_revenue_2)
    perf_courrent_annual_revenue = calculate(current_annual_revenue, previous_annual_revenue)
    perf_next_quarter_revenue = calculate(next_annual_revenue, current_annual_revenue)

    # 各値をリスト型のdataに追加する
    data.append([ticker, perf_previous_quarter_eps_2, perf_previous_quarter_eps, perf_courrent_quarter_eps, perf_next_quarter_eps,
                perf_previous_annual_eps_2, perf_previous_annual_eps, perf_courrent_annual_eps, perf_next_quarter_eps,
                perf_previous_quarter_revenue_2, perf_previous_quarter_revenue, perf_courrent_quarter_revenue, perf_next_quarter_revenue,
                perf_previous_annual_revenue_2, perf_previous_annual_revenue, perf_courrent_annual_revenue, perf_next_quarter_revenue,
                ])

    print(f"{i+1}/{len(ticker_list)} ", end="\r")

append_df = pd.DataFrame(data)
col = ["Ticker", "Previous Quarter Eps2", "Previous Quarter EPS", "Courrent Quarter EPS", "Next Quarter EPS",
            "Previous Annual EPS2", "Previous Annual EPS", "Courrent Annual EPS", "Next Quarter EPS",
            "Previous Quarter Revenue2", "Previous Quarter Revenue", "Courrent Quarter Revenue", "Next Quarter Revenue",
            "Previous Annual Revenue2", "Previous Annual Revenue", "Courrent Annual Revenue", "Next Quarter Revenue"]
append_df.columns = col

df = pd.merge(df, append_df, on='Ticker', how='inner')

outputDir = os.path.join(glob.glob(os.getcwd()+"/Stock_Trade")[0], "courrent_annual.csv")
df.to_csv(outputDir, index=False)

print(time.time() - start)
