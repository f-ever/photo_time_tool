"""
照片时间修改工具
主程序入口
"""
import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 尝试导入ttkbootstrap以获得现代化主题
try:
    import ttkbootstrap as ttk_bs
    USE_BOOTSTRAP = True
except ImportError:
    USE_BOOTSTRAP = False

from gui.main_window import MainWindow


def main():
    """主函数"""
    if USE_BOOTSTRAP:
        # 使用ttkbootstrap的现代主题
        root = ttk_bs.Window(themename="cosmo")
    else:
        # 使用标准tkinter
        root = tk.Tk()
        # 尝试使用更好看的ttk主题
        try:
            style = ttk.Style()
            available_themes = style.theme_names()
            if 'vista' in available_themes:
                style.theme_use('vista')
            elif 'clam' in available_themes:
                style.theme_use('clam')
        except:
            pass
    
    # 创建主窗口
    app = MainWindow(root)
    
    # 居中显示窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    main()
