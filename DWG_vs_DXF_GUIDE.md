# DWG vs DXF 提取器对比指南

## 快速选择指南

```
有 DWG 文件?
    ├─ 有 AutoCAD? 
    │   ├─ 是 → 使用 dwg_extractor.py
    │   └─ 否 → 先转换为 DXF，再使用 dxf_extractor.py
    └─ 有 DXF 文件?
        └─ 是 → 使用 dxf_extractor.py (推荐)
```

## 详细对比

| 特性 | dwg_extractor.py | dxf_extractor.py |
|------|------------------|------------------|
| **文件格式** | DWG (AutoCAD 原生) | DXF (交换格式) |
| **依赖库** | pyautocad, pywin32 | ezdxf |
| **需要 AutoCAD** | ✅ 必需 | ❌ 不需要 |
| **平台支持** | Windows only | Windows/Linux/macOS |
| **处理速度** | 较慢 (依赖 AutoCAD) | 快 (直接读取) |
| **准确性** | 100% (官方 COM API) | 99%+ (ezdxf) |
| **内存占用** | 高 (AutoCAD 进程) | 低 (纯 Python) |
| **批处理** | 可以，但需保持 AutoCAD 运行 | 非常适合 |
| **安装难度** | 中等 (需要 AutoCAD 许可) | 简单 (pip install) |
| **学习曲线** | 容易 | 容易 |

## 使用场景

### 使用 dwg_extractor.py 当:

1. **只有 DWG 文件**
   - 没有工具转换为 DXF
   - DWG 是唯一格式

2. **已安装 AutoCAD**
   - 公司有 AutoCAD 许可
   - 日常工作使用 AutoCAD

3. **需要 100% 准确性**
   - 处理复杂的 AutoCAD 特性
   - 不能容忍任何数据丢失

4. **处理新版本 DWG**
   - AutoCAD 2019-2024 格式
   - 使用最新 AutoCAD 特性

### 使用 dxf_extractor.py 当:

1. **已有 DXF 文件** ⭐ 推荐
   - 直接使用，无需 AutoCAD
   - 最快最简单的方式

2. **没有 AutoCAD** ⭐ 推荐
   - 不想购买 AutoCAD 许可
   - 在 Linux/macOS 上运行

3. **批量处理** ⭐ 推荐
   - 处理大量文件
   - 需要快速执行
   - 服务器端处理

4. **跨平台需求** ⭐ 推荐
   - 需要在多个操作系统上运行
   - Docker 容器中运行

5. **自动化流程**
   - CI/CD 管道
   - 无人值守处理
   - Web 服务

## 性能对比

### 小文件 (< 1000 实体)

| 提取器 | 时间 | 内存 |
|--------|------|------|
| DWG | 5-10秒 | ~500MB |
| DXF | 1-3秒 | ~50MB |

### 中等文件 (1000-10000 实体)

| 提取器 | 时间 | 内存 |
|--------|------|------|
| DWG | 15-30秒 | ~500MB |
| DXF | 3-10秒 | ~100MB |

### 大文件 (> 10000 实体)

| 提取器 | 时间 | 内存 |
|--------|------|------|
| DWG | 30秒+ | ~500MB+ |
| DXF | 10-30秒 | ~200MB |

## 代码示例对比

### DWG 提取器

```python
from dwg_extractor import DWGExtractor

# 需要 AutoCAD 运行在 Windows 上
extractor = DWGExtractor()
elements = extractor.extract_from_file("file.dwg")
extractor.save_to_csv("output.csv")
```

### DXF 提取器

```python
from dxf_extractor import DXFExtractor

# 不需要 AutoCAD，跨平台
extractor = DXFExtractor()
elements = extractor.extract_from_file("file.dxf")
extractor.save_to_csv("output.csv")
```

**代码完全一致！** 只需改变导入的模块和文件扩展名。

## 文件转换方案

如果只有 DWG 文件，建议转换为 DXF 后使用 `dxf_extractor.py`：

### 方案 1: 使用 AutoCAD (如果有)

```
1. 打开 DWG 文件
2. 文件 → 另存为
3. 格式选择 "AutoCAD 2018 DXF (*.dxf)"
4. 保存
```

### 方案 2: 使用 DWG TrueView (免费)

1. 下载 [Autodesk DWG TrueView](https://www.autodesk.com/products/dwg/viewers)
2. 安装后打开
3. 批量转换 DWG → DXF

### 方案 3: 使用 ODA File Converter (免费)

1. 下载 [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter)
2. 批量转换 DWG → DXF
3. 支持命令行自动化

### 方案 4: 在线转换 (小文件)

- CloudConvert: https://cloudconvert.com/dwg-to-dxf
- Zamzar: https://www.zamzar.com/convert/dwg-to-dxf/
- AnyConv: https://anyconv.com/dwg-to-dxf-converter/

## 最佳实践

### 推荐工作流 🌟

```
1. 获取 DWG 文件
   ↓
2. 转换为 DXF (使用免费工具)
   ↓
3. 使用 dxf_extractor.py 提取
   ↓
4. 导出 CSV 进行分析
```

**优势:**
- ✅ 不需要 AutoCAD 许可 (节省成本)
- ✅ 处理速度快
- ✅ 可在任何平台运行
- ✅ 适合自动化
- ✅ 资源占用少

### 混合使用策略

**开发环境:**
- 使用 `dwg_extractor.py` (已有 AutoCAD)
- 实时测试和调试

**生产环境:**
- DWG → DXF 转换
- 使用 `dxf_extractor.py` 批量处理
- 部署在 Linux 服务器

## 常见问题

### Q: DXF 会丢失数据吗？

A: DXF 是 AutoCAD 的官方交换格式，几乎不会丢失数据。对于标准 CAD 元素（文本、线条、圆形等），DXF 和 DWG 完全等效。

### Q: 转换会降低精度吗？

A: 不会。DXF 保存的是矢量数据，精度与 DWG 相同。

### Q: 哪个提取器更准确？

A: `dwg_extractor.py` 使用 AutoCAD 官方 COM API，理论上 100% 准确。`dxf_extractor.py` 使用成熟的 ezdxf 库，准确性也在 99%+ 以上。对于标准元素，两者效果相同。

### Q: 可以同时使用两个提取器吗？

A: 可以！它们的 API 完全兼容，可以根据文件格式选择使用。

### Q: 批量处理应该用哪个？

A: 推荐 `dxf_extractor.py`：
- 更快的处理速度
- 更低的资源占用
- 不需要管理 AutoCAD 进程
- 更稳定可靠

## 成本对比

### DWG 提取器成本

- AutoCAD 许可: $1,775/年 或 $220/月
- Windows 服务器: 必需
- 总成本: **高**

### DXF 提取器成本

- ezdxf: 免费 (MIT License)
- 转换工具: 免费
- 任何操作系统: 灵活
- 总成本: **免费**

## 推荐方案

### 个人用户 / 小团队

```
建议: DXF 提取器
原因: 免费、快速、跨平台
```

### 企业用户 (已有 AutoCAD)

```
建议: 混合使用
- 开发: DWG 提取器
- 生产: DXF 提取器
```

### 服务器端处理

```
建议: DXF 提取器
原因: 稳定、快速、低成本
```

### 临时项目

```
建议: DXF 提取器
原因: 无需安装 AutoCAD
```

## 总结

**简单选择规则:**

1. 有 DXF 文件 → `dxf_extractor.py` ✅
2. 有 DWG + AutoCAD → `dwg_extractor.py` ✅
3. 有 DWG 无 AutoCAD → 转 DXF + `dxf_extractor.py` ✅
4. 批量处理 → `dxf_extractor.py` ✅
5. 跨平台 → `dxf_extractor.py` ✅

**最推荐:** 转换 DWG → DXF，然后使用 `dxf_extractor.py` 🌟
