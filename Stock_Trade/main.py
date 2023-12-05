from utils import InitProcess, PickFinviz, HistData, ProcessNASDAQ, ProcessHistData
import time


start = time.time()

# 初期実行
InitProcess()
# finvizから銘柄の配列を取得
PickFinviz()
# ヒストリカルデータをダウンロードする
HistData()
# NASDAQのヒストリカルデータの列を増やす
ProcessNASDAQ()
# 個別株のヒストリカルデータの列を増やす
ProcessHistData()

end = time.time()
print(end-start)