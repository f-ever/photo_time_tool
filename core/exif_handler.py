"""
EXIF数据处理模块
负责读取和修改照片的EXIF元数据
"""
import piexif
from PIL import Image
from datetime import datetime
from pathlib import Path


class ExifHandlerError(Exception):
    """EXIF处理异常"""
    pass


def read_exif(filepath):
    """
    读取照片的EXIF数据
    
    Args:
        filepath: 照片文件路径
        
    Returns:
        dict: EXIF数据字典，如果无EXIF则返回空结构
        
    Raises:
        ExifHandlerError: 文件不存在或无法读取
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise ExifHandlerError(f"文件不存在: {filepath}")
    
    try:
        exif_dict = piexif.load(str(filepath))
        
        # 确保必要的IFD存在
        if '0th' not in exif_dict:
            exif_dict['0th'] = {}
        if 'Exif' not in exif_dict:
            exif_dict['Exif'] = {}
        if 'GPS' not in exif_dict:
            exif_dict['GPS'] = {}
        if '1st' not in exif_dict:
            exif_dict['1st'] = {}
            
        return exif_dict
        
    except (piexif.InvalidImageDataError, ValueError) as e:
        # 图片没有EXIF数据或数据损坏，创建新的EXIF结构
        return {
            '0th': {},
            'Exif': {},
            'GPS': {},
            '1st': {}
        }
    except Exception as e:
        raise ExifHandlerError(f"读取EXIF失败: {e}")


def write_exif(filepath, dt):
    """
    修改照片的EXIF时间戳
    
    修改以下三个时间标签：
    - DateTime (0th IFD): 文件修改时间
    - DateTimeOriginal (Exif IFD): 原始拍摄时间
    - DateTimeDigitized (Exif IFD): 数字化时间
    
    Args:
        filepath: 照片文件路径
        dt: datetime对象，目标时间
        
    Raises:
        ExifHandlerError: 写入失败
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise ExifHandlerError(f"文件不存在: {filepath}")
    
    try:
        # 读取现有EXIF数据
        exif_dict = read_exif(filepath)
        
        # 格式化时间字符串: YYYY:MM:DD HH:MM:SS
        time_str = dt.strftime("%Y:%m:%d %H:%M:%S")
        time_bytes = time_str.encode('ascii')
        
        # 修改时间标签
        exif_dict['0th'][piexif.ImageIFD.DateTime] = time_bytes
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = time_bytes
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = time_bytes
        
        # 生成EXIF字节数据
        exif_bytes = piexif.dump(exif_dict)
        
        # 直接插入EXIF数据，不改变图像本身
        # 这样可以避免图像重新编码导致的质量损失
        piexif.insert(exif_bytes, str(filepath))
        
    except Exception as e:
        raise ExifHandlerError(f"写入EXIF失败: {e}")


def get_exif_datetime(filepath):
    """
    获取照片的EXIF拍摄时间
    
    Args:
        filepath: 照片文件路径
        
    Returns:
        datetime对象，如果无法获取则返回None
    """
    try:
        exif_dict = read_exif(filepath)
        
        # 优先读取DateTimeOriginal
        if piexif.ExifIFD.DateTimeOriginal in exif_dict.get('Exif', {}):
            time_bytes = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
            time_str = time_bytes.decode('ascii')
            return datetime.strptime(time_str, "%Y:%m:%d %H:%M:%S")
        
        # 尝试DateTime
        if piexif.ImageIFD.DateTime in exif_dict.get('0th', {}):
            time_bytes = exif_dict['0th'][piexif.ImageIFD.DateTime]
            time_str = time_bytes.decode('ascii')
            return datetime.strptime(time_str, "%Y:%m:%d %H:%M:%S")
            
        return None
        
    except Exception:
        return None


def is_supported_format(filepath):
    """
    检查文件是否为支持的图片格式
    
    Args:
        filepath: 文件路径
        
    Returns:
        bool: 是否支持
    """
    supported_extensions = {'.jpg', '.jpeg', '.jpe', '.jfif', '.tiff', '.tif'}
    ext = Path(filepath).suffix.lower()
    return ext in supported_extensions
