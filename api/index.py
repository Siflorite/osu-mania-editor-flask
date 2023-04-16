from flask import Flask, request, send_file
import requests
import os
import time
from contextlib import closing

import osuFunc
import malodyFunc
import miscFunc

mcz_file = ""
osz_file = ""
PicArr = []

app = Flask(__name__)

@app.route('/convert', methods = ['GET'])
def convert():
    # 获取请求参数中的url
    url = request.args.get('url')
    # 如果url不为空
    if url:
        global mcz_file
        global osz_file
        # 下载.mcz文件到本地，假设文件名为mcz_file.mcz
        # 这里可以使用requests模块或者其他方法
        # 例如：import requests; requests.get(url).content
        mcz_file = download_file(url)
        # 调用已经设计好的函数convert，传入文件名，得到返回值
        osz_file = malodyFunc.convertMcOrMczFile(mcz_file)[1]
        # 返回.osz文件的下载链接，使用send_file函数
        return send_file(osz_file, as_attachment=True)
    # 如果url为空，返回错误信息
    else:
        return '请提供一个有效的.mcz文件的下载链接'

@app.route('/preview/osz', methods = ['GET'])
def osuPreview():
    url = request.args.get('url')
    if url:
        global osz_file
        global PicArr
        osz_file = download_file(url)
        typeName, osuFiles, basePath = osuFunc.loadOsuOrOszFile(osz_file)
        PicArr = []
        for item in osuFiles:
            newPic = osuFunc.generatePreviewPic(basePath, item)
            PicArr.append(newPic)
        osuFunc.cleanTempOsuFile(osz_file, "", False)
        return send_file(PicArr[0])
    else:
        return '请提供一个有效的.osz文件的下载链接'

@app.after_request
def delete_files(response):
    global mcz_file
    global osz_file
    global PicArr
    if request.endpoint == "convert":
        os.remove(mcz_file)
        os.remove(osz_file)
    elif request.endpoint == "osuPreview":
        os.remove(osz_file)
        for item in PicArr:
            os.remove(item)
    
def download_file(url, filename = None):
    start_time = time.time()  # 文件开始下载时的时间
    if not filename:
        filename = os.path.abspath(miscFunc.convertIllegalCharacters(os.path.basename(url)))
    with closing(requests.get(url, stream=True, allow_redirects=True)) as response:
        chunk_size = 1024  # 单次请求最大值
        content_size = int(response.headers['content-length'])  # 内容体总大小
        data_count = 0
        with open(filename, "wb") as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                data_count = data_count + len(data)
                now_progress = (data_count / content_size) * 100
                speed = data_count / 1024 / (time.time() - start_time)
                print("\r 文件下载进度：%d%%(%d/%d) 文件下载速度：%dKB/s - %s"
                      % (now_progress, data_count, content_size, speed, filename), end=" ")
    return filename

if __name__=="__main__":
    app.run(host='0.0.0.0', port=9000)