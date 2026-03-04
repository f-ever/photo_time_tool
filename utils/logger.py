"""
日志系统
提供日志记录和显示功能
"""
from datetime import datetime
from pathlib import Path


class Logger:
    """
    日志记录器
    可以输出到GUI组件或文件
    """
    
    # 日志级别
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    SUCCESS = 'SUCCESS'
    
    def __init__(self, text_widget=None):
        """
        初始化日志记录器
        
        Args:
            text_widget: tkinter Text或ScrolledText组件，用于显示日志
        """
        self.text_widget = text_widget
        self.logs = []  # 存储所有日志
    
    def log(self, level, message):
        """
        记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # 存储到列表
        self.logs.append({
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'full': log_entry
        })
        
        # 输出到GUI
        if self.text_widget:
            self._write_to_widget(log_entry, level)
    
    def info(self, message):
        """记录INFO日志"""
        self.log(self.INFO, message)
    
    def warning(self, message):
        """记录WARNING日志"""
        self.log(self.WARNING, message)
    
    def error(self, message):
        """记录ERROR日志"""
        self.log(self.ERROR, message)
    
    def success(self, message):
        """记录SUCCESS日志"""
        self.log(self.SUCCESS, message)
    
    def _write_to_widget(self, text, level):
        """
        将日志写入GUI组件
        
        Args:
            text: 日志文本
            level: 日志级别
        """
        if not self.text_widget:
            return
        
        try:
            # 在文本框末尾插入
            self.text_widget.insert('end', text + '\n')
            
            # 根据日志级别设置颜色（如果支持标签）
            try:
                line_start = self.text_widget.index('end-2c linestart')
                line_end = self.text_widget.index('end-1c')
                
                if level == self.ERROR:
                    self.text_widget.tag_add('error', line_start, line_end)
                elif level == self.WARNING:
                    self.text_widget.tag_add('warning', line_start, line_end)
                elif level == self.SUCCESS:
                    self.text_widget.tag_add('success', line_start, line_end)
            except:
                pass  # 如果标签功能不可用，忽略
            
            # 自动滚动到底部
            self.text_widget.see('end')
            
            # 强制更新显示
            self.text_widget.update_idletasks()
            
        except Exception as e:
            # 如果写入失败，静默忽略
            pass
    
    def clear(self):
        """清空日志"""
        self.logs = []
        
        if self.text_widget:
            try:
                self.text_widget.delete('1.0', 'end')
            except:
                pass
    
    def export_to_file(self, filepath):
        """
        导出日志到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            filepath = Path(filepath)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("照片时间修改工具 - 日志导出\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                for log in self.logs:
                    f.write(log['full'] + '\n')
            
            return True
            
        except Exception as e:
            self.error(f"导出日志失败: {e}")
            return False
    
    def get_summary(self):
        """
        获取日志摘要统计
        
        Returns:
            dict: 统计信息
        """
        summary = {
            'total': len(self.logs),
            'info': 0,
            'warning': 0,
            'error': 0,
            'success': 0
        }
        
        for log in self.logs:
            level = log['level'].lower()
            if level in summary:
                summary[level] += 1
        
        return summary


def configure_text_widget_tags(text_widget):
    """
    配置文本组件的标签样式
    
    Args:
        text_widget: tkinter Text组件
    """
    try:
        # 错误日志 - 红色
        text_widget.tag_config('error', foreground='#dc3545')
        
        # 警告日志 - 橙色
        text_widget.tag_config('warning', foreground='#fd7e14')
        
        # 成功日志 - 绿色
        text_widget.tag_config('success', foreground='#28a745')
        
    except Exception:
        pass  # 如果配置失败，使用默认样式
