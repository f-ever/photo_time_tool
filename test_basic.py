"""
简单测试脚本
测试核心功能是否正常工作
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 测试导入
print("测试导入模块...")
try:
    from core.exif_handler import read_exif, write_exif, is_supported_format
    from core.file_handler import set_file_times, get_file_times
    from core.batch_processor import scan_directory, process_photos
    print("✓ 所有核心模块导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试扫描目录
print("\n测试扫描目录...")
try:
    test_dir = project_root / "test_photos"
    if test_dir.exists():
        files = scan_directory(test_dir, recursive=True)
        print(f"✓ 找到 {len(files)} 个图片文件")
        for f in files:
            print(f"  - {f.name}")
    else:
        print("⚠ test_photos目录不存在")
except Exception as e:
    print(f"✗ 扫描失败: {e}")

# 测试文件格式识别
print("\n测试格式识别...")
test_files = [
    "test.jpg",
    "test.jpeg",
    "test.png",
    "test.tiff",
    "test.txt"
]
for f in test_files:
    supported = is_supported_format(f)
    symbol = "✓" if supported else "✗"
    print(f"  {symbol} {f}: {supported}")

# 测试EXIF读取（如果有测试文件）
print("\n测试EXIF读取...")
try:
    test_dir = project_root / "test_photos"
    if test_dir.exists():
        test_files = list(test_dir.glob("*.jpg"))
        if test_files:
            test_file = test_files[0]
            print(f"读取文件: {test_file.name}")
            exif_dict = read_exif(test_file)
            print(f"✓ EXIF读取成功，包含 {len(exif_dict)} 个IFD")
            
            # 读取文件时间
            file_times = get_file_times(test_file)
            print(f"✓ 文件时间: {file_times['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("⚠ 没有找到测试JPEG文件")
except Exception as e:
    print(f"✗ EXIF读取失败: {e}")

print("\n所有基础测试完成!")
print("\n提示: 运行 'python main.py' 启动GUI程序")
