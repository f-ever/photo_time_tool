"""
批量处理引擎
负责扫描目录、计算目标时间、批量处理照片
"""
from pathlib import Path
from datetime import datetime, timedelta
from core.exif_handler import write_exif, is_supported_format, ExifHandlerError
from core.file_handler import set_file_times, FileHandlerError


class BatchProcessorError(Exception):
    """批量处理异常"""
    pass


def scan_directory(dir_path, recursive=True):
    """
    扫描目录，查找所有支持的图片文件
    
    Args:
        dir_path: 目录路径
        recursive: 是否递归扫描子目录
        
    Returns:
        list: 图片文件路径列表
        
    Raises:
        BatchProcessorError: 目录不存在或无法访问
    """
    dir_path = Path(dir_path)
    
    if not dir_path.exists():
        raise BatchProcessorError(f"目录不存在: {dir_path}")
    
    if not dir_path.is_dir():
        raise BatchProcessorError(f"路径不是目录: {dir_path}")
    
    image_files = []
    
    try:
        if recursive:
            # 递归扫描所有子目录
            for file_path in dir_path.rglob('*'):
                if file_path.is_file() and is_supported_format(file_path):
                    image_files.append(file_path)
        else:
            # 仅扫描当前目录
            for file_path in dir_path.glob('*'):
                if file_path.is_file() and is_supported_format(file_path):
                    image_files.append(file_path)
                    
    except PermissionError as e:
        raise BatchProcessorError(f"无权限访问目录: {e}")
    
    return sorted(image_files)


def calculate_target_time(mode, params=None):
    """
    根据模式和参数计算目标时间
    
    Args:
        mode: 修改模式
            - 'current': 当前时间
            - 'specified': 指定时间（需要params['datetime']）
            - 'relative': 相对时间（需要params['days']和params['hours']）
        params: 参数字典
        
    Returns:
        datetime: 目标时间
        
    Raises:
        BatchProcessorError: 参数错误
    """
    if mode == 'current':
        return datetime.now()
    
    elif mode == 'specified':
        if not params or 'datetime' not in params:
            raise BatchProcessorError("指定时间模式需要datetime参数")
        
        target_dt = params['datetime']
        if not isinstance(target_dt, datetime):
            raise BatchProcessorError("datetime参数必须是datetime对象")
        
        return target_dt
    
    elif mode == 'relative':
        if not params:
            raise BatchProcessorError("相对时间模式需要参数")
        
        days = params.get('days', 0)
        hours = params.get('hours', 0)
        minutes = params.get('minutes', 0)
        seconds = params.get('seconds', 0)
        
        # 可以基于当前时间或文件时间进行调整
        base_time = params.get('base_time', datetime.now())
        
        delta = timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )
        
        return base_time + delta
    
    else:
        raise BatchProcessorError(f"未知的模式: {mode}")


def process_single_photo(filepath, target_time, modify_exif=True, modify_file_time=True):
    """
    处理单张照片
    
    Args:
        filepath: 照片路径
        target_time: 目标时间
        modify_exif: 是否修改EXIF数据
        modify_file_time: 是否修改文件时间
        
    Returns:
        tuple: (success: bool, message: str)
    """
    errors = []
    
    # 修改EXIF时间
    if modify_exif:
        try:
            write_exif(filepath, target_time)
        except ExifHandlerError as e:
            errors.append(f"EXIF修改失败: {e}")
    
    # 修改文件系统时间
    if modify_file_time:
        try:
            set_file_times(filepath, target_time)
        except FileHandlerError as e:
            errors.append(f"文件时间修改失败: {e}")
    
    if errors:
        return False, "; ".join(errors)
    else:
        return True, "成功"


def process_photos(file_list, mode, params=None, progress_callback=None):
    """
    批量处理照片
    
    Args:
        file_list: 文件路径列表
        mode: 修改模式（'current', 'specified', 'relative'）
        params: 模式参数
        progress_callback: 进度回调函数 callback(current, total, filepath, success, message)
        
    Returns:
        dict: 处理结果统计
            {
                'total': 总数,
                'success': 成功数,
                'failed': 失败数,
                'errors': [(filepath, error_msg), ...]
            }
    """
    total = len(file_list)
    success_count = 0
    failed_count = 0
    errors = []
    
    # 对于非相对时间模式，计算一次目标时间
    if mode != 'relative':
        try:
            target_time = calculate_target_time(mode, params)
        except BatchProcessorError as e:
            return {
                'total': total,
                'success': 0,
                'failed': total,
                'errors': [(None, f"计算目标时间失败: {e}")]
            }
    
    # 处理每个文件
    for i, filepath in enumerate(file_list, 1):
        try:
            # 相对时间模式需要为每个文件单独计算
            if mode == 'relative':
                # 可以基于文件当前时间进行偏移
                from core.exif_handler import get_exif_datetime
                from core.file_handler import get_file_times
                
                # 尝试从EXIF获取基准时间
                base_time = get_exif_datetime(filepath)
                if base_time is None:
                    # 如果没有EXIF时间，使用文件修改时间
                    file_times = get_file_times(filepath)
                    base_time = file_times['modified']
                
                if params:
                    params['base_time'] = base_time
                
                target_time = calculate_target_time(mode, params)
            
            # 处理照片
            success, message = process_single_photo(filepath, target_time)
            
            if success:
                success_count += 1
            else:
                failed_count += 1
                errors.append((filepath, message))
            
            # 调用进度回调
            if progress_callback:
                progress_callback(i, total, filepath, success, message)
                
        except Exception as e:
            failed_count += 1
            error_msg = f"处理异常: {e}"
            errors.append((filepath, error_msg))
            
            if progress_callback:
                progress_callback(i, total, filepath, False, error_msg)
    
    return {
        'total': total,
        'success': success_count,
        'failed': failed_count,
        'errors': errors
    }
