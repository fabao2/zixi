from flask import Flask, jsonify,render_template
import pymysql
from datetime import datetime, timedelta
import os
import glob
import time
import threading
from PIL import Image

from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder='templates')

def get_data_from_db():
    # 模拟数据，不连接数据库
    return [{
        'width': 640,
        'avg_gray': 128,
        'timestamp_column': '2025-06-01_12_00_00',
        'latitude': 3210,  # 实际显示时会除以100，变为32.10
        'longitude': 11850, # 实际显示时会除以100，变为118.50
        'image_path': '/static/images/default.jpg'
    }]

@app.route('/', methods=['GET'])
def index():
    data_points = get_data_from_db()  # 获取数据
    return render_template('index.html', data_points=data_points)  # 将数据传递给模板

@app.route('/api/data', methods=['GET'])
def get_data():
    data_points = get_data_from_db()
    return jsonify(data_points)

def monitor_and_rename(folder_path):
    while True:
        files = glob.glob(os.path.join(folder_path, '*.jpg'))
        if files:
            latest_file = max(files, key=os.path.getmtime)
            target_path = os.path.join(folder_path, 'zhanshi.jpg')
            if latest_file != target_path:
                try:
                    with Image.open(latest_file) as img:
                        resized_img = img.resize((650, 600), Image.LANCZOS)
                        resized_img.save(target_path)
                        print(f"Resized and renamed {latest_file} to {target_path}")
                    os.remove(latest_file)
                    print(f"Deleted original file: {latest_file}")
                except Exception as e:
                    print(f"Error processing file {latest_file}: {e}")
            time.sleep(5)
folder_to_monitor = 'E:\\liangfabao\\xiangmu\\haozhu\\发送图片\\static\\images'
monitor_thread = threading.Thread(target=monitor_and_rename, args=(folder_to_monitor,))
monitor_thread.daemon = True
monitor_thread.start()

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用缓存
if __name__ == "__main__":
    app.run(debug=True)