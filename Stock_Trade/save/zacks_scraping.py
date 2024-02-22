import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd
import glob
import yfinance as yf
import yahoo_fin.stock_info as si
import math
import numpy as np


start = time.time()

# 関数の定義
# アナリスト情報を取得
def analysts_info(ticker_code):
    try:
        analysts = si.get_analysts_info(ticker_code)
        eps = analysts["EPS Trend"].iloc[0]
        revenue = analysts["Revenue Estimate"].iloc[1]
        analysts_data.append([ticker_code, eps.iloc[1], eps.iloc[2], eps.iloc[3], eps.iloc[4], revenue.iloc[1], revenue.iloc[2], revenue.iloc[3], revenue.iloc[4]])
    except:
        analysts_data.append([ticker_code, None, None, None, None, None, None, None, None])
        print(f"Failed to fetch the page for {ticker_code} AnalystInfo.")
# 過去の情報を取得
def previous_info(ticker_code):
    '''
    EPS(Year)
    '''
    try:
        ticker = yf.Ticker(ticker_code)
        eps = ticker.income_stmt.loc["Diluted EPS"]
        date = eps.index.strftime("%Y")
        previous_data.append([ticker_code, date[0], eps.iloc[0], None, None, None, None]) # 一年前の年間EPS
        previous_data.append([ticker_code, date[1], eps.iloc[1], None, None, None, None]) # 二年前の年間EPS
        previous_data.append([ticker_code, date[2], eps.iloc[2], None, None, None, None]) # 三年前の年間EPS
    except Exception as e:
        print(f"Failed to fetch the page for {ticker_code} EPS Year. \n {e}")
        previous_data.append([ticker_code, np.nan, np.nan, None, None, None, None]) # 一年前の年間EPS

    '''
    EPS(Quarter)
    '''
    try:
        url = f"https://www.zacks.com/stock/chart/{ticker_code}/fundamental/eps-diluted-quarterly"
        driver.get(url)
        time.sleep(1.0)
        # 1ページ目の値を取得
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0'))) # ページ上の指定の要素が読み込まれるまで待機（15秒でタイムアウト判定）
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tbody = soup.find(id='DataTables_Table_0').find('tbody')
        for idx, tr in enumerate(tbody.find_all('tr')):
            date = tr.find_all('td')[0].text
            eps = tr.find_all('td')[1].text
            if eps != "N/A":
                eps = float(eps.replace("$", ""))
            else:
                eps = math.nan
            if not (idx==0) & (math.isnan(eps)): # 1つ目の値がNaNの場合は追加しない
                previous_data.append([ticker_code, None, None, None, date, eps, None])
        # 2ページ目の値を取得
        element = driver.find_element(By.ID, "DataTables_Table_0_next")
        driver.execute_script("arguments[0].click();", element) # ページ遷移ボタンを押下
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0'))) # ページ上の指定の要素が読み込まれるまで待機（15秒でタイムアウト判定）
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tbody = soup.find(id='DataTables_Table_0').find('tbody')
        for tr in tbody.find_all('tr'):
            date = tr.find_all('td')[0].text
            eps = tr.find_all('td')[1].text
            if eps != "N/A":
                eps = float(eps.replace("$", ""))
            else:
                eps = math.nan
            previous_data.append([ticker_code, None, None, None, date, eps, None])
    except Exception as e:
        print(f"Failed to fetch the page for {ticker_code} EPS Quarter. \n {e}")
        previous_data.append([ticker_code, None, None, None, np.nan, np.nan, None])

    '''
    Revenue(Year)
    '''
    try:
        ticker = yf.Ticker(ticker_code)
        revenue = ticker.income_stmt.loc["Total Revenue"]
        date = revenue.index.strftime("%Y")
        previous_data.append([ticker_code, date[0], None, revenue.iloc[0], None, None, None]) # 一年前の年間Revenue
        previous_data.append([ticker_code, date[1], None, revenue.iloc[1], None, None, None]) # 二年前の年間Revenue
        previous_data.append([ticker_code, date[2], None, revenue.iloc[2], None, None, None]) # 三年前の年間Revenue
    except Exception as e:
        print(f"Failed to fetch the page for {ticker_code} Revenue Year. \n {e}")
        previous_data.append([ticker_code, np.nan, None, np.nan, None, None, None]) # 一年前の年間Revenue

    '''
    Revenue(Quarter)
    '''
    try:
        url = f"https://www.zacks.com/stock/chart/{ticker_code}/fundamental/revenue-quarterly"
        driver.get(url)
        time.sleep(1.0)
        # 1ページ目の値を取得
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0'))) # ページ上の指定の要素が読み込まれるまで待機（15秒でタイムアウト判定）
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tbody = soup.find(id='DataTables_Table_0').find('tbody')
        for idx, tr in enumerate(tbody.find_all('tr')):
            date = tr.find_all('td')[0].text
            revenue = tr.find_all('td')[1].text
            if revenue != "N/A":
                revenue = float(revenue.replace(",", "").replace("$", ""))*1000000
            else:
                revenue = math.nan
            if not (idx==0) & (math.isnan(revenue)): # 1つ目の値がNaNの場合は追加しない
                previous_data.append([ticker_code, None, None, None, date, None, revenue])
        # 2ページ目の値を取得
        element = driver.find_element(By.ID, "DataTables_Table_0_next")
        driver.execute_script("arguments[0].click();", element) # ページ遷移ボタンを押下
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0'))) # ページ上の指定の要素が読み込まれるまで待機（15秒でタイムアウト判定）
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tbody = soup.find(id='DataTables_Table_0').find('tbody')
        for tr in tbody.find_all('tr'):
            date = tr.find_all('td')[0].text
            revenue = tr.find_all('td')[1].text
            if revenue != "N/A":
                revenue = float(revenue.replace(",", "").replace("$", ""))*1000000
            else:
                revenue = math.nan
            previous_data.append([ticker_code, None, None, None, date, None, revenue])
    except Exception as e:
        print(f"Failed to fetch the page for {ticker_code} Revenue Quarter. \n {e}")
        previous_data.append([ticker_code, None, None, None, np.nan, None, np.nan])

# データが存在しないときの関数
def try_exist_index(data, index):
    try:
        if 0 <= int(index) < len(data):
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

# 桁数を変換
def convert_value(value):
    if (isinstance(value, float)) or (pd.isna(value)):
        return value
    elif 'k' in value:
        return float(value.replace('k', '')) * 1000
#       return float(value.replace('k', '')) * 0.001
    elif 'M' in value:
        return float(value.replace('M', '')) * 1000000
#       return float(value.replace('M', ''))
    elif 'B' in value:
        return float(value.replace('B', '')) * 1000000000
#       return float(value.replace('B', '')) * 1000
    else:
        return None


# driverの設定
chromedriver = os.getcwd() + r"/driver/chromedriver"
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--headless')

driver = webdriver.Chrome(chromedriver, chrome_options=options)
driver.implicitly_wait(30)

# 入力するdfの設定
stock_dir = glob.glob(os.getcwd()+"/Stock_Trade/BuyingStock.csv", recursive=True)[0]
stock_df = pd.read_csv(stock_dir)["Ticker"]
analysts_data = []
previous_data = []

# EPSとRevenueの予測値データと過去のデータを取得
for i, ticker_code in enumerate(stock_df):
    analysts_info(ticker_code)
    previous_info(ticker_code)
    print(f"{i+1}/{len(stock_df)} ", end="\r")

# 出力するdfの設定
col = ["Ticker", "CQ_EPS", "NQ_EPS", "CY_EPS", "NY_EPS", "CQ_Rev", "NQ_Rev", "CY_Rev", "NY_Rev"]
analysts_df = pd.DataFrame(analysts_data, columns=col)
col = ["Ticker", "Year", "Annual EPS", "Annual Revenue","Date", "Quarter EPS", "Quarter Revenue"]
previous_df = pd.DataFrame(previous_data, columns=col)
# dfの結合
df = pd.concat([analysts_df, previous_df], axis=0, ignore_index=True)

# 'CQ_Rev'列の各セルに対して変換関数を適用
df['CQ_Rev'] = df['CQ_Rev'].apply(convert_value)
df['NQ_Rev'] = df['NQ_Rev'].apply(convert_value)
df['CY_Rev'] = df['CY_Rev'].apply(convert_value)
df['NY_Rev'] = df['NY_Rev'].apply(convert_value)

# 日付の列のフォーマットを変更する
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y').dt.strftime('%Y/%m/%d')

# 各値のYoYパフォーマンスの列を作成する
data = [] # 作成データを格納するリスト

print("Calculating Data", end="\r")

for i, ticker_code in enumerate(stock_df):
    ticker_df = df[df["Ticker"]==ticker_code]
    # 四半期EPSを設定
    quarter_eps = ticker_df[pd.notna(ticker_df["Date"])].groupby("Date").nth(0).sort_values("Date", ascending=False)["Quarter EPS"]
    # quarter_eps = quarter_eps.str.replace(",", "").astype(float) # 浮動小数点に変換
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
    # annual_eps = annual_eps.str.replace(",", "").astype(float) # 浮動小数点に変換
    previous_annual_eps_3 = try_exist_index(annual_eps, 2) # 3年前
    previous_annual_eps_2 = try_exist_index(annual_eps, 1) # 2年前
    previous_annual_eps = try_exist_index(annual_eps, 0) # 1年前
    current_annual_eps = try_float_data(ticker_df["CY_EPS"].dropna()) # 今年
    next_annual_eps = try_float_data(ticker_df["NY_EPS"].dropna()) # 来年
    # 年度EPSのパフォーマンスを計算
    perf_previous_annual_eps_2 = calculate(previous_annual_eps_2, previous_annual_eps_3)
    perf_previous_annual_eps = calculate(previous_annual_eps, previous_annual_eps_2)
    perf_courrent_annual_eps = calculate(current_annual_eps, previous_annual_eps)
    perf_next_annual_eps = calculate(next_annual_eps, current_annual_eps)

    # 四半期Revenueを設定
    quarter_revenue = ticker_df[pd.notna(ticker_df["Date"])].groupby("Date").nth(1).sort_values("Date", ascending=False)["Quarter Revenue"]
    # quarter_revenue = quarter_revenue.str.replace(",", "").astype(float) # カンマを取り除き浮動小数点に変換
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
    # annual_revenue = annual_revenue.str.replace(",", "").astype(float) # カンマを取り除き浮動小数点に変換
    previous_annual_revenue_3 = try_exist_index(annual_revenue, 2) # 3年前
    previous_annual_revenue_2 = try_exist_index(annual_revenue, 1) # 2年前
    previous_annual_revenue = try_exist_index(annual_revenue, 0) # 1年前
    current_annual_revenue = try_float_data(ticker_df["CY_Rev"].dropna()) # 今年
    next_annual_revenue = try_float_data(ticker_df["NY_Rev"].dropna()) # 来年
    # 年度Revenueのパフォーマンスを計算
    perf_previous_annual_revenue_2 = calculate(previous_annual_revenue_2, previous_annual_revenue_3)
    perf_previous_annual_revenue = calculate(previous_annual_revenue, previous_annual_revenue_2)
    perf_courrent_annual_revenue = calculate(current_annual_revenue, previous_annual_revenue)
    perf_next_annual_revenue = calculate(next_annual_revenue, current_annual_revenue)

    # 各値をリスト型のdataに追加する
    data.append([ticker_code, perf_previous_quarter_eps_2, perf_previous_quarter_eps, perf_courrent_quarter_eps, perf_next_quarter_eps,
                perf_previous_annual_eps_2, perf_previous_annual_eps, perf_courrent_annual_eps, perf_next_annual_eps,
                perf_previous_quarter_revenue_2, perf_previous_quarter_revenue, perf_courrent_quarter_revenue, perf_next_quarter_revenue,
                perf_previous_annual_revenue_2, perf_previous_annual_revenue, perf_courrent_annual_revenue, perf_next_annual_revenue,
                ])

col = ["Ticker", "Previous Quarter Eps2", "Previous Quarter EPS", "Corrent Quarter EPS", "Next Quarter EPS",
            "Previous Annual EPS2", "Previous Annual EPS", "Corrent Annual EPS", "Next Annual EPS",
            "Previous Quarter Revenue2", "Previous Quarter Revenue", "Corrent Quarter Revenue", "Next Quarter Revenue",
            "Previous Annual Revenue2", "Previous Annual Revenue", "Corrent Annual Revenue", "Next Annual Revenue"]
append_df = pd.DataFrame(data, columns=col)

df = pd.merge(df, append_df, on='Ticker', how='inner')

df.to_csv("zacks_scraping.csv", index=False)

driver.quit()

print(time.time() - start)

# 2934s=48.9m