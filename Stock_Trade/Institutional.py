from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import os
from bs4 import BeautifulSoup
import codecs
import shutil
import selenium
import pandas as pd
import time
import glob
import numpy as np

import random


# 機関投資家数のパフォーマンスを取得する関数
def get_inst_perf(i, ticker):
    try:
        # 各銘柄の株主機関投資家数のパフォーマンスを取得
        driver.get("https://whalewisdom.com")
        driver.implicitly_wait(1.0)
        input_search = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[1]/div/header/div/div[2]/div[1]/div[2]/div/div/div/div[2]/input[1]")
        input_search.clear()
        input_search.send_keys(ticker)
        driver.implicitly_wait(1.5)
        xpath_expression = f"//div[contains(text(), 'Stock:') and contains(text(), ' {ticker}')]"
        driver.find_element(By.XPATH, xpath_expression).click()

        driver.implicitly_wait(1.5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        # 目的の要素を取得する
        try:
            perf_inst = soup.find(id="summary_div").find_all("span")[2].text
        except:
            width = driver.execute_script("return document.body.scrollWidth;")
            height = driver.execute_script("return document.body.scrollHeight;")
            driver.set_window_size(width,height)
            driver.save_screenshot(f"selenium_screen_shot/{ticker}.png")
            perf_inst = np.nan
            print(f"{i+1} | {ticker} Value could not be earned")
    except:
        try:
            width = driver.execute_script("return document.body.scrollWidth;")
            height = driver.execute_script("return document.body.scrollHeight;")
            driver.set_window_size(width,height)
            driver.save_screenshot(f"selenium_screen_shot/{ticker}_error.png")
            perf_inst = np.nan
            if add_error_flg == True:
                error_data.append(ticker)
            print(f"{i+1} | {ticker} Value could not be earned (Error)")
        except:
            perf_inst = np.nan
            if add_error_flg == True:
                error_data.append(ticker)
            print(f"{i+1} | {ticker} Value could not be earned (Error)")

    data.append([ticker, perf_inst])

    print(f"{i+1}/{len(input_df)} ", end="\r")
    sleep(1.0) # 待機時間


#実行時間の計測
start = time.time()

# 銘柄のリストを読み込む
input_df = pd.read_csv(os.getcwd()+"/Stock_Trade/Comprehensive.csv")["Ticker"]
input_df = input_df[:5]

# リスト型のデータ変数
data = []
error_data = []

# flg
add_error_flg = True

# スクリーンショットを保存
shutil.rmtree(os.getcwd()+"/selenium_screen_shot")
os.mkdir(os.getcwd()+"/selenium_screen_shot")

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
options.add_argument('--disable-gpu') # これが勝因かもしれない headlessではログインできなかった
options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36')
options.add_argument('--user-data-dir=~/Library/Application Support/Google/Chrome')
options.add_argument('--profile-directory=Profile1') # recapcahエラーの際にユーザーを変えたらログインできた
# Chromeのユーザーとしてrecapchaのブロックを食らっていた可能性、または時間をおいたからログインできたのかも←多分後者
driver = webdriver.Chrome(chromedriver, options=options)
driver.set_window_size(1200, 1000)

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

driver.save_screenshot("selenium_screen_shot/00.png") # ?
cur_url = driver.current_url
print(f"-----------------Loggined | {cur_url} -------------------") # ?
# ------------------------------------------------------------------------------------------------------------------------------------------------------
start2 = time.time()

sleep(2.0)

for i, ticker in enumerate(input_df):
    get_inst_perf(i, ticker)

sleep(15) # 待機時間
add_error_flg = False

print(error_data)

# errorになった銘柄のデータを再度取得する
for i, ticker in enumerate(error_data):
    ticker = row["Ticker"]
    company = row["Company"]
    get_inst_perf(i, ticker)


# Chrome driverを終了する
driver.close()

# dataをdfに変換する
df = pd.DataFrame(data)
col = ["Ticker", "Perf Inst"]
df.columns = col

outputDir = os.path.join(glob.glob(os.getcwd()+"/Stock_Trade")[0], "Perf_Inst_test.csv")
df.to_csv(outputDir, index=False)


print(f"All Time : {round(time.time() - start, 2)}")
print(f"Get Stock Data Time : {round(time.time() - start2, 2)}")

# ! ティッカーで検索するよりも会社名のほうがいいかもしれない→ティッカーで検索の後に見つからなかった場合は会社名がいいかもしれない

# ! recapchaエラーが出た際は実行停止または、再度実行する


#  * 次のエラーは VScodeの再起動で解消されたまたは、seleniumで開いたChromeを閉じる session not created: Chrome failed to start: exited normally

#TODO f"{ticker} Value could not be earned (Error)"が10回連続出力されるとすべての銘柄の値をnp.nanにして処理を終了する
    # または、もう一度処理を開始する (Profile2にしても良い)