import requests
import time
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import subprocess
import xml.etree.ElementTree as ET


# 下载远程文件
def download_file(url, local_filename_prefix="playlist"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    local_filename = f"{local_filename_prefix}_{timestamp}{os.path.splitext(url)[-1]}"

    response = requests.get(url)
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            f.write(response.content)
        print(f"文件已下载到 {local_filename}")
        return local_filename
    else:
        print(f"无法下载文件，HTTP 错误代码: {response.status_code}")
        return None


# 解析 M3U 文件
def parse_m3u(file_path):
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在！")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.readlines()

    channels = []
    current_channel = None

    for line in content:
        line = line.strip()
        if line.startswith("#EXTINF"):
            parts = line.split(",")
            if len(parts) > 1:
                current_channel = parts[1].strip()
        elif line.startswith("http"):
            if current_channel:
                channels.append((current_channel, line))
                current_channel = None

    return channels


# 解析 PLS 文件
def parse_pls(file_path):
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在！")
        return []

    channels = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith("File"):
            parts = line.split("=")
            if len(parts) == 2:
                channels.append(("Unknown Channel", parts[1]))

    return channels


# 解析 XSPF 文件
def parse_xspf(file_path):
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在！")
        return []

    channels = []
    tree = ET.parse(file_path)
    root = tree.getroot()

    for track in root.findall(".//track"):
        location = track.find("location")
        title = track.find("title")
        if location is not None:
            url = location.text.strip()
            name = title.text.strip() if title is not None else "Unknown Channel"
            channels.append((name, url))

    return channels


# 选择解析方法
def parse_playlist(file_path):
    extension = os.path.splitext(file_path)[-1].lower()
    if extension == ".m3u":
        return parse_m3u(file_path)
    elif extension == ".pls":
        return parse_pls(file_path)
    elif extension == ".xspf":
        return parse_xspf(file_path)
    else:
        print("不支持的文件格式！")
        return []


# 截取画面并保存
def capture_snapshot(index, channel_name, url):
    snapshot_folder = "snapshot"
    os.makedirs(snapshot_folder, exist_ok=True)  # 确保目录存在

    snapshot_filename = os.path.join(snapshot_folder, f"{index}_{channel_name}.jpg")

    # 调用 ffmpeg 截取视频流的一帧作为截图
    command = [
        "ffmpeg", "-i", url, "-vframes", "1", "-q:v", "2", "-timeout", "30", snapshot_filename
    ]
    try:
        subprocess.run(command, check=True, timeout=30)  # 设置超时为30秒
        print(f"截图已保存到 {snapshot_filename}")
    except subprocess.CalledProcessError:
        print(f"无法从 {url} 获取截图")
    except subprocess.TimeoutExpired:
        print(f"从 {url} 获取截图时超时")



# 测试 URL
def test_url(index, channel_name, url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            elapsed_time = time.time() - start_time
            speed = len(response.content) / elapsed_time / 1024  # KB/s
            print(f"{index}. {channel_name} - {url} | 下载速度: {speed:.2f} KB/s")
            capture_snapshot(index, channel_name, url)  # 如果可用，截取画面
        else:
            print(f"{index}. {channel_name} - {url} | HTTP 错误代码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{index}. {channel_name} - {url} | 错误: {e}")


# 主函数
def main(input_path, max_threads=10):
    is_remote = input_path.startswith("http://") or input_path.startswith("https://")

    if is_remote:
        downloaded_file = download_file(input_path)
        if downloaded_file is None:
            return
        playlist_file = downloaded_file
    else:
        playlist_file = input_path

    channels = parse_playlist(playlist_file)

    if not channels:
        print("没有找到有效的流媒体地址。")
        return

    with ThreadPoolExecutor(max_threads) as executor:
        for index, (channel_name, url) in enumerate(channels, 1):
            executor.submit(test_url, index, channel_name, url)


if __name__ == "__main__":
    input_path = input("请输入播放列表文件的 URL 或本地路径: ")
    main(input_path)
