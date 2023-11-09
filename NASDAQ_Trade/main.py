from utils import NasdaqHistDownload, ProcessNASDAQ, PlotImage, LineNotify


# # NASDAQのヒストリカルデータをダウンロード
NasdaqHistDownload()
# # CSVデータに情報を加える
ProcessNASDAQ()
# Lineに送信する画像の生成
PlotImage()
# # 売買フラグが立った際にLINEで通知する
LineNotify()