from bs4 import BeautifulSoup
import requests
import os
import glob

# URL ###################################################
url = "https://finviz.com/screener.ashx?v=152&f=cap_smallover,exch_nasd,\ind_stocksonly&o=-marketcap&c=0,1,2,3,4,6,7,8,65,67,68&r="
#########################################################
num = 5 # ページ数

# ファイル名
output_path = os.path.join(glob.glob(os.getcwd()+"/Stock_Trade/StockData*", recursive=True)[0], "input.txt")

with open(output_path, "w", encoding="utf-8") as file:
    # 1ページごとでループする
    for i in range(num):
        page = str(i * 20 + 1)
        site = requests.get(url + page, headers={'User-Agent': 'Custom'})
        data = BeautifulSoup(site.text, 'html.parser')

        tr_tag = data.find_all("tr", {"class": "styled-row is-hoverable is-bordered is-rounded is-striped has-color-text"})
        # 1銘柄ごとループする
        for j in range(0, len(tr_tag), 1):
            a_tag = [a.text for a in tr_tag[j].find_all("a")]
            # 行をテキストファイルに書き込む (波線で区切る)
            file.write("~".join(a_tag[1:]) + "\n")

        print(f"Done {(i+1) * 20}", end="\r")
