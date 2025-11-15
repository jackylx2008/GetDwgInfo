# DXF 提取器使用说明

## 概述

`dxf_extractor.py` 是一个用于从 DXF 文件中提取各种元素的工具。与 `dwg_extractor.py` 不同，DXF 提取器使用 `ezdxf` 库直接读取 DXF 文件，**不需要安装 AutoCAD**。

## 主要区别

| 特性         | dwg_extractor.py   | dxf_extractor.py  |
| ------------ | ------------------ | ----------------- |
| 文件格式     | DWG (二进制)       | DXF (文本/二进制) |
| 依赖库       | pyautocad, pywin32 | ezdxf             |
| 需要 AutoCAD | ✅ 是               | ❌ 否              |
| 平台限制     | Windows only       | 跨平台            |
| 速度         | 依赖 AutoCAD       | 较快              |
| 准确性       | 100% (官方 API)    | 非常高            |

## 安装依赖

```bash
pip install ezdxf>=1.0.0
```

或安装所有依赖：

```bash
pip install -r requirements.txt
```

## 快速开始

### 基本用法

```python
from dxf_extractor import DXFExtractor

# 创建提取器
extractor = DXFExtractor()

# 提取 DXF 文件
elements = extractor.extract_from_file("your_file.dxf")

# 查看结果
print(f"文本: {len(elements['texts'])} 个")
print(f"线条: {len(elements['lines'])} 个")
print(f"圆形: {len(elements['circles'])} 个")
print(f"矩形: {len(elements['rects'])} 个")

# 保存到 CSV
extractor.save_to_csv("output.csv")
```

### 自定义配置

```python
# 只提取文本和圆形
config = {
    "extract_text": True,
    "extract_lines": False,
    "extract_rects": False,
    "extract_circles": True,
}

elements = extractor.extract_from_file("file.dxf", config)
```

## 支持的元素类型

### 1. 文本 (TEXT, MTEXT)
```python
{
    'content': '文本内容',
    'x': 100.0,
    'y': 200.0,
    'z': 0.0,
    'height': 3.5,
    'rotation': 0.0,
    'color': 7,
    'layer': '0',
    'style': 'Standard'
}
```

### 2. 线条 (LINE)
```python
{
    'start_x': 0.0,
    'start_y': 0.0,
    'start_z': 0.0,
    'end_x': 100.0,
    'end_y': 100.0,
    'end_z': 0.0,
    'color': 7,
    'layer': '0',
    'linetype': 'CONTINUOUS',
    'lineweight': -1
}
```

### 3. 圆形 (CIRCLE)
```python
{
    'center_x': 50.0,
    'center_y': 50.0,
    'center_z': 0.0,
    'radius': 25.0,
    'color': 7,
    'layer': '0'
}
```

### 4. 矩形 (从 LWPOLYLINE/POLYLINE 识别)
```python
{
    'x': 0.0,
    'y': 0.0,
    'width': 100.0,
    'height': 50.0,
    'color': 7,
    'layer': '0'
}
```

### 5. 多段线 (LWPOLYLINE, POLYLINE)
```python
{
    'vertices': [(0,0,0), (10,0,0), (10,10,0), (0,10,0)],
    'is_closed': True,
    'color': 7,
    'layer': '0'
}
```

## 使用示例

### 示例 1: 批量处理 DXF 文件

```python
import os
from dxf_extractor import DXFExtractor

extractor = DXFExtractor()

for filename in os.listdir("input"):
    if filename.endswith('.dxf'):
        input_path = os.path.join("input", filename)
        output_path = os.path.join("output", filename.replace('.dxf', '.csv'))
        
        elements = extractor.extract_from_file(input_path)
        extractor.save_to_csv(output_path)
        
        print(f"✓ 处理完成: {filename}")
```

### 示例 2: 按图层过滤

```python
from dxf_extractor import DXFExtractor

extractor = DXFExtractor()
elements = extractor.extract_from_file("file.dxf")

# 获取特定图层的文本
layer_name = "文字图层"
texts_in_layer = [
    text for text in elements['texts']
    if text['layer'] == layer_name
]

print(f"图层 '{layer_name}' 中有 {len(texts_in_layer)} 个文本")
```

### 示例 3: 统计分析

```python
from dxf_extractor import DXFExtractor
from collections import Counter

extractor = DXFExtractor()
elements = extractor.extract_from_file("file.dxf")

# 统计各图层的元素数量
layer_counts = Counter()
for text in elements['texts']:
    layer_counts[text['layer']] += 1

print("各图层的文本分布:")
for layer, count in layer_counts.most_common(10):
    print(f"  {layer}: {count} 个")
```

### 示例 4: 几何分析

```python
from dxf_extractor import DXFExtractor

extractor = DXFExtractor()
elements = extractor.extract_from_file("file.dxf")

# 计算图纸边界
all_x = [text['x'] for text in elements['texts']]
all_y = [text['y'] for text in elements['texts']]

if all_x and all_y:
    print(f"X 范围: {min(all_x):.2f} 到 {max(all_x):.2f}")
    print(f"Y 范围: {min(all_y):.2f} 到 {max(all_y):.2f}")
```

## 测试

运行测试脚本：

```bash
# 测试 DXF 提取器
python test_dxf_extractor.py

# 查看使用示例
python example_dxf.py
```

## 与 DWG 提取器的选择

**使用 dxf_extractor.py 当:**
- ✅ 已有 DXF 文件
- ✅ 不想安装 AutoCAD
- ✅ 需要跨平台支持
- ✅ 需要更快的处理速度
- ✅ 批量处理大量文件

**使用 dwg_extractor.py 当:**
- ✅ 只有 DWG 文件（无 DXF）
- ✅ 已安装 AutoCAD
- ✅ 需要 100% 准确性
- ✅ 处理复杂的 AutoCAD 特性

## DWG 转 DXF

如果你有 DWG 文件但想使用 DXF 提取器，可以：

1. **使用 AutoCAD**:
   - 打开 DWG 文件
   - 文件 → 另存为 → 选择 DXF 格式

2. **使用在线转换工具**:
   - CloudConvert
   - Zamzar
   - AnyConv

3. **使用命令行工具**:
   - DWG TrueView (免费)
   - ODA File Converter (免费)

## 常见问题

### Q: DXF 和 DWG 有什么区别？
A: DWG 是 AutoCAD 的原生二进制格式，DXF 是文本格式（也有二进制版本）。DXF 更易于第三方工具读取。

### Q: 提取的数据准确吗？
A: 非常准确。ezdxf 是一个成熟的库，广泛用于 DXF 文件处理。

### Q: 支持所有版本的 DXF 吗？
A: ezdxf 支持 AutoCAD R12 到 R2018+ 的 DXF 格式。

### Q: 可以修改 DXF 文件吗？
A: 当前版本只支持读取。如需修改，可以使用 ezdxf 库的完整功能。

### Q: 处理大文件会很慢吗？
A: DXF 提取器比 DWG 提取器快，因为不依赖 AutoCAD。大文件（几MB）通常在几秒内完成。

## 性能参考

| 文件大小 | 实体数量       | 处理时间 |
| -------- | -------------- | -------- |
| < 1 MB   | < 10,000       | 1-3 秒   |
| 1-5 MB   | 10,000-50,000  | 3-10 秒  |
| 5-10 MB  | 50,000-100,000 | 10-30 秒 |
| > 10 MB  | > 100,000      | 30+ 秒   |

*实际性能取决于硬件配置和文件复杂度*

## API 参考

### DXFExtractor 类

#### 方法

**`extract_from_file(dxf_path, extract_config=None)`**
- 参数:
  - `dxf_path` (str): DXF 文件路径
  - `extract_config` (dict, 可选): 提取配置
- 返回: dict - 包含各类元素的字典

**`get_all_elements()`**
- 返回: list - 所有元素的扁平列表

**`save_to_csv(output_path)`**
- 参数:
  - `output_path` (str): 输出 CSV 文件路径
- 返回: None

## 许可证

MIT License

## 相关文件

- `dxf_extractor.py` - DXF 提取器主模块
- `test_dxf_extractor.py` - 测试脚本
- `example_dxf.py` - 使用示例
- `dwg_extractor.py` - DWG 提取器（需要 AutoCAD）
