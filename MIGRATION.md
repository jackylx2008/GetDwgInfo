# 从 ezdxf 迁移到 pyautocad 的说明

## 主要变更

本次更新将 DWG 文件解析库从 `ezdxf` 更换为 `pyautocad`。

### 为什么更换？

| 特性         | ezdxf         | pyautocad              |
| ------------ | ------------- | ---------------------- |
| 依赖         | 无需 AutoCAD  | 需要 AutoCAD           |
| 平台         | 跨平台        | 仅 Windows             |
| 性能         | 快速          | 较慢（COM 调用）       |
| 数据准确性   | 解析 DXF 格式 | AutoCAD 原生数据       |
| 文件版本支持 | 有限          | AutoCAD 支持的所有版本 |

**选择 pyautocad 的优势**:
1. 获取 AutoCAD 原生数据，更准确
2. 支持所有 AutoCAD 能打开的 DWG 文件版本
3. 可以访问更多 AutoCAD 特性和属性

## 变更内容

### 1. 依赖包更新 (`requirements.txt`)

**之前**:
```
ezdxf>=1.0.0
PyYAML>=6.0
```

**现在**:
```
pyautocad
pywin32
PyYAML>=6.0
```

### 2. 核心模块重写 (`dwg_extractor.py`)

#### 导入变更
```python
# 之前
import ezdxf

# 现在
from pyautocad import Autocad, APoint
import os
```

#### 连接方式变更

**之前**: 直接读取文件
```python
doc = ezdxf.readfile(dwg_path)
modelspace = doc.modelspace()
```

**现在**: 通过 AutoCAD COM 接口
```python
acad = Autocad(create_if_not_exists=True)
doc = acad.app.Documents.Open(dwg_path)
modelspace = doc.ModelSpace
```

#### 实体类型识别变更

**之前**: 使用 DXF 类型名
```python
entity.dxftype() in ["TEXT", "MTEXT"]
entity.dxftype() == "LINE"
```

**现在**: 使用 AutoCAD 对象名
```python
entity.ObjectName in ["AcDbText", "AcDbMText"]
entity.ObjectName == "AcDbLine"
```

#### 属性访问变更

**之前**: 通过 `entity.dxf` 访问
```python
text_elem.content = entity.dxf.text
text_elem.color = entity.dxf.color
```

**现在**: 直接访问 COM 属性
```python
text_elem.content = entity.TextString
text_elem.color = entity.Color
```

### 3. 新增文件

- **test_connection.py**: 测试 AutoCAD 连接
- **example.py**: 使用示例脚本

### 4. 文档更新 (`README.md`)

- 添加了系统要求说明（Windows + AutoCAD）
- 更新了安装说明
- 添加了测试连接步骤
- 添加了注意事项

## 安装和使用

### 安装步骤

1. 确保已安装 AutoCAD（任意版本）
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 测试连接：
   ```bash
   python test_connection.py
   ```

### 使用示例

```bash
# 基本使用
python main.py input/test.dwg

# 查看示例
python example.py
```

## 兼容性说明

### 优点
- ✅ 支持所有 AutoCAD DWG 文件版本
- ✅ 数据提取更准确
- ✅ 可访问更多 AutoCAD 特性

### 限制
- ❌ 仅支持 Windows 系统
- ❌ 必须安装 AutoCAD
- ❌ 处理速度比文件解析慢
- ❌ AutoCAD 必须能够打开文件

## 故障排除

### 常见问题

1. **"无法连接到 AutoCAD"**
   - 确保 AutoCAD 已安装
   - 以管理员身份运行脚本
   - 检查 AutoCAD 是否能正常启动

2. **"无法打开 DWG 文件"**
   - 确保文件路径正确
   - 检查文件是否损坏
   - 尝试在 AutoCAD 中手动打开文件

3. **性能问题**
   - COM 接口比直接解析慢，这是正常的
   - 大文件可能需要更长时间
   - 考虑只提取必要的元素类型

## 回退到 ezdxf

如果需要回退到 ezdxf：

1. 恢复 `requirements.txt`：
   ```
   ezdxf>=1.0.0
   PyYAML>=6.0
   ```

2. 恢复 `dwg_extractor.py` 的原始版本
   - 使用 git 或备份恢复

3. 重新安装依赖：
   ```bash
   pip uninstall pyautocad pywin32
   pip install ezdxf>=1.0.0
   ```

## 技术细节

### COM 接口工作原理

```python
# 连接到 AutoCAD 应用程序
acad = Autocad()

# 打开文档
doc = acad.app.Documents.Open(dwg_path)

# 遍历模型空间中的所有实体
for entity in doc.ModelSpace:
    # 访问实体属性
    entity_type = entity.ObjectName
    layer = entity.Layer
    color = entity.Color
    
# 关闭文档（不保存）
doc.Close(False)
```

### 资源管理

程序会自动：
- 在完成后关闭打开的文档
- 恢复原始活动文档
- 处理异常情况

```python
finally:
    if doc is not None:
        doc.Close(False)  # 不保存更改
    if acad is not None and original_doc is not None:
        acad.app.ActiveDocument = original_doc
```

## 贡献

如有问题或建议，欢迎提出 issue 或 pull request。
