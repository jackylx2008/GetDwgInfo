# GetDwgInfo 快速开始指南

## 5分钟快速上手

### 前提条件
- ✅ Windows 系统
- ✅ 已安装 AutoCAD (2016-2020 任一版本)
- ✅ Python 3.7 或更高版本

### 第一步: 安装依赖

打开命令行,进入项目目录:
```bash
cd d:\CloudStation\Python\Project\GetDwgInfo
pip install -r requirements.txt
```

### 第二步: 验证 AutoCAD 连接

运行连接测试:
```bash
python test_connection.py
```

期望输出:
```
✓ 成功连接到 AutoCAD
✓ AutoCAD 版本: [你的版本]
✓ ProgID: [自动识别的 ProgID]
```

### 第三步: 提取你的第一个 DWG 文件

创建一个简单的脚本 `my_first_extract.py`:

```python
from dwg_extractor import DWGExtractor

# 创建提取器
extractor = DWGExtractor()

# 提取 DWG 文件
dwg_file = "你的文件路径.dwg"  # 修改为你的 DWG 文件路径
elements = extractor.extract_from_file(dwg_file)

# 查看结果
print(f"文本: {len(elements['texts'])} 个")
print(f"线条: {len(elements['lines'])} 个")
print(f"圆形: {len(elements['circles'])} 个")
print(f"矩形: {len(elements['rects'])} 个")

# 保存到 CSV
extractor.save_to_csv("output.csv")
print("✓ 已保存到 output.csv")
```

运行:
```bash
python my_first_extract.py
```

### 第四步: 查看提取的数据

用 Excel 或记事本打开 `output.csv`,查看提取的元素数据。

## 常见使用场景

### 场景 1: 只提取文本

```python
from dwg_extractor import DWGExtractor

extractor = DWGExtractor()

# 自定义配置 - 只提取文本
config = {
    "extract_text": True,
    "extract_lines": False,
    "extract_rects": False,
    "extract_circles": False
}

elements = extractor.extract_from_file("file.dwg", config)
texts = elements['texts']

# 打印所有文本内容
for text in texts:
    print(f"{text['content']} at ({text['x']}, {text['y']})")
```

### 场景 2: 批量处理多个文件

```python
from dwg_extractor import DWGExtractor
import os

extractor = DWGExtractor()

# DWG 文件目录
dwg_dir = "input"
output_dir = "output"

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 处理所有 DWG 文件
for filename in os.listdir(dwg_dir):
    if filename.endswith('.dwg'):
        dwg_path = os.path.join(dwg_dir, filename)
        output_path = os.path.join(
            output_dir, 
            filename.replace('.dwg', '_elements.csv')
        )
        
        print(f"处理: {filename}")
        elements = extractor.extract_from_file(dwg_path)
        extractor.save_to_csv(output_path)
        print(f"✓ 完成: {output_path}")
```

### 场景 3: 提取特定图层的元素

```python
from dwg_extractor import DWGExtractor

extractor = DWGExtractor()
elements = extractor.extract_from_file("file.dwg")

# 筛选特定图层的文本
target_layer = "文字图层"
texts_in_layer = [
    text for text in elements['texts'] 
    if text['layer'] == target_layer
]

print(f"图层 '{target_layer}' 中的文本: {len(texts_in_layer)} 个")
```

### 场景 4: 统计元素信息

```python
from dwg_extractor import DWGExtractor
from collections import Counter

extractor = DWGExtractor()
elements = extractor.extract_from_file("file.dwg")

# 统计文本按图层分布
text_layers = [text['layer'] for text in elements['texts']]
layer_counts = Counter(text_layers)

print("文本按图层分布:")
for layer, count in layer_counts.most_common():
    print(f"  {layer}: {count} 个")

# 统计文本内容
text_contents = [text['content'] for text in elements['texts']]
content_counts = Counter(text_contents)

print("\n最常见的文本:")
for content, count in content_counts.most_common(10):
    print(f"  '{content}': {count} 次")
```

## 配置选项

### 提取配置

```python
config = {
    "extract_text": True,      # 是否提取文本
    "extract_lines": True,     # 是否提取线条
    "extract_rects": True,     # 是否提取矩形
    "extract_circles": True,   # 是否提取圆形
}
```

### 元素数据结构

#### 文本元素
```python
{
    'content': '文本内容',
    'x': 123.45,           # X 坐标
    'y': 678.90,           # Y 坐标
    'z': 0.0,              # Z 坐标
    'height': 3.5,         # 文字高度
    'rotation': 0.0,       # 旋转角度
    'layer': '图层名',
    'color': 7,            # 颜色索引
    'style': '文字样式'
}
```

#### 线条元素
```python
{
    'start_x': 0.0,        # 起点 X
    'start_y': 0.0,        # 起点 Y
    'start_z': 0.0,        # 起点 Z
    'end_x': 100.0,        # 终点 X
    'end_y': 100.0,        # 终点 Y
    'end_z': 0.0,          # 终点 Z
    'layer': '图层名',
    'color': 7,
    'linetype': '线型',
    'lineweight': -1
}
```

#### 圆形元素
```python
{
    'center_x': 50.0,      # 圆心 X
    'center_y': 50.0,      # 圆心 Y
    'center_z': 0.0,       # 圆心 Z
    'radius': 25.0,        # 半径
    'layer': '图层名',
    'color': 7
}
```

#### 矩形元素
```python
{
    'x': 0.0,              # 左下角 X
    'y': 0.0,              # 左下角 Y
    'width': 100.0,        # 宽度
    'height': 50.0,        # 高度
    'layer': '图层名',
    'color': 7
}
```

## 故障排除

### 问题: 导入错误

**错误**: `ModuleNotFoundError: No module named 'pyautocad'`

**解决**:
```bash
pip install pyautocad pywin32
```

### 问题: AutoCAD 连接失败

**错误**: `无法找到或启动 AutoCAD`

**检查清单**:
1. ✅ AutoCAD 是否已安装?
2. ✅ AutoCAD 是否已激活(不是试用版过期)?
3. ✅ 运行 `test_connection.py` 查看详细错误
4. ✅ 尝试手动打开 AutoCAD

### 问题: 提取元素为空

**可能原因**:
1. DWG 文件中没有实体
2. 实体在图纸空间而不是模型空间
3. 实体类型不在支持列表中

**解决**:
1. 用 AutoCAD 打开文件检查
2. 确保实体在模型空间
3. 查看日志了解跳过的实体类型

### 问题: 提取速度慢

**优化建议**:
1. 只提取需要的元素类型
2. 关闭不需要的图层(在 AutoCAD 中)
3. 对于超大文件,考虑分批处理

## 获取帮助

### 运行诊断工具
```bash
python diagnose_autocad.py
```

### 查看完整测试
```bash
python test_dwg_extractor.py
```

### 查看日志
日志默认输出到控制台,可以重定向到文件:
```bash
python my_script.py > output.log 2>&1
```

## 下一步

- 📖 阅读 [README.md](README.md) 了解详细文档
- 📝 查看 [MIGRATION.md](MIGRATION.md) 了解从 ezdxf 迁移的详情
- 🔍 参考 [example.py](example.py) 查看更多示例
- 📋 阅读 [UPDATE_SUMMARY.md](UPDATE_SUMMARY.md) 了解最新更新

## 技术支持

如果遇到问题:
1. 检查 [故障排除](#故障排除) 部分
2. 运行 `diagnose_autocad.py` 获取诊断信息
3. 查看日志输出了解详细错误

祝使用愉快! 🎉
