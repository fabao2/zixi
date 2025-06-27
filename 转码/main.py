import cv2
from numpy import ndarray
import torch
from HK import HKCamera
from ultralytics import YOLO
import time
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import sqlite3
import print111
import torch.cuda
from tkinter import font
import threading
import os
import pymysql
# 检查 GPU 是否可用
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# 加载 YOLOv8 模型
model = YOLO('5.19 bamboo.pt')
dev = print111.operate_usb_device()
# 初始化数据库
# def init_db():
#     conn = sqlite3.connect('bamboo.db')
#     conn.commit()
#     conn.close()

def time_zh():
    time1=' '
    timestamp = int(time.time())
    # 将时间戳转换为字符串，方便逐位处理
    timestamp_str = str(timestamp)
    # 存储每个数字的十六进制表示
    hex_ascii_list = []
    for digit in timestamp_str:
        # 获取字符的 ASCII 码值
        ascii_code = ord(digit)
        # 将 ASCII 码值转换为十六进制字符串
        hex_ascii = hex(ascii_code)
        # 去掉 0x 前缀
        hex_without_prefix = hex_ascii[2:]
        hex_ascii_list.append(hex_without_prefix)
        # 用空格连接列表元素成字符串
    result_str = ' '.join(hex_ascii_list)
    return result_str

def time_xs():
    timestamp = int(time.time())
    tre_timeArray = time.localtime(timestamp)
    timestamp_str=time.strftime("%Y%m%d%H%M%S", tre_timeArray)
    hex_ascii_list = []
    for digit in timestamp_str:
        # 获取字符的 ASCII 码值
        ascii_code = ord(digit)
        # 将 ASCII 码值转换为十六进制字符串
        hex_ascii = hex(ascii_code)
        # 去掉 0x 前缀
        hex_without_prefix = hex_ascii[2:]
        hex_ascii_list.append(hex_without_prefix)
        # 用空格连接列表元素成字符串
    result_str = ' '.join(hex_ascii_list)
    return result_str

def str_to_asci(input_str):
    try:
        gbk_bytes = input_str.encode('gbk')
        return gbk_bytes
    except UnicodeEncodeError:
        print(f"字符串 {input_str} 无法转换为 GBK 编码。")
        return b''
def chinese_to_hex(input_str, encoding='gbk'):
    """
    将汉字字符串转换为十六进制码

    :param input_str: 输入的汉字字符串
    :param encoding: 编码方式，默认为 GBK
    :return: 十六进制码字符串
    """
    try:
        # 将字符串按指定编码方式编码成字节序列
        encoded_bytes = input_str.encode(encoding)
        # 将字节序列转换为十六进制字符串，并添加空格分隔
        hex_str = ' '.join([f'{byte:02x}' for byte in encoded_bytes]).upper()
        return hex_str
    except UnicodeEncodeError:
        print(f"字符串 {input_str} 无法使用 {encoding} 编码。")
        return ""
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("登录界面")
        # 扩大登录界面大小
        self.geometry("400x300")
        # 将登录界面置于屏幕中央
        self.center_window()
        self.username_label = tk.Label(self, text="选择账户:")
        self.username_label.pack(pady=10)

        self.usernames = ["研发", "管理", "操作"]
        self.username_var = tk.StringVar(self)
        self.username_var.set(self.usernames[0])
        self.username_menu = tk.OptionMenu(self, self.username_var, *self.usernames)
        self.username_menu.pack(pady=5)

        self.password_label = tk.Label(self, text="输入密码:")
        self.password_label.pack(pady=10)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = tk.Button(self, text="登录", command=self.login)
        self.login_button.pack(pady=20)

    def center_window(self):
        """将窗口置于屏幕中央"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def login(self):
        username = self.username_var.get()
        password = self.password_entry.get()
        if password == "":
            self.destroy()
            root = tk.Tk()
            app = CameraApp(root)
            # 获取屏幕宽度和高度
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()-root.winfo_screenheight()//20
            # 设置窗口大小
            root.geometry(f"{screen_width}x{screen_height}")

            # 将窗口置于屏幕中央
            x = 0
            y = 0
            root.geometry(f"+{x}+{y}")
            root.configure(bg="blue")
            root.mainloop()

        else:
            messagebox.showerror("登录失败", "密码错误，请重试。")
def vertical_text(text):
    return '\n'.join(text)
def image_to_tk(file_path, size):
    try:
        image = Image.open(file_path)
        image = image.resize((size, size), Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"图片加载失败: {e}")
        return None

class CameraApp:
        def __init__(self, root):
            self.root = root
            self.root.title("怀清号竹检测设备")
            self.camera = None
            self.is_capturing = False  # 新增标志位
            self.is_comparing = False  # 新增比较坐标运行标志位
            # 创建按钮框架，将按钮放在同一行
            button_frame = tk.Frame(root)
            button_frame.pack(side=tk.BOTTOM, fill=tk.X)
            button_frame1 = tk.Frame(root)
            button_frame1.pack(side=tk.TOP, fill=tk.X)
        # 获取屏幕宽度
            screen_width = self.root.winfo_screenwidth()
        # 计算按钮宽度为屏幕宽度的一半
            button_width = screen_width // 5
            image_path = "C:/a/图标/连接相机.png"

            if os.path.exists(image_path):
                self.image = image_to_tk(image_path, button_width)
        # 创建一个字体对象，根据按钮宽度动态调整字体大小
        # 这里简单设置一个初始字体大小，你可以根据实际情况调整
            button_font = font.Font(size=20)
            self.connect_button = tk.Button(button_frame,image=self.image ,command=self.connect_camera, width=button_width-15,height=button_width-15)
            self.connect_button.pack(side=tk.LEFT, padx=5, pady=10)
            image_path = "C:/a/图标/开始工作.png"
            if os.path.exists(image_path):
                self.image1 = image_to_tk(image_path, button_width)
            self.capture_button = tk.Button(button_frame,image=self.image1, command=self.start_capture,
                                        state=tk.DISABLED, width=button_width-15,height=button_width-15,activebackground='lightblue')
            self.capture_button.pack(side=tk.LEFT, padx=5, pady=10)
            image_path = "C:/a/图标/停止工作.png"
            if os.path.exists(image_path):
                self.image2 = image_to_tk(image_path, button_width)
            self.stop_button = tk.Button(button_frame, image=self.image2,command=self.stop_capture,
                                     state=tk.DISABLED, width=button_width-15,height=button_width-15, activebackground='lightblue')
            self.stop_button.pack(side=tk.LEFT, padx=5, pady=10)
            image_path = "C:/a/图标/查询数据库.png"
            if os.path.exists(image_path):
                self.image3 = image_to_tk(image_path, button_width)
            self.query_button = tk.Button(button_frame, image=self.image3, command=self.query_database,
                                      width=button_width-15,height=button_width-15,activebackground='lightblue')
            self.query_button.pack(side=tk.LEFT, padx=5, pady=0)
            image_path = "C:/a/图标/对比坐标.png"
            if os.path.exists(image_path):
                self.image4 = image_to_tk(image_path, button_width)
        # 新增查询坐标比较按钮
            self.compare_coords_button = tk.Button(button_frame, image=self.image4,
                                               command=self.compare_coordinates, width=button_width-10,height=button_width-10,
                                               activebackground='lightblue')
            self.compare_coords_button.pack(side=tk.LEFT, padx=5, pady=10)
            # 加载图片
            top_frame = tk.Frame(self.root)
            top_frame.pack(side=tk.TOP, fill=tk.X)

            # 时间标签
            self.time_label = tk.Label(top_frame, text=time.strftime("%Y-%m-%d %H:%M:%S"), font='30')
            self.time_label.pack(side=tk.LEFT, padx=0, pady=0)
            self.update_time()

            # 输入阈值相关控件框架
            input_frame = tk.Frame(top_frame)
            input_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)

            tk.Label(input_frame, text="请输入阈值:").pack(side=tk.LEFT, padx=5)
            self.threshold_entry = tk.Entry(input_frame)
            self.threshold_entry.insert(0,'0.000000000000000001')
            self.threshold_entry.pack(side=tk.LEFT, padx=5)

            try:
                image_path = "C:/a/图标/1.png"  # 替换为实际图片路径
                img = Image.open(image_path)
                img = img.resize((250, 70), Image.LANCZOS)  # 调整图片大小
                self.photo = ImageTk.PhotoImage(img)
                self.image_label = tk.Label(top_frame, image=self.photo)
                self.image_label.pack(side=tk.RIGHT, padx=0, pady=0)  # 放置在右上角
            except FileNotFoundError:
                print("图片未找到，请检查路径。")

            # 文本显示框
            self.label_text = tk.Text(self.root, height=270, width=20, font='70')
            self.label_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        def update_time(self):
            self.time_label.config(text=time.strftime("%Y-%m-%d %H:%M:%S"))
            self.root.after(1000, self.update_time)

        def update_time(self):
            # 更新 Label 控件的文本
            self.time_label.config(text=time.strftime("%Y-%m-%d %H:%M:%S"))
            # 每隔 1000 毫秒（即 1 秒）调用一次 update_time 函数
            self.root.after(1000, self.update_time)

        def connect_camera(self):
            self.label_text.delete(1.0, tk.END)
            self.label_text.insert(tk.END, "相机正在连接。。。。\n")
            self.label_text.update_idletasks()
            try:

                self.camera = HKCamera(CameraIp='192.168.0.55')
                # 对摄像头配置进行设置
                self.camera.set_Value(param_type="enum_value", node_name="PixelFormat",
                                      node_value='RGB8Packed')
                # 设置自动曝光
                self.camera.set_Value(param_type="enum_value", node_name="ExposureAuto",
                                      node_value='Continuous')  # 假设 Continuous 表示连续自动曝光，具体值按相机文档调整
                self.camera.start_camera()
                self.capture_button.config(state=tk.NORMAL)
                self.connect_button.config(state=tk.DISABLED)
                self.label_text.insert(tk.END, "相机连接完成。。。。\n")
            except Exception as e:
                error_message = f"相机连接失败。。。。\n错误原因: {str(e)}\n"
                self.label_text.insert(tk.END, error_message)
                print(e)


        def start_capture(self):
            self.is_comparing = False
            self.is_capturing = True
            self.capture_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.capture_loop()

        def stop_capture(self):
            self.is_capturing = False
            self.capture_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

        def capture_loop(self):
            if self.is_capturing:
                self.compare_coords_button.config(state=tk.NORMAL)
                threshold_input = self.threshold_entry.get()
                try:
                    threshold = float(threshold_input)
                except ValueError:
                    tk.messagebox.showerror("输入错误", "请输入有效的数字作为阈值！")
                    self.is_comparing = False
                    self.compare_coords_button.config(state=tk.NORMAL)
                    return
                try:
                    Caiji = print111.write_com_port("COM6")
                    if Caiji:
                        image: ndarray = self.camera.get_image()

                    if image is not None:
                        # 转换为 BGR 格式，因为 YOLOv8 默认使用 BGR
                        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                        img = Image.fromarray(image)
                        timestamp = time.strftime("%Y-%m-%d %H_%M_%S")
                        save_path = 'C:/a/jianceqian/' + timestamp + '.jpg'
                        img.save(save_path)
                        # 使用 YOLOv8 进行检测
                        results = model(image)
                        # 获取检测结果并过滤低置信度检测框
                        filtered_results = []
                        for result in results:
                            boxes = result.boxes
                            keep = [i for i, box in enumerate(boxes) if float(box.conf) >= 0.2]
                            filtered_results.append(result[keep])

                        # 筛选最接近图片中心的检测框
                        closest_result = None
                        min_distance = float('inf')
                        image_height, image_width = image.shape[:2]
                        center_x, center_y = image_width/2, image_height/2
                        min_distance = float('inf')
                        closest_box = None
                        
                        # 遍历所有检测结果
                        for result in filtered_results:
                            for box in result.boxes:
                                # 计算检测框中心坐标
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                box_center = ((x1+x2)/2, (y1+y2)/2)
                                
                                # 计算欧式距离
                                distance = ((box_center[0]-center_x)**2 + (box_center[1]-center_y)**2)**0.5
                                
                                # 更新最近检测框
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_box = box
                        # 新增结束
                        
                        # 仅保留最近检测框
                        filtered_results = [closest_box] if closest_box else []
                        for result in filtered_results:
                            boxes = result.boxes
                            for box in boxes:
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                box_center_x = (x1 + x2) / 2
                                box_center_y = (y1 + y2) / 2
                                distance = ((box_center_x - center_x) ** 2 + (box_center_y - center_y) ** 2) ** 0.5
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_result = result
                                    closest_box = box
                        
                        if closest_result is not None:
                            # 获取过滤后的检测结果并绘制在图像上
                            annotated_frame = closest_result.plot() if len(filtered_results) > 0 else image
                        
                            # 转换为灰度图像以计算平均灰度
                            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        
                            try:
                                conn = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="bamboo")
                                c = conn.cursor()
                                # 修改表结构，添加 latitude 和 longitude 字段
                                create_table_query = '''
                                CREATE TABLE IF NOT EXISTS segmentation_results (
                                    id INT PRIMARY KEY AUTO_INCREMENT,
                                    class_name TEXT,
                                    confidence REAL,
                                    area REAL,
                                    width REAL,
                                    avg_gray REAL,
                                    timestamp TEXT,
                                    latitude TEXT, 
                                    longitude TEXT
                                )
                                '''
                                c.execute(create_table_query)
                        
                                # 收集需要显示的信息
                                display_info = []
                                if hasattr(results[0], 'masks') and results[0].masks is not None:
                                    masks = results[0].masks.data.to(device).cpu().numpy() if torch.cuda.is_available() else \
                                        results[0].masks.data.numpy()
                                    boxes = results[0].boxes
                                    for i, box in enumerate(boxes):
                                        if float(box.conf) >= 0.1:
                                            class_id = int(box.cls.item())
                                            class_name = model.names[class_id]
                                            confidence = float(box.conf.cpu().numpy())
                        
                                            mask = masks[i]
                                            # 将掩码转换为合适的形状和尺寸
                                            mask = cv2.resize(mask.astype('uint8') * 255,
                                                              (gray_image.shape[1], gray_image.shape[0]))
                                            # 计算分割区域的轮廓
                                            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                            for contour in contours:
                                                # 计算分割区域的面积
                                                area = cv2.contourArea(contour)
                                                # 获取分割区域的边界框
                                                x, y, w, h = cv2.boundingRect(contour)
                                                if h > 0:
                                                    calculated_width = area / h * 0.1091
                                                else:
                                                    calculated_width = 0
                                                # 确保掩码和灰度图像尺寸一致
                                                if mask.shape == gray_image.shape:
                                                    # 计算分割区域内的灰度平均值
                                                    masked_gray = cv2.bitwise_and(gray_image, gray_image, mask=mask)
                                                    mean_gray = cv2.mean(masked_gray, mask=mask)[0]
                                                    text = f"Width: {calculated_width:.2f}, Gray: {mean_gray:.2f}"
                                                    cv2.putText(annotated_frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                                (0, 255, 0), 3)
                                                    timestamp = time.strftime("%Y-%m-%d%H:%M:%S")
                                                    North, South = print111.read_com_port("COM3")
                                                    c.execute("SELECT latitude, longitude FROM segmentation_results")
                                                    rows = c.fetchall()
                                                    for row in rows:
                                                        db_latitude, db_longitude = row
                                                        if abs(float(North) - db_latitude) < threshold and abs(float(South) - db_longitude) < threshold:
                                                            tk.messagebox.showwarning("报警", "该竹子已检测！")
                                                            break
                                                    # 仅插入最接近中心的检测结果
                                                    try:
                                                        c.execute(
                                                            "INSERT INTO segmentation_results (class_name, confidence, area, width, avg_gray, timestamp, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                                            (class_name, confidence, area, calculated_width, mean_gray, timestamp, North, South)
                                                        )
                                                    except sqlite3.Error as e:
                                                        print(f"数据库插入失败，错误信息: {e}")
                                                        print(f"插入的数据: {class_name}, {confidence}, {area}, {calculated_width}, {mean_gray}, {timestamp}, {North}, {South}")
                        
                                            # 显示信息
                                            display_info.append(f"类别名称: {class_name}, 置信度: {confidence:.2f}, 面积: {area:.2f}, 宽度: {calculated_width:.2f}, 平均灰度: {mean_gray:.2f}, 时间戳: {timestamp}, 北纬: {North}, 东经: {South}")
                                        conn.commit()
                                    except Exception as e:
                                        print(e)
                                        # 发生异常时回滚事务
                                        if conn:
                                            conn.rollback()
                                    finally:
                                        # 确保连接关闭
                                        if conn:
                                            conn.close()

                                        # 显示检测到的标签
                                        detected_labels = []
                                        boxes = results[0].boxes
                                        for box in boxes:
                                            if float(box.conf) >= 0.2:
                                                class_id = int(box.cls.item())
                                                class_name = model.names[class_id]
                                                detected_labels.append(class_name)
                                        self.label_text.delete(1.0, tk.END)
                                        self.label_text.insert(tk.END, "检测到的标签:\n" + "\n".join(display_info))
                                        print111.print_zuobiao(dev, calculated_width)
                                        # # 转换为适合 tkinter 显示的格式
                                        timestamp = time.strftime("%Y-%m-%d %H_%M_%S")
                                        save_path = 'C:/a/jiancebaocun/'+timestamp+'.jpg'

                                        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                                        img = Image.fromarray(annotated_frame)
                                        img.save(save_path)
                                        # # 获取可用的显示区域大小
                                        # self.root.update_idletasks()
                                        # available_width = self.root.winfo_width()
                                        # available_height = self.root.winfo_height() - self.label_text.winfo_height()

                                        # # 计算缩放比例
                                        # img_width, img_height = img.size
                                        # width_ratio = (available_width - 100) / img_width
                                        # height_ratio = (available_height - 100) / img_height
                                        # scale_ratio = min(width_ratio, height_ratio)

                                        # # 缩放图片
                                        # new_width = int(img_width * scale_ratio)
                                        # new_height = int(img_height * scale_ratio)
                                        # img = img.resize((new_width, new_height), Image.LANCZOS)

                                        # img = ImageTk.PhotoImage(image=img)
                                        # self.image_label.config(image=img)
                                        # self.image_label.image = img

                                except Exception as e:
                                    print(e)

                                # 递归调用 capture_loop 实现循环
                                self.root.after(100, self.capture_loop)

        def query_database(self):
            try:
                # 创建查询窗口
                query_window = tk.Toplevel(self.root)
                query_window.title("数据库查询")

                # 创建输入框和按钮的框架
                input_frame = tk.Frame(query_window)
                input_frame.pack(fill=tk.X, padx=10, pady=10)

                # 创建标签和输入框
                tk.Label(input_frame, text="请输入编号:").pack(side=tk.LEFT, padx=5)
                entry = tk.Entry(input_frame)
                entry.pack(side=tk.LEFT, padx=5)

                def perform_query():
                    # 获取用户输入的编号
                    query_id = entry.get()

                    # 检查输入位数是否正确，这里假设正确位数是 14 位
                    if len(query_id) != 14:
                        messagebox.showerror("输入错误", "输入的编号位数不正确，请检查！")
                        return
                    formatted_query_id = f"{query_id[:4]}-{query_id[4:6]}-{query_id[6:8]} {query_id[8:10]}:{query_id[10:12]}:{query_id[12:]}"

                    try:
                        # 清空 Treeview 中的现有数据
                        for item in tree.get_children():
                            tree.delete(item)

                        conn = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="bamboo")
                        c = conn.cursor()
                        # 假设比对的列名为 timestamp，可根据实际情况修改
                        c.execute("SELECT * FROM segmentation_results WHERE timestamp = %s", (formatted_query_id,))
                        rows = c.fetchall()

                        if not rows:
                            messagebox.showerror("查询结果", "未找到匹配的记录，请检查输入的编号！")
                        else:
                            for row in rows:
                                tree.insert('', 'end', values=row)

                        conn.close()
                    except Exception as e:
                        print(e)

                def show_all_data():
                    try:
                        # 清空输入框
                        entry.delete(0, tk.END)
                        # 清空 Treeview 中的现有数据
                        for item in tree.get_children():
                            tree.delete(item)

                        conn = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="bamboo")
                        c = conn.cursor()
                        c.execute("SELECT * FROM segmentation_results")
                        rows = c.fetchall()

                        for row in rows:
                            tree.insert('', 'end', values=row)

                        conn.close()
                    except Exception as e:
                        print(e)

                # 创建查询按钮
                tk.Button(input_frame, text="查询", command=perform_query).pack(side=tk.LEFT, padx=5)
                # 创建显示所有数据按钮
                tk.Button(input_frame, text="显示所有数据", command=show_all_data).pack(side=tk.LEFT, padx=5)

                # 创建一个框架来包含 Treeview 和 Scrollbar
                tree_frame = tk.Frame(query_window)
                tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

                # 更新列名以匹配数据库表结构
                tree = ttk.Treeview(tree_frame, columns=(
                    'ID', '类别名称', '置信度', '面积', '宽度', '平均灰度', '时间戳', '北纬', '东经'),
                                    show='headings')
                tree.heading('ID', text='ID')
                tree.heading('类别名称', text='类别名称')
                tree.heading('置信度', text='置信度')
                tree.heading('面积', text='面积')
                tree.heading('宽度', text='宽度')
                tree.heading('平均灰度', text='平均灰度')
                tree.heading('时间戳', text='时间戳')
                tree.heading('北纬', text='北纬')
                tree.heading('东经', text='东经')

                # 创建垂直滚动条
                vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
                vsb.pack(side='right', fill='y')
                tree.configure(yscrollcommand=vsb.set)

                # 创建水平滚动条
                hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
                hsb.pack(side='bottom', fill='x')
                tree.configure(xscrollcommand=hsb.set)

                tree.pack(side='left', fill=tk.BOTH, expand=True)

            except Exception as e:
                print(e)

        def compare_coordinates(self):
            self.compare_thread = threading.Thread(target=self._compare_coordinates_task)
            if self.compare_thread is None or not self.compare_thread.is_alive():
                self.compare_thread.start()

        def _compare_coordinates_task(self):
            self.is_comparing = True
            self.compare_coords_button.config(state=tk.DISABLED)
            while self.is_comparing:
                try:
                    # 获取当前坐标
                    Caiji = print111.write_com_port("COM6")
                    try:
                        threshold_input = self.threshold_entry.get()
                        threshold = float(threshold_input)
                    except ValueError:
                        tk.messagebox.showerror("输入错误", "请输入有效的数字作为阈值！")
                        self.is_comparing = False
                        self.compare_coords_button.config(state=tk.NORMAL)
                        return

                    while Caiji:
                        time.sleep(1)
                        North, South = print111.read_com_port("COM3")
                        conn = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="bamboo")
                        c = conn.cursor()
                        c.execute("SELECT latitude, longitude FROM segmentation_results")
                        rows = c.fetchall()

                        # 清空 Text 控件内容
                        self.label_text.delete(1.0, tk.END)

                        found = False
                        for row in rows:
                            db_latitude, db_longitude = row
                            if abs(float(North) - db_latitude) < threshold and abs(
                                    float(South) - db_longitude) < threshold:
                                found = True
                                # 将数据添加到 Text 控件中
                                info = f"纬度: {db_latitude}, 经度: {db_longitude}\n"
                                self.label_text.insert(tk.END, info)

                        if not found:
                            # 没有符合条件的数据，报警提示
                            tk.messagebox.showwarning("报警", "未检测到符合阈值条件的竹子坐标！")

                        Caiji = print111.write_com_port("COM6")
                        conn.close()
                except Exception as e:
                    print(e)



if __name__ == '__main__':
    # init_db()
    login_window = LoginWindow()
    login_window.mainloop()



