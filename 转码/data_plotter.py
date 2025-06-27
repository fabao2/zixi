class DataPlotter:
    # ... existing code ...

    def combine_and_save(self, images_per_page=10, skip_first=0):
        """每10张图像合并保存（横向十列布局）"""
        if not self.arrays:
            print("没有可处理的数据数组")
            return

        # 新增：跳过前N组数据
        if skip_first > 0:
            if len(self.arrays) <= skip_first:
                print(f"警告：数据组数({len(self.arrays)})小于跳过数量({skip_first})，将处理全部数据")
            else:
                self.arrays = self.arrays[skip_first:]
                print(f"已跳过前{skip_first}组数据，剩余{len(self.arrays)}组")

        total_pages = (len(self.arrays) + images_per_page - 1) // images_per_page
        print(f"开始生成图像，共 {total_pages} 页...")

        for page in range(total_pages):
            start = page * images_per_page
            end = min((page+1)*images_per_page, len(self.arrays))
            page_arrays = self.arrays[start:end]

            # 修改：十列布局（1行10列）
            rows = 1
            cols = images_per_page
            fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))  # 横向扩展画布
            axes = axes.flatten() if rows*cols > 1 else [axes]

            # 绘制每页图像
            for i, (data_id, data) in enumerate(page_arrays):
                ax = axes[i]
                x = np.arange(1, len(data)+1)
                ax.plot(x, data, 'b-', marker='o', markersize=2, linewidth=0.8)
                ax.set_title(f'组{data_id}', fontsize=10)
                ax.tick_params(axis='both', labelsize=8)
                ax.grid(True, linestyle='--', alpha=0.5)
                # 优化：自动调整Y轴范围，突出数据变化
                ax.autoscale(enable=True, axis='y', tight=True)

            # 隐藏空白子图
            for j in range(len(page_arrays), len(axes)):
                axes[j].axis('off')

            # ... existing code ...