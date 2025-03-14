#coding:utf-8
import requests
import time


def read_m3u_file(file_path):
    """
    读取 M3U 文件，提取其中的 URL 地址。
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 提取每个 URL
    urls = [line.strip() for line in lines if line.strip().startswith('http')]
    return urls


def check_url_validity(url):
    """
    检查 URL 是否有效
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False


def test_speed(url):
    """
    测试 URL 的下载速度
    """
    try:
        start_time = time.time()
        response = requests.get(url, stream=True, timeout=10)
        total_bytes = 0
        for chunk in response.iter_content(chunk_size=1024):
            total_bytes += len(chunk)
        end_time = time.time()

        download_time = end_time - start_time
        speed = total_bytes / download_time / 1024  # KB/s
        return download_time, speed
    except requests.RequestException:
        return None, None


def main():
    m3u_file_path = input("请输入 M3U 文件路径：")
    urls = read_m3u_file(m3u_file_path)

    for url in urls:
        print(f"检查 URL: {url}")
        is_valid = check_url_validity(url)

        if is_valid:
            print("URL 有效")
            download_time, speed = test_speed(url)
            if download_time is not None:
                print(f"下载时间: {download_time:.2f}秒, 速度: {speed:.2f} KB/s")
            else:
                print("无法获取下载速度")
        else:
            print("URL 无效")
        print("=" * 50)


if __name__ == '__main__':
    main()
