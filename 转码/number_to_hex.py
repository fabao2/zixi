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
                        # 获取过滤后的检测结果并绘制在图像上
                        annotated_frame = filtered_results[0].plot() if len(filtered_results) > 0 else image

                        # 转换为灰度图像以计算平均灰度
                        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    try:
                        conn = pymysql.connect(host="127.0.0.1",user="root",password="123456",database="bamboo")
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
                                            # 计算分割后的区域宽度*像素比0.1091
                                            calculated_width = area / h * 0.1091

                                        else:
                                            calculated_width = 0
                                        # 确保掩码和灰度图像尺寸一致
                                        if mask.shape == gray_image.shape:
                                            # 计算分割区域内的灰度平均值
                                            masked_gray = cv2.bitwise_and(gray_image, gray_image, mask=mask)
                                            mean_gray = cv2.mean(masked_gray, mask=mask)[0]

                                            # 在检测后的图像上显示宽度和灰度值，增大字体大小和线条粗细
                                            text = f"Width: {calculated_width:.2f}, Gray: {mean_gray:.2f}"
                                            cv2.putText(annotated_frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                        (0, 255, 0), 3)
                                            timestamp = time.strftime("%Y-%m-%d%H:%M:%S")
                                            North, South = print111.read_com_port("COM3")
                                            c.execute("SELECT latitude, longitude FROM segmentation_results")
                                            rows = c.fetchall()
                                            for row in rows:
                                                db_latitude, db_longitude = row
                                                if abs(float(North) - db_latitude) < threshold and abs(
                                                        float(South) - db_longitude) < threshold:
                                                    tk.messagebox.showwarning("报警", "该竹子已检测！")
                                                    break
                                            # 插入数据到新表
                                            try:
                                                # 插入数据到新表
                                                c.execute(
                                                    "INSERT INTO segmentation_results (class_name, confidence, area, width, avg_gray, timestamp, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                                    (class_name, confidence, area, calculated_width, mean_gray,
                                                     timestamp, North, South)
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