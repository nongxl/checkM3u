import requests
import time
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


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


# 从本地 M3U 文件解析出地址和频道名称
def parse_m3u(file_path):
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在！")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:  # 使用 utf-8 编码打开文件
        content = f.readlines()

    channels = []
    current_channel = None

    for line in content:
        line = line.strip()

        # 如果是频道名称（以 #EXTINF 开头）
        if line.startswith("#EXTINF"):
            parts = line.split(",")
            if len(parts) > 1:
                channel_name = parts[1].strip()
                current_channel = channel_name
        # 如果是 URL（以 http:// 或 https:// 开头）
        elif line.startswith("http"):
            if current_channel:
                channels.append((current_channel, line))  # 存储频道名称和 URL
                current_channel = None  # 清空当前频道名称

    return channels


# 测试地址的有效性和速度
def test_url(index, channel_name, url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)  # 设置超时时间10秒
        if response.status_code == 200:
            elapsed_time = time.time() - start_time
            speed = len(response.content) / elapsed_time / 1024  # 速度单位 KB/s
            print(f"{index}. {channel_name} - {url} | 下载速度: {speed:.2f} KB/s")
        else:
            print(f"{index}. {channel_name} - {url} | HTTP 错误代码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{index}. {channel_name} - {url} | 错误: {e}")


# 主函数
def main(m3u_input, max_threads=10):
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
    channels = parse_m3u(m3u_file)

    if not channels:
        print("没有找到有效的流媒体地址。")
        return

    # 使用线程池并行测试 URL
    with ThreadPoolExecutor(max_threads) as executor:
        # 使用 enumerate 为每个频道添加索引，方便输出时显示序号
        for index, (channel_name, url) in enumerate(channels, 1):
            executor.submit(test_url, index, channel_name, url)  # 提交每个 URL 测试任务


if __name__ == "__main__":
    # 获取输入
    m3u_input = input("请输入 M3U 文件的 URL 或本地文件路径: ")

    # 根据输入判断是远程文件还是本地文件
    main(m3u_input)
