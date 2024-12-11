import datetime

def convert_to_srt_time(seconds):
    """
    将秒数转换为 SRT 时间格式 (HH:MM:SS,MS)
    """
    dt = datetime.datetime(1900, 1, 1) + datetime.timedelta(seconds=seconds)
    ms = dt.microsecond // 1000
    return f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d},{ms:03d}"

# 示例用法
seconds = 162.875
srt_time = convert_to_srt_time(seconds)
print(srt_time)