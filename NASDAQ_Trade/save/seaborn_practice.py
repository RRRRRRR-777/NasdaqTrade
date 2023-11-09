import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import glob
from PIL import Image, ImageDraw, ImageFont
import os


# NASDAQデータの読み込み
data_dir = glob.glob(os.getcwd()+f"/NASDAQ_Trade/NASDAQData*/^IXIC.csv")[0]
data = pd.read_csv(data_dir)[-11:]
# 出力ファイルの指定
out_path = os.path.join(glob.glob(os.getcwd() + r"/NASDAQ_Trade/NASDAQData*", recursive=True)[0], 'heatmap.png')

# 前日比の列を作成
data['Performance'] = ((data['Close'] / data['Close'].shift(1) -1) * 100).round(2)

"""
ヒートマップの作成
"""
# データの作成
data = [
    [data['Performance'].iloc[-10]],
    [data['Performance'].iloc[-9]],
    [data['Performance'].iloc[-8]],
    [data['Performance'].iloc[-7]],
    [data['Performance'].iloc[-6]],
    [data['Performance'].iloc[-5]],
    [data['Performance'].iloc[-4]],
    [data['Performance'].iloc[-3]],
    [data['Performance'].iloc[-2]],
    [data['Performance'].iloc[-1]],
]

heatmap_df = pd.DataFrame(data=data)

plt.figure(figsize=(6.5, 6))
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
text = "Date       Adj Close    Performance    U/D       Total"
position = (110, 40)  # テキストを挿入する位置 (x, y)
# テキストのフォントとサイズを指定
font_size = 20
font = ImageFont.truetype(os.getcwd()+"/Arial Unicode.ttf", font_size)
# テキストを画像に挿入
draw.text(position, text, fill="black", font=font)

# 画像を保存
image.save(out_path)