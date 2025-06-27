import socket
import struct
import datetime  # 新增：导入时间模块用于日志

# 配置 UDP 接收的 IP 和端口
UDP_IP = "192.168.254.101"
UDP_PORT = 12000
# 新增：文件保存路径和基本配置
DATA_FILE = "radar_gps_data.txt"
MAX_RETRY = 3  # 文件写入最大重试次数

# 创建 UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# 新增：文件写入函数
def write_to_file(data_type, content):
    """将数据写入文本文件，包含时间戳和数据类型"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(DATA_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {data_type} 数据:\n")
            f.write(f"{content}\n\n")
        return True
    except Exception as e:
        print(f"文件写入失败: {e}")
        return False

print(f"等待在 {UDP_IP}:{UDP_PORT} 接收数据...")
print(f"数据将自动保存至: {DATA_FILE}")

while True:
    data, addr = sock.recvfrom(1024 * 1024)  # 接收数据
    offset = 0
    header = data[offset:offset + 4]
    offset += 4
    if header == b'\x20\x20\x20\x00':
        # 处理雷达数据
        channel = struct.unpack('i', data[offset:offset + 4])[0]
        offset += 4
        channel_num = struct.unpack('i', data[offset:offset + 4])[0]
        offset += 4
        sample_num = struct.unpack('i', data[offset:offset + 4])[0]
        offset += 4

        radar_data = []
        for _ in range(sample_num):
            data_val = struct.unpack('h', data[offset:offset + 2])[0]
            offset += 2
            radar_data.append(data_val)

        print("雷达数据：")
        print(f"通道：{channel}，道号：{channel_num}，采样点数：{sample_num}")
        print(f"数据：{radar_data}")
        
        # 新增：写入雷达数据到文件
        content = f"通道：{channel}，道号：{channel_num}，采样点数：{sample_num}\n数据：{radar_data}"
        write_to_file("雷达", content)

    elif header == b'\x20\x20\x20\x01':
        # 处理 GPS 数据
        channel_num = struct.unpack('i', data[offset:offset + 4])[0]
        offset += 4
        gps_data = data[offset:].decode('utf-8')

        print("GPS 数据：")
        print(f"道号：{channel_num}，GPS 内容：{gps_data}")
        
        # 新增：写入GPS数据到文件
        content = f"道号：{channel_num}，GPS 内容：{gps_data}"
        write_to_file("GPS", content)

    else:
        print("未知数据头文件，无法解析")
        # 新增：记录未知数据到文件
        content = f"未知数据头：{header.hex()}，原始数据：{data.hex()}"
        write_to_file("未知类型", content)