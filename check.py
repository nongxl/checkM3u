import requests
import time
import os
from datetime import datetime


# 下载远程 M3U 文件到本地，带时间戳
def download_m3u(m3u_url, local_filename_prefix="local_playlist"):
    # 获取当前时间戳，格式为：yyyy-mm-dd_hh-mm-ss
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    local_filename = f"{local_filename_prefix}_{timestamp}.m3u"

    response = requests.get(m3u_url)
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            f.write(response.content)
        print(f"M3U 文件已下载到 {local_filename}")
        return local_filename  # 返回下载的文件名
    else:
        print(f"无法下载 M3U 文件，HTTP 错误代码: {response.status_code}")
        return None


# 从本地 M3U 文件解析出地址
def parse_m3u(file_path):
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在！")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:  # 使用 utf-8 编码打开文件
        content = f.readlines()

    # 只提取包含http/https地址的行
    urls = [line.strip() for line in content if line.strip().startswith('http')]
    return urls


# 测试地址的有效性和速度
def test_url(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)  # 设置超时时间10秒
        if response.status_code == 200:
            elapsed_time = time.time() - start_time
            speed = len(response.content) / elapsed_time / 1024  # 速度单位 KB/s
            print(f"地址有效: {url} | 下载速度: {speed:.2f} KB/s")
        else:
            print(f"地址无效: {url} | HTTP 错误代码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"地址无效: {url} | 错误: {e}")


# 主函数
def main(m3u_input):
    # 判断是否是远程 M3U 文件
    is_remote = m3u_input.startswith("http://") or m3u_input.startswith("https://")

    if is_remote:
        # 如果是远程 M3U 文件，下载并获取下载后的文件名
        downloaded_file = download_m3u(m3u_input)
        if downloaded_file is None:
            return  # 如果下载失败，直接返回
        m3u_file = downloaded_file  # 使用下载后的文件名
    else:
        # 如果是本地 M3U 文件
        m3u_file = m3u_input

    # 解析 M3U 文件
    urls = parse_m3u(m3u_file)

    if not urls:
        print("没有找到有效的流媒体地址。")
        return

    # 测试每个 URL
    for url in urls:
        test_url(url)


if __name__ == "__main__":
    # 获取输入
    m3u_input = input("请输入 M3U 文件的 URL 或本地文件路径: ")

    # 根据输入判断是远程文件还是本地文件
    main(m3u_input)
