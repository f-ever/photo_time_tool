"""
自定义GUI组件
包括日期时间选择器和相对时间输入框
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class DateTimePicker(ttk.Frame):
    """
    日期时间选择器组件
    提供图形化的日期和时间选择功能
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.create_widgets()
        
        # 设置默认值为当前时间
        now = datetime.now()
        self.set_datetime(now)
    
    def create_widgets(self):
        """创建子组件"""
        # 日期选择部分 - 使用Spinbox实现年月日选择
        date_frame = ttk.Frame(self)
        date_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(date_frame, text="日期:").pack(side=tk.LEFT, padx=(0, 5))
        
        # 年
        self.year_var = tk.StringVar()
        year_spinbox = ttk.Spinbox(
            date_frame,
            from_=2000,
            to=2100,
            width=5,
            textvariable=self.year_var
        )
        year_spinbox.pack(side=tk.LEFT)
        ttk.Label(date_frame, text="年").pack(side=tk.LEFT, padx=(2, 5))
        
        # 月
        self.month_var = tk.StringVar()
        month_spinbox = ttk.Spinbox(
            date_frame,
            from_=1,
            to=12,
            width=3,
            textvariable=self.month_var,
            format='%02.0f'
        )
        month_spinbox.pack(side=tk.LEFT)
        ttk.Label(date_frame, text="月").pack(side=tk.LEFT, padx=(2, 5))
        
        # 日
        self.day_var = tk.StringVar()
        day_spinbox = ttk.Spinbox(
            date_frame,
            from_=1,
            to=31,
            width=3,
            textvariable=self.day_var,
            format='%02.0f'
        )
        day_spinbox.pack(side=tk.LEFT)
        ttk.Label(date_frame, text="日").pack(side=tk.LEFT, padx=(2, 0))
        
        # 时间选择部分
        time_frame = ttk.Frame(self)
        time_frame.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text="时间:").pack(side=tk.LEFT, padx=(0, 5))
        
        # 小时
        self.hour_var = tk.StringVar()
        hour_spinbox = ttk.Spinbox(
            time_frame,
            from_=0,
            to=23,
            width=3,
            textvariable=self.hour_var,
            format='%02.0f'
        )
        hour_spinbox.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        
        # 分钟
        self.minute_var = tk.StringVar()
        minute_spinbox = ttk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            width=3,
            textvariable=self.minute_var,
            format='%02.0f'
        )
        minute_spinbox.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        
        # 秒
        self.second_var = tk.StringVar()
        second_spinbox = ttk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            width=3,
            textvariable=self.second_var,
            format='%02.0f'
        )
        second_spinbox.pack(side=tk.LEFT)
    
    def get_datetime(self):
        """
        获取选择的日期时间
        
        Returns:
            datetime对象，如果解析失败则返回None
        """
        try:
            # 获取日期
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            
            # 获取时间
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            second = int(self.second_var.get())
            
            return datetime(year, month, day, hour, minute, second)
            
        except Exception as e:
            return None
    
    def set_datetime(self, dt):
        """
        设置日期时间
        
        Args:
            dt: datetime对象
        """
        try:
            # 设置日期
            self.year_var.set(str(dt.year))
            self.month_var.set(f'{dt.month:02d}')
            self.day_var.set(f'{dt.day:02d}')
            
            # 设置时间
            self.hour_var.set(f'{dt.hour:02d}')
            self.minute_var.set(f'{dt.minute:02d}')
            self.second_var.set(f'{dt.second:02d}')
            
        except Exception as e:
            pass


class RelativeTimeInput(ttk.Frame):
    """
    相对时间输入组件
    允许用户输入时间偏移量（天、小时、分钟）
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建子组件"""
        # 天数
        days_frame = ttk.Frame(self)
        days_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.days_var = tk.IntVar(value=0)
        ttk.Spinbox(
            days_frame,
            from_=-365,
            to=365,
            width=5,
            textvariable=self.days_var
        ).pack(side=tk.LEFT)
        ttk.Label(days_frame, text="天").pack(side=tk.LEFT, padx=(2, 0))
        
        # 小时
        hours_frame = ttk.Frame(self)
        hours_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.hours_var = tk.IntVar(value=0)
        ttk.Spinbox(
            hours_frame,
            from_=-24,
            to=24,
            width=5,
            textvariable=self.hours_var
        ).pack(side=tk.LEFT)
        ttk.Label(hours_frame, text="小时").pack(side=tk.LEFT, padx=(2, 0))
        
        # 分钟
        minutes_frame = ttk.Frame(self)
        minutes_frame.pack(side=tk.LEFT)
        
        self.minutes_var = tk.IntVar(value=0)
        ttk.Spinbox(
            minutes_frame,
            from_=-60,
            to=60,
            width=5,
            textvariable=self.minutes_var
        ).pack(side=tk.LEFT)
        ttk.Label(minutes_frame, text="分钟").pack(side=tk.LEFT, padx=(2, 0))
    
    def get_offset(self):
        """
        获取时间偏移量
        
        Returns:
            dict: 包含days, hours, minutes的字典
        """
        return {
            'days': self.days_var.get(),
            'hours': self.hours_var.get(),
            'minutes': self.minutes_var.get(),
            'seconds': 0
        }
    
    def set_offset(self, days=0, hours=0, minutes=0):
        """
        设置时间偏移量
        
        Args:
            days: 天数
            hours: 小时数
            minutes: 分钟数
        """
        self.days_var.set(days)
        self.hours_var.set(hours)
        self.minutes_var.set(minutes)
    
    def reset(self):
        """重置为0"""
        self.set_offset(0, 0, 0)
