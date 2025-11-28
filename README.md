# GetDwgInfo

一个强大的 DWG 元素提取与关联分析工具，用于从 DWG 文件中提取特定元素，保存到数据库，并分析元素之间的关联性。

## 项目简介

GetDwgInfo 是一个专业的 DWG 数据提取和分析工具，能够：

- 从 DWG 文件中精确提取文本、线条、矩形、圆形等元素
- 获取每个元素的详细特征（坐标、尺寸、颜色、图层等）
- 将提取的数据保存为结构化的 CSV 数据库
- 交叉分析元素之间的空间关系、颜色关联和图层关联
- 生成详细的关联性分析报告

## 功能特性

### 1. 元素提取

- **文本元素**: 提取文本内容、坐标、字高、旋转角度、颜色、图层、样式等
- **线条元素**: 提取起点、终点坐标、颜色、图层、线型、线宽等
- **矩形元素**: 识别闭合多段线，提取位置、宽度、高度、颜色、图层等
- **圆形元素**: 提取圆心坐标、半径、颜色、图层等
- **多段线**: 支持任意多段线的顶点提取

### TODO: 2. 关联分析

- **包含关系**: 分析文本是否包含在矩形内
- **邻近关系**: 计算文本与线条的距离
- **相交关系**: 检测线条与矩形的相交情况
- **颜色关联**: 识别相同颜色的元素组
- **图层关联**: 识别相同图层的元素组
- **对齐关系**: 检测元素的水平和垂直对齐

### 3. 数据管理

- CSV 格式存储，易于在 Excel 中查看和处理
- 自动类型转换，保持数据类型一致性
- 支持数据的重新加载和分析

## 系统要求

**重要**: 本工具使用 pyautocad 通过 COM 接口与 AutoCAD 交互，因此需要：

1. **Windows 操作系统**（COM 接口仅在 Windows 上可用）
2. **已安装 AutoCAD**（任意版本，如 AutoCAD 2018/2019/2020/2021 等）
3. **Python 3.7+**

## 安装依赖

```bash
pip install -r requirements.txt
```

**依赖说明**:

- `pyautocad`: AutoCAD COM 接口库
- `pywin32`: Windows COM 支持
- `PyYAML`: 配置文件解析

**测试连接**:

```bash
# 安装依赖后，测试是否能连接到 AutoCAD
python test_connection.py
```

如果测试通过，说明环境配置正确，可以正常使用本工具。

## 使用方法

### 1. 命令行批量处理 (推荐)

项目提供了直接可运行的脚本，用于批量处理 `input` 目录下的文件。

#### DXF 文件处理 (无需 AutoCAD)

将 `.dxf` 文件放入 `input/` 目录，然后运行：

```bash
# 批量处理 input 目录下的所有 .dxf 文件
python dxf_extractor.py
```

脚本会自动：

1. 扫描 `input/` 目录下的所有 `.dxf` 文件
2. 提取文本、线条、矩形、圆形等元素
3. 在 `output/` 目录生成对应的 CSV 文件（如 `test_elements.csv`）

### 2. Python 代码调用

你也可以在自己的 Python 脚本中导入使用。

#### DXF 提取 (dxf_extractor)

```python
from dxf_extractor import DXFExtractor

# 1. 初始化并加载文件
extractor = DXFExtractor("input/test.dxf")

# 2. 执行提取
extractor.extract()

# 3. 获取数据或导出
# 方式 A: 获取字典列表
elements = extractor.get_all_elements()
print(f"提取了 {len(elements)} 个元素")

# 方式 B: 导出 CSV
extractor.save_to_csv("output/test_elements.csv")
```

#### DWG 提取 (dwg_extractor)

> **注意**: 需要安装 AutoCAD 并运行在 Windows 环境下。

```python
from dwg_extractor import DWGExtractor
import os

# 1. 初始化
extractor = DWGExtractor()

# 2. 提取文件 (需提供绝对路径)
dwg_path = os.path.abspath("input/test.dwg")
extractor.extract_from_file(dwg_path)

# 3. 导出 CSV
extractor.save_to_csv("output/test_dwg_elements.csv")
```

## 项目结构

```text
GetDwgInfo/
├── config.yaml             # 配置文件
├── logging_config.py       # 日志配置模块
├── dwg_extractor.py        # DWG 元素提取模块 (依赖 AutoCAD)
├── dxf_extractor.py        # DXF 元素提取模块 (独立，无依赖)
├── convert_dwg_to_dxf.py   # DWG 转 DXF 工具
├── diagnose_autocad.py     # AutoCAD 环境诊断工具
├── test_dwg_extractor.py   # DWG 提取测试脚本
├── test_dxf_extractor.py   # DXF 提取测试脚本
├── requirements.txt        # 依赖包列表
├── README.md               # 项目说明文档
├── CHANGES.md              # 变更日志
├── input/                  # 输入文件目录
│   └── test.dwg
├── output/                 # 输出文件目录
│   └── test_elements.csv
└── logs/                   # 日志文件目录
```

## 更新日志

### 2025-11-15 更新

#### 新增功能

1. **DXF 提取器 (`dxf_extractor.py`)**
   - ✅ 完全独立的 DXF 文件提取模块
   - ✅ 使用 ezdxf 库，无需 AutoCAD
   - ✅ 支持跨平台（Windows/Linux/macOS）
   - ✅ 处理速度更快，资源占用更低
   - ✅ API 与 DWG 提取器完全兼容

2. **双提取器架构**
   - `dwg_extractor.py`: DWG 文件提取（需要 AutoCAD）
   - `dxf_extractor.py`: DXF 文件提取（不需要 AutoCAD）
   - 两者功能完全相同，API 一致

#### 技术改进

1. **COM 对象安全访问**
   - 实现带重试机制的属性访问
   - 解决"被呼叫方拒绝接收呼叫"错误
   - 提高 DWG 提取稳定性

2. **依赖更新**
   - 新增: `ezdxf>=1.0.0`
   - 保留: `pyautocad`, `pywin32`, `PyYAML>=6.0`

#### 使用建议

**推荐工作流**:

1. 如有 DWG 文件，转换为 DXF（使用免费工具）
2. 使用 `dxf_extractor.py` 提取元素（更快、免费、跨平台）
3. 如必须使用 DWG，则用 `dwg_extractor.py`（需要 AutoCAD）

**快速开始**:

```python
# DXF 提取（推荐 - 不需要 AutoCAD）
from dxf_extractor import DXFExtractor

# 1. 构造时直接传入 DXF 路径
extractor = DXFExtractor("input/file.dxf")

# 2. 提取元素
extractor.extract()

# 3. 接口一：获取扁平的 List[Dict]
elements = extractor.get_all_elements()
print(f"共提取 {len(elements)} 个元素")

# 4. 接口二：直接导出到 CSV
extractor.save_to_csv("output/file_elements.csv")
# 如只导出部分类型：
# extractor.save_to_csv("output/file_text_lines.csv", types=["text", "line"])
```

## 开发者

- 项目名称: GetDwgInfo
- 许可证: MIT License
- 最后更新: 2025-11-15

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
