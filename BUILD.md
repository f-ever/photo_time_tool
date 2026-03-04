# 打包说明

本文档说明如何将照片时间修改工具打包为Windows可执行文件。

## 准备工作

1. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

2. **测试源码运行**

   ```bash
   python main.py
   ```

   确保程序可以正常运行。

3. **重要提示**

   如果在运行PyInstaller时提示命令找不到，请使用以下方式运行：

   ```bash
   # 使用Python模块方式（推荐）
   python -m PyInstaller

   # 或者将Scripts目录添加到PATH
   # 通常位于: C:\Users\你的用户名\AppData\Roaming\Python\Python3XX\Scripts
   ```

## 打包步骤

### 方法1: 使用spec文件打包（推荐）

```bash
python -m PyInstaller PhotoTimeTool.spec
```

> **注意**: 如果提示 `pyinstaller` 命令找不到，请使用 `python -m PyInstaller` 代替 `pyinstaller`

打包完成后，可执行文件位于 `dist/PhotoTimeTool.exe`

### 方法2: 使用命令行参数打包

```bash
python -m PyInstaller --name PhotoTimeTool --onefile --windowed --clean main.py
```

参数说明:

- `--name PhotoTimeTool`: 指定输出文件名
- `--onefile`: 打包为单个exe文件
- `--windowed`: 不显示控制台窗口（GUI应用）
- `--clean`: 清理临时文件

### 方法3: 生成新的spec文件

如果需要重新生成spec配置:

```bash
python -m PyInstaller --name PhotoTimeTool --onefile --windowed main.py
```

然后编辑生成的 `PhotoTimeTool.spec` 文件，添加必要的配置。

## 打包优化

### 减小体积

在spec文件的 `excludes` 列表中添加不需要的大型库:

```python
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'pytest',
    'IPython'
]
```

### 使用UPX压缩

确保spec文件中 `upx=True`:

```python
exe = EXE(
    ...
    upx=True,
    ...
)
```

如果没有UPX，可以从这里下载: <https://upx.github.io/>

## 常见问题

### 1. pywin32打包问题

如果遇到pywin32相关错误，确保在spec文件的 `hiddenimports` 中包含:

```python
hiddenimports=[
    'win32file',
    'win32con',
    'win32api',
    'win32timezone',  # 重要：修改文件时间需要
    'pywintypes'
]
```

**常见错误**:

- `No module named 'win32timezone'`: 需要在hiddenimports中添加 `'win32timezone'`
- `No module named 'pywintypes'`: 需要添加 `'pywintypes'`

### 2. 杀毒软件误报

打包后的exe可能被杀毒软件误报为病毒。解决方法:

- 使用 `--clean` 参数重新打包
- 添加exe到杀毒软件白名单
- 使用代码签名证书签名（需要付费证书）

### 3. 启动慢

单文件模式（--onefile）启动时需要解压，会比较慢。如果需要更快启动，可以使用目录模式:

```bash
python -m PyInstaller --name PhotoTimeTool --windowed main.py
```

这样会生成一个文件夹，包含exe和依赖文件。

## 测试打包结果

1. 将生成的 `PhotoTimeTool.exe` 复制到没有Python环境的Windows机器
2. 双击运行，测试所有功能
3. 特别测试EXIF修改和文件时间修改功能

## 预期打包体积

- 基础版本: 约 20-25 MB
- 使用UPX压缩后: 约 15-20 MB

## 分发

打包完成后，可以直接分发 `dist/PhotoTimeTool.exe` 文件给用户使用，无需安装Python环境。
