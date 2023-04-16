from flask import Flask, request, send_from_directory
import requests
import os
import time
from contextlib import closing

from .malodyFunc import convertMcOrMczFile
from .miscFunc import convertIllegalCharacters

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
        if os.path.exists(mcz_file): os.remove(mcz_file)
        if os.path.exists(osz_file): os.remove(osz_file)
        # 下载.mcz文件到本地，假设文件名为mcz_file.mcz
        # 这里可以使用requests模块或者其他方法
        # 例如：import requests; requests.get(url).content
        mcz_file = download_file(url)
        # 调用已经设计好的函数convert，传入文件名，得到返回值
        osz_file = convertMcOrMczFile(mcz_file)[1]
        # 返回.osz文件的下载链接，使用send_file函数
        return send_from_directory(os.path.dirname(osz_file), os.path.split(osz_file)[-1])
    # 如果url为空，返回错误信息
    else:
        return '请提供一个有效的.mcz文件的下载链接'
    
def download_file(url, filename = None):
    start_time = time.time()  # 文件开始下载时的时间
    if not filename:
        filename = os.path.abspath(convertIllegalCharacters(os.path.basename(url))
    with closing(requests.get(url, stream=True)) as response:
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
    app.run()
