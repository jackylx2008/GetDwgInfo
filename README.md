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

### 2. 关联分析
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

### 基本用法

```bash
# 提取 DWG 文件中的所有元素并进行分析
python main.py input/test.dwg

# 指定配置文件
python main.py input/test.dwg -c config.yaml

# 自定义输出文件名前缀
python main.py input/test.dwg -o my_project
```

**注意**: 
- 首次运行时，程序会自动启动 AutoCAD（如果未运行）
- AutoCAD 会打开指定的 DWG 文件，提取完成后自动关闭
- 提取过程中不会修改原文件

### 高级选项

```bash
# 只提取文本元素
python main.py input/test.dwg --text-only

# 只提取线条元素
python main.py input/test.dwg --lines-only

# 不进行关联分析
python main.py input/test.dwg --no-analysis
```

## 配置说明

编辑 `config.yaml` 文件来自定义工具行为：

```yaml
# 日志配置
log_level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
log_file: ./logs/app.log

# DWG 解析配置
dwg:
  extract_text: true
  extract_lines: true
  extract_rects: true
  extract_circles: true

# 分析配置
analysis:
  max_distance: 100.0  # 空间关系最大距离
  alignment_tolerance: 5.0  # 对齐容差

# 路径配置
paths:
  input_dir: ./input
  output_dir: ./output
```

## 输出文件

程序会在 `output` 目录生成以下文件：

1. **元素数据文件** (`*_elements.csv`): 包含所有提取的元素及其属性
2. **关联关系文件** (`*_relationships.csv`): 包含元素之间的关联关系

### 元素数据示例

| type | content | x   | y   | height | color | layer |
| ---- | ------- | --- | --- | ------ | ----- | ----- |
| TEXT | 标题    | 100 | 200 | 10     | 7     | 0     |
| LINE |         | 50  | 50  |        | 1     | 0     |

### 关联关系示例

| type        | source_type | target_type | description  | distance |
| ----------- | ----------- | ----------- | ------------ | -------- |
| PROXIMITY   | TEXT        | LINE        | 文本靠近线条 | 15.5     |
| COLOR_MATCH | TEXT        | TEXT        | 相同颜色     |          |

## 项目结构

```
GetDwgInfo/
├── main.py                 # 主程序入口
├── dwg_extractor.py        # DWG 元素提取模块
├── database.py             # CSV 数据库管理模块
├── analyzer.py             # 元素关联分析模块
├── logging_config.py       # 日志配置模块
├── config.yaml             # 配置文件
├── requirements.txt        # 依赖包列表
├── README.md              # 项目说明文档
├── input/                 # 输入文件目录
│   └── test.dwg
├── output/                # 输出文件目录
│   └── test_elements.csv
└── logs/                  # 日志文件目录
```

## 技术栈

- **Python 3.7+**
- **pyautocad**: 通过 COM 接口与 AutoCAD 交互
- **pywin32**: Windows COM 支持
- **PyYAML**: 配置文件解析
- **标准库**: logging, csv, argparse, dataclasses

## 注意事项

1. **AutoCAD 必须安装**: 程序运行时会自动启动 AutoCAD（如果未运行）
2. **文件自动关闭**: 提取完成后会自动关闭打开的 DWG 文件，不会保存任何修改
3. **性能**: 使用 COM 接口比直接解析文件慢，但能获取更准确的 AutoCAD 原生数据
4. **兼容性**: 支持所有 AutoCAD 能打开的 DWG 文件版本

## 更新日志

### 2025-11-15 更新

**重大更新**: 新增 DXF 文件提取支持，不再依赖 AutoCAD！

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

3. **测试和文档**
   - ✅ `test_dxf_extractor.py`: DXF 提取器测试套件
   - ✅ `example_dxf.py`: DXF 使用示例
   - ✅ `DXF_EXTRACTOR_README.md`: DXF 详细文档
   - ✅ `DWG_vs_DXF_GUIDE.md`: 选择指南

4. **CSV 保存功能**
   - ✅ 为 DWG 提取器添加 `save_to_csv()` 方法
   - ✅ 统一的 CSV 导出格式
   - ✅ 自动创建输出目录

#### 测试结果

**DWG 提取器测试** (input/test.dwg):
- 文本: 742 个 ✅
- 线条: 488 个 ✅
- 矩形: 109 个 ✅
- 圆形: 70 个 ✅
- 总计: 1,409 个元素

**DXF 提取器测试** (input/test.dxf):
- 文本: 474 个 ✅
- 线条: 1,245 个 ✅
- 矩形: 120 个 ✅
- 圆形: 70 个 ✅
- 总计: 1,909 个元素

#### 技术改进

1. **COM 对象安全访问**
   - 实现带重试机制的属性访问
   - 解决"被呼叫方拒绝接收呼叫"错误
   - 提高 DWG 提取稳定性

2. **依赖更新**
   - 新增: `ezdxf>=1.0.0`
   - 保留: `pyautocad`, `pywin32`, `PyYAML>=6.0`

3. **文档完善**
   - 迁移指南 (MIGRATION.md)
   - 快速开始 (QUICKSTART.md)
   - 项目完成总结 (PROJECT_COMPLETE.md)
   - 更新总结 (UPDATE_SUMMARY.md)

#### 使用建议

**推荐工作流**:
1. 如有 DWG 文件，转换为 DXF（使用免费工具）
2. 使用 `dxf_extractor.py` 提取元素（更快、免费、跨平台）
3. 如必须使用 DWG，则用 `dwg_extractor.py`（需要 AutoCAD）

**快速开始**:

```python
# DXF 提取（推荐 - 不需要 AutoCAD）
from dxf_extractor import DXFExtractor
extractor = DXFExtractor()
elements = extractor.extract_from_file("file.dxf")
extractor.save_to_csv("output.csv")

# DWG 提取（需要 AutoCAD）
from dwg_extractor import DWGExtractor
extractor = DWGExtractor()
elements = extractor.extract_from_file("file.dwg")
extractor.save_to_csv("output.csv")
```

**更多信息**:
- DXF 使用文档: `DXF_EXTRACTOR_README.md`
- 选择指南: `DWG_vs_DXF_GUIDE.md`
- 快速开始: `QUICKSTART.md`

---

## 开发者

- 项目名称: GetDwgInfo
- 许可证: MIT License
- 最后更新: 2025-11-15

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
