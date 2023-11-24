from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import os
from bs4 import BeautifulSoup
import shutil
import selenium
import pandas as pd
import time
import glob
import numpy as np
import sys

import random


# 機関投資家数のパフォーマンスを取得する関数
def get_inst_perf(i, ticker, max_num):
    try:
        # サイトのホームへ移動
        driver.get("https://whalewisdom.com")
        # 各銘柄のページへ移動
        input_search = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[1]/div/header/div/div[2]/div[1]/div[2]/div/div/div/div[2]/input[1]")
        input_search.clear()
        input_search.send_keys(ticker)
        input_search.send_keys(Keys.ENTER) # エンターキーを押下
        tmp_ticker = ticker + " " # 銘柄の検索に空白が必要なので一時的に空白を追加
        xpath_expression = f"//td[text()='{tmp_ticker}']/preceding-sibling::td/a"
        try:
            driver.find_element(By.XPATH, xpath_expression).click()
        except Exception as e:
            # 該当銘柄の企業名で再度検索する
            driver.get("https://whalewisdom.com")
            input_search = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[1]/div/header/div/div[2]/div[1]/div[2]/div/div/div/div[2]/input[1]")
            input_search.clear()
            company = input_df[input_df["Ticker"]==ticker]["Company"].to_string(index=False)
            input_search.send_keys(company)
            input_search.send_keys(Keys.ENTER) # エンターキーを押下
            driver.find_element(By.XPATH, xpath_expression).click()
            print("Get By Company")
        # ページソースを収録
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        # 目的の要素を取得する
        try:
            perf_inst = soup.find(id="summary_div").find_all("span")[2].text
            try:
                get_ticker = soup.find(class_="profile-default").find("h1").find("a").text
                true_or_false = ticker == get_ticker
            except:
                true_or_false = np.nan
                print("cound not be earned True or False")
        except Exception as e:
            perf_inst = np.nan
            true_or_false = np.nan
            if add_error_flg == True:
                error_data.append(ticker)
            print(f"{i+1} | {ticker} Value could not be earned \n {e}")
            print("-------------------------------------------------------------------------------------------------------------------")
    except Exception as e:
        perf_inst = np.nan
        true_or_false = np.nan
        if add_error_flg == True:
            error_data.append(ticker)
        print(f"{i+1} | {ticker} Value could not be earned (Error) \n {e}")
        print("-------------------------------------------------------------------------------------------------------------------")

    if add_error_flg == True:
        data.append([ticker, perf_inst, true_or_false])
    else:
        # 既存の要素を上書き
        for item in data:
            if item[0] == ticker:
                item[1] = perf_inst
                item[2] = true_or_false

    print(f"{i+1}/{max_num} ", end="\r")
    sleep(1.0) # 待機時間


#実行時間の計測
start = time.time()
# 銘柄のリストを読み込む
input_df = pd.read_csv(os.getcwd()+"/Stock_Trade/Comprehensive.csv")
input_df_ticker = input_df["Ticker"]
input_df_ticker = random.sample(input_df_ticker.tolist(), 10)
# リスト型のデータ変数
data = []
error_data = []
# エラーが起こった際に再実行するためのリストに追加するフラグ
add_error_flg = True

# 対象リンク
loggin_url = "https://whalewisdom.com/login"
# ユーザーネーム
username = os.getenv("whalewisdom_username")
# パスワード
password = os.getenv("whalewisdom_password")
# WEBブラウザの起動
chromedriver = os.getcwd() + "/driver/chromedriver"
#ドライバの設定
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument('--disable-gpu')
options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0 Safari/537.36')
driver = webdriver.Chrome(chromedriver, options=options)
driver.set_window_size(1200, 1000)
# 暗黙的な待機
driver.implicitly_wait(1.5)

# --------------------------------------------------------------------------------------------------------------------------------------------------------
# サイトにログインする
driver.get(loggin_url) # URLを開く
sleep(0.5)
driver.find_element(By.ID, "lnk-login").click()
input_login = driver.find_element(By.ID, "login")
input_login.clear()
input_login.send_keys(username)
input_pass = driver.find_element(By.ID, "password")
input_pass.clear()
input_pass.send_keys(password)
driver.find_element(By.CLASS_NAME, "login").click()
sleep(5) # 待機時間

# 現在のURLを取得
cur_url = driver.current_url
# ログインに失敗した場合はperf_instをnanとしてdf出力する
if cur_url == "https://whalewisdom.com/":
    print(f"----------------- Loggined -------------------")
    sleep(5.0) # 待機時間

    driver.get("https://whalewisdom.com") # URLを開く
    sleep(0.5)
    # 検索をStock Onlyに変更
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div/header/div/div[2]/div[1]/div[1]/div/div/div/div[1]/div[1]/div").click()
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/div/div").click()

    max_num = len(input_df_ticker)
    for i, ticker in enumerate(input_df_ticker):
        get_inst_perf(i, ticker, max_num)

    sleep(15) # 待機時間
    add_error_flg = False

    if len(error_data) != 0:
        print(error_data)

    # errorになった銘柄のデータを再度取得する
    max_num = len(error_data)
    for i, ticker in enumerate(error_data):
        get_inst_perf(i, ticker, max_num)
else:
    print(f"----------------- Loggined False -------------------")
    # ログインエラーの際はすべての銘柄をnanとしてdfを出力する
    try:
        ticker_list = input_df_ticker.to_list()
    except:
        ticker_list = input_df_ticker
    data = [[ticker, np.nan] for ticker in ticker_list]

# Chrome driverを終了する
driver.close()

# dataをdfに変換する
df = pd.DataFrame(data)
col = ["Ticker", "Perf Inst", "True or False"]
df.columns = col

# dfを出力する
outputDir = os.path.join(glob.glob(os.getcwd()+"/Stock_Trade")[0], "Perf_Inst_test.csv")
df.to_csv(outputDir, index=False)

print(f"Time : {round(time.time() - start, 2)}")

# ! Chromeドライバーを入れ直してみる

# ! gitに上げる

# 見つかるが値がないもの
# OXLC
# SLRN
# SFWL

# 本当に見つからなかったもの
# AY
# SLRN
# QQQX(ETF)
# NVEI
# CART
# ARM
# CHY(ETF)

# 会社名で見つかったもの
# EVRG Evergy Inc
    # 2つ目を選択すると表示される
# Z Zillow Group Inc
# GO Grocery Outlet Holding Corp
# BKR Baker Hughes Company
