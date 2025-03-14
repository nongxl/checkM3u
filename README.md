# checkM3u
批量检测直播源文件中的地址有效性和测速，支持多线程，max_threads=10

支持本地文件和远程地址（通过输入内容开头的http判断是远程地址还是本地文件），支持m3u、pls和xspf格式

如果系统安装有ffmpeg，会在检测到有效直播地址后尝试获取截图

运行方式 python3 check.py
