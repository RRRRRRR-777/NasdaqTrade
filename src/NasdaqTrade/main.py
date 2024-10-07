from utils import LineNotify, NasdaqHistDownload, PlotImage, ProcessNASDAQ

if __name__ == "__main__":
    # NASDAQのヒストリカルデータをダウンロード
    data = NasdaqHistDownload()
    # CSVデータに情報を加える
    ProcessNASDAQ(data)
    # Lineに送信する画像の生成
    PlotImage()
    # 売買フラグが立った際にLINEで通知する
    LineNotify()
