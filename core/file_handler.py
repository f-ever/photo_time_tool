"""
Windows文件系统时间戳处理模块
负责修改文件的创建时间、修改时间和访问时间
"""
import os
import stat
from pathlib import Path
from datetime import datetime

# Windows特定模块
try:
    import win32file
    import win32con
    import pywintypes
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False


class FileHandlerError(Exception):
    """文件处理异常"""
    pass


def make_writable(filepath):
    """
    移除文件的只读属性，使其可写
    
    Args:
        filepath: 文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            return False
            
        # 获取当前权限
        current_permissions = os.stat(filepath).st_mode
        
        # 添加写权限
        os.chmod(filepath, current_permissions | stat.S_IWRITE | stat.S_IREAD)
        return True
        
    except (PermissionError, OSError) as e:
        return False


def set_file_times(filepath, dt):
    """
    修改文件的创建时间、修改时间和访问时间
    
    在Windows上使用win32file API修改真正的创建时间
    如果pywin32不可用，则回退到os.utime（无法修改创建时间）
    
    Args:
        filepath: 文件路径
        dt: datetime对象，目标时间
        
    Raises:
        FileHandlerError: 修改失败
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileHandlerError(f"文件不存在: {filepath}")
    
    # 尝试移除只读属性
    make_writable(filepath)
    
    try:
        if HAS_PYWIN32:
            # 使用pywin32修改Windows文件时间（包括创建时间）
            _set_file_times_win32(filepath, dt)
        else:
            # 回退方案：使用os.utime（仅修改访问和修改时间）
            _set_file_times_fallback(filepath, dt)
            
    except Exception as e:
        raise FileHandlerError(f"修改文件时间失败: {e}")


def _set_file_times_win32(filepath, dt):
    """
    使用win32file API修改文件时间（Windows）
    
    Args:
        filepath: 文件路径
        dt: datetime对象
    """
    # 打开文件句柄
    handle = win32file.CreateFile(
        str(filepath),
        win32con.GENERIC_WRITE,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL,
        None
    )
    
    try:
        # 转换为Windows时间格式
        wintime = pywintypes.Time(dt)
        
        # 设置文件时间：创建时间、访问时间、修改时间
        win32file.SetFileTime(handle, wintime, wintime, wintime)
        
    finally:
        handle.close()


def _set_file_times_fallback(filepath, dt):
    """
    使用os.utime修改文件时间（跨平台）
    
    注意：在Windows上无法修改创建时间
    
    Args:
        filepath: 文件路径
        dt: datetime对象
    """
    import time
    
    # 转换为时间戳
    timestamp = time.mktime(dt.timetuple())
    
    # 修改访问时间和修改时间
    os.utime(filepath, (timestamp, timestamp))


def get_file_times(filepath):
    """
    获取文件的时间信息
    
    Args:
        filepath: 文件路径
        
    Returns:
        dict: 包含ctime, mtime, atime的字典
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileHandlerError(f"文件不存在: {filepath}")
    
    stat_info = os.stat(filepath)
    
    return {
        'created': datetime.fromtimestamp(stat_info.st_ctime),
        'modified': datetime.fromtimestamp(stat_info.st_mtime),
        'accessed': datetime.fromtimestamp(stat_info.st_atime)
    }


def check_write_permission(filepath):
    """
    检查文件是否可写
    
    Args:
        filepath: 文件路径
        
    Returns:
        bool: 是否可写
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return False
    
    return os.access(filepath, os.W_OK)
