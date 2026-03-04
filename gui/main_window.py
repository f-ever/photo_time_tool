"""
主GUI窗口
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pathlib import Path
from datetime import datetime

from gui.widgets import DateTimePicker, RelativeTimeInput
from core.batch_processor import scan_directory, process_photos, BatchProcessorError
from utils.logger import Logger, configure_text_widget_tags


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("照片时间修改工具 v1.0")
        self.root.geometry("800x650")
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap("resources/app.ico")
        except:
            pass
        
        # 变量
        self.directory_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="current")
        self.recursive_var = tk.BooleanVar(value=True)
        self.processing = False
        
        # 创建GUI组件
        self.create_widgets()
        
        # 初始化日志
        self.logger = Logger(self.log_text)
        configure_text_widget_tags(self.log_text)
        
        self.logger.info("照片时间修改工具已启动")
        self.logger.info("支持的格式: JPEG, TIFF")
    
    def create_widgets(self):
        """创建所有GUI组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # 1. 目录选择区域
        self.create_directory_section(main_frame, 0)
        
        # 2. 修改模式选择区域
        self.create_mode_section(main_frame, 1)
        
        # 3. 参数输入区域
        self.create_params_section(main_frame, 2)
        
        # 4. 操作按钮区域
        self.create_buttons_section(main_frame, 3)
        
        # 5. 日志显示区域
        self.create_log_section(main_frame, 4)
    
    def create_directory_section(self, parent, row):
        """创建目录选择区域"""
        frame = ttk.LabelFrame(parent, text="目标目录", padding="10")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        # 目录路径输入
        ttk.Label(frame, text="目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        dir_entry = ttk.Entry(frame, textvariable=self.directory_var)
        dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(frame, text="浏览...", command=self.browse_directory)
        browse_btn.grid(row=0, column=2)
        
        # 递归选项
        recursive_check = ttk.Checkbutton(
            frame,
            text="包括子目录",
            variable=self.recursive_var
        )
        recursive_check.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
    
    def create_mode_section(self, parent, row):
        """创建修改模式选择区域"""
        frame = ttk.LabelFrame(parent, text="修改模式", padding="10")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 当前时间
        rb_current = ttk.Radiobutton(
            frame,
            text="修改为当前时间",
            variable=self.mode_var,
            value="current",
            command=self.on_mode_changed
        )
        rb_current.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # 指定时间
        rb_specified = ttk.Radiobutton(
            frame,
            text="修改为指定时间",
            variable=self.mode_var,
            value="specified",
            command=self.on_mode_changed
        )
        rb_specified.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # 相对时间
        rb_relative = ttk.Radiobutton(
            frame,
            text="相对时间调整 (基于照片当前时间)",
            variable=self.mode_var,
            value="relative",
            command=self.on_mode_changed
        )
        rb_relative.grid(row=2, column=0, sticky=tk.W, pady=2)
    
    def create_params_section(self, parent, row):
        """创建参数输入区域"""
        self.params_frame = ttk.LabelFrame(parent, text="参数设置", padding="10")
        self.params_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 指定时间选择器
        self.datetime_picker = DateTimePicker(self.params_frame)
        
        # 相对时间输入
        self.relative_input = RelativeTimeInput(self.params_frame)
        
        # 默认显示指定时间选择器
        self.on_mode_changed()
    
    def create_buttons_section(self, parent, row):
        """创建操作按钮区域"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 开始处理按钮
        self.process_btn = ttk.Button(
            frame,
            text="开始修改",
            command=self.start_processing,
            style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 清空日志按钮
        clear_btn = ttk.Button(
            frame,
            text="清空日志",
            command=self.clear_log
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 导出日志按钮
        export_btn = ttk.Button(
            frame,
            text="导出日志",
            command=self.export_log
        )
        export_btn.pack(side=tk.LEFT)
    
    def create_log_section(self, parent, row):
        """创建日志显示区域"""
        frame = ttk.LabelFrame(parent, text="处理日志", padding="10")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        parent.rowconfigure(row, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            frame,
            width=80,
            height=15,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def on_mode_changed(self):
        """模式变化时的回调"""
        # 清除当前显示的组件
        for widget in self.params_frame.winfo_children():
            widget.pack_forget()
        
        mode = self.mode_var.get()
        
        if mode == "current":
            # 当前时间模式不需要参数
            ttk.Label(
                self.params_frame,
                text="将所有照片的时间修改为执行时的当前时间",
                foreground="gray"
            ).pack(anchor=tk.W)
            
        elif mode == "specified":
            # 显示日期时间选择器
            self.datetime_picker.pack(anchor=tk.W)
            
        elif mode == "relative":
            # 显示相对时间输入
            ttk.Label(
                self.params_frame,
                text="在照片当前时间基础上增加或减少时间:",
                foreground="gray"
            ).pack(anchor=tk.W, pady=(0, 5))
            self.relative_input.pack(anchor=tk.W)
    
    def browse_directory(self):
        """浏览并选择目录"""
        directory = filedialog.askdirectory(
            title="选择照片目录",
            initialdir=self.directory_var.get() or Path.home()
        )
        
        if directory:
            self.directory_var.set(directory)
    
    def start_processing(self):
        """开始处理照片"""
        if self.processing:
            return
        
        # 验证目录
        directory = self.directory_var.get()
        if not directory:
            messagebox.showwarning("警告", "请选择目标目录")
            return
        
        if not Path(directory).exists():
            messagebox.showerror("错误", "目录不存在")
            return
        
        # 验证参数
        mode = self.mode_var.get()
        params = None
        
        if mode == "specified":
            dt = self.datetime_picker.get_datetime()
            if dt is None:
                messagebox.showerror("错误", "日期时间格式错误")
                return
            params = {'datetime': dt}
            
        elif mode == "relative":
            offset = self.relative_input.get_offset()
            params = offset
        
        # 开始处理
        self.processing = True
        self.process_btn.config(state='disabled')
        
        try:
            self.logger.info("=" * 60)
            self.logger.info(f"开始扫描目录: {directory}")
            
            # 扫描文件
            recursive = self.recursive_var.get()
            files = scan_directory(directory, recursive)
            
            if not files:
                self.logger.warning("未找到任何支持的图片文件")
                messagebox.showinfo("提示", "未找到任何支持的图片文件")
                return
            
            self.logger.info(f"找到 {len(files)} 个图片文件")
            
            # 确认开始处理
            if mode == "current":
                mode_desc = f"当前时间 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
            elif mode == "specified":
                mode_desc = f"指定时间 ({params['datetime'].strftime('%Y-%m-%d %H:%M:%S')})"
            else:
                offset = params
                mode_desc = f"时间偏移 ({offset['days']}天 {offset['hours']}小时 {offset['minutes']}分钟)"
            
            confirm = messagebox.askyesno(
                "确认",
                f"将修改 {len(files)} 个文件的时间为:\n{mode_desc}\n\n确定继续吗?"
            )
            
            if not confirm:
                self.logger.info("用户取消操作")
                return
            
            self.logger.info(f"修改模式: {mode_desc}")
            self.logger.info("开始处理...")
            
            # 处理照片
            def progress_callback(current, total, filepath, success, message):
                """进度回调"""
                filename = Path(filepath).name
                if success:
                    self.logger.success(f"[{current}/{total}] {filename}: {message}")
                else:
                    self.logger.error(f"[{current}/{total}] {filename}: {message}")
            
            result = process_photos(files, mode, params, progress_callback)
            
            # 显示结果
            self.logger.info("=" * 60)
            self.logger.info(f"处理完成!")
            self.logger.info(f"总计: {result['total']} | 成功: {result['success']} | 失败: {result['failed']}")
            
            if result['failed'] > 0:
                self.logger.warning(f"有 {result['failed']} 个文件处理失败，请查看上方日志")
            
            messagebox.showinfo(
                "完成",
                f"处理完成!\n\n总计: {result['total']}\n成功: {result['success']}\n失败: {result['failed']}"
            )
            
        except BatchProcessorError as e:
            self.logger.error(f"处理失败: {e}")
            messagebox.showerror("错误", str(e))
            
        except Exception as e:
            self.logger.error(f"未知错误: {e}")
            messagebox.showerror("错误", f"发生错误: {e}")
            
        finally:
            self.processing = False
            self.process_btn.config(state='normal')
    
    def clear_log(self):
        """清空日志"""
        self.logger.clear()
    
    def export_log(self):
        """导出日志到文件"""
        filepath = filedialog.asksaveasfilename(
            title="导出日志",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"photo_tool_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filepath:
            if self.logger.export_to_file(filepath):
                messagebox.showinfo("成功", "日志已导出")
            else:
                messagebox.showerror("错误", "导出失败")
