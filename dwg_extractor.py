"""
DWG 元素提取模块。

从 DWG 文件中提取文本、线条、矩形等元素及其详细特征。
使用 pyautocad 通过 AutoCAD COM 接口提取数据。
"""

import logging
import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

try:
    from pyautocad import Autocad, APoint
    import win32com.client

    PYAUTOCAD_AVAILABLE = True
except ImportError:
    PYAUTOCAD_AVAILABLE = False


@dataclass
class TextElement:
    """文本元素数据类"""

    type: str = "TEXT"
    content: str = ""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    height: float = 0.0
    rotation: float = 0.0
    color: int = 7
    layer: str = ""
    style: str = ""


@dataclass
class LineElement:
    """线条元素数据类"""

    type: str = "LINE"
    start_x: float = 0.0
    start_y: float = 0.0
    start_z: float = 0.0
    end_x: float = 0.0
    end_y: float = 0.0
    end_z: float = 0.0
    color: int = 7
    layer: str = ""
    linetype: str = ""
    lineweight: int = -1


@dataclass
class RectElement:
    """矩形元素数据类"""

    type: str = "RECT"
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    width: float = 0.0
    height: float = 0.0
    color: int = 7
    layer: str = ""
    is_closed: bool = True


@dataclass
class CircleElement:
    """圆形元素数据类"""

    type: str = "CIRCLE"
    center_x: float = 0.0
    center_y: float = 0.0
    center_z: float = 0.0
    radius: float = 0.0
    color: int = 7
    layer: str = ""


class DWGExtractor:
    """DWG 元素提取器类"""

    def __init__(self):
        """初始化提取器"""
        self.logger = logging.getLogger(__name__)
        self.elements = {
            "texts": [],
            "lines": [],
            "rects": [],
            "circles": [],
            "polylines": [],
        }

    def extract_from_file(
        self, dwg_path: str, extract_config: Dict[str, bool] = None
    ) -> Dict[str, List]:
        """
        从 DWG 文件中提取元素。

        :param dwg_path: DWG 文件路径
        :param extract_config: 提取配置字典，指定要提取的元素类型
        :return: 包含各类元素的字典
        """
        if extract_config is None:
            extract_config = {
                "extract_text": True,
                "extract_lines": True,
                "extract_rects": True,
                "extract_circles": True,
            }

        acad = None
        doc = None
        original_doc = None

        try:
            self.logger.info(f"开始提取 DWG 文件: {dwg_path}")

            # 检查文件是否存在
            if not os.path.exists(dwg_path):
                raise FileNotFoundError(f"DWG 文件不存在: {dwg_path}")

            # 获取绝对路径
            dwg_path = os.path.abspath(dwg_path)

            # 连接到 AutoCAD - 使用 win32com 直接连接
            try:
                # 尝试获取已运行的 AutoCAD 实例
                acad_app = None
                progids = [
                    "AutoCAD.Application",
                    "AutoCAD.Application.24",  # AutoCAD 2020
                    "AutoCAD.Application.23",  # AutoCAD 2019
                    "AutoCAD.Application.22",  # AutoCAD 2018
                    "AutoCAD.Application.21",  # AutoCAD 2017
                    "AutoCAD.Application.20",  # AutoCAD 2016
                ]

                # 首先尝试连接到已运行的实例
                for progid in progids:
                    try:
                        acad_app = win32com.client.GetActiveObject(progid)
                        self.logger.info(f"连接到已运行的 AutoCAD: {progid}")
                        break
                    except:
                        continue

                # 如果没有运行实例，尝试启动新实例
                if acad_app is None:
                    for progid in progids:
                        try:
                            acad_app = win32com.client.Dispatch(progid)
                            acad_app.Visible = True
                            self.logger.info(f"启动新的 AutoCAD 实例: {progid}")
                            # 等待 AutoCAD 初始化
                            time.sleep(2)
                            break
                        except:
                            continue

                if acad_app is None:
                    raise RuntimeError("无法找到或启动 AutoCAD")

                self.logger.info("成功连接到 AutoCAD")
            except Exception as e:
                raise RuntimeError(
                    f"无法连接到 AutoCAD，请确保 AutoCAD 已安装并可以启动。错误: {str(e)}"
                )  # 保存当前文档引用
            try:
                if acad_app.Documents.Count > 0:
                    original_doc = acad_app.ActiveDocument
            except:
                original_doc = None

            # 打开 DWG 文件
            try:
                # 使用 Documents.Open 方法
                # 参数: Name, [ReadOnly], [Password]
                doc = acad_app.Documents.Open(dwg_path, True)  # True = 只读
                # 设置为活动文档并获取引用
                acad_app.ActiveDocument = doc
                # 重新获取活动文档引用以确保正确
                doc = acad_app.ActiveDocument
                self.logger.info(f"成功打开文件: {dwg_path}")
            except Exception as e:
                raise RuntimeError(f"无法打开 DWG 文件: {str(e)}")

            # 重置元素列表
            self.elements = {
                "texts": [],
                "lines": [],
                "rects": [],
                "circles": [],
                "polylines": [],
            }

            # 获取模型空间
            modelspace = doc.ModelSpace

            # 获取实体数量
            entity_count = modelspace.Count
            self.logger.info(f"模型空间中共有 {entity_count} 个实体")

            # 遍历所有实体 - 使用索引方式而不是迭代器
            for i in range(entity_count):
                try:
                    entity = modelspace.Item(i)
                    entity_type = entity.ObjectName

                    # 提取文本元素
                    if extract_config.get("extract_text", True) and entity_type in [
                        "AcDbText",
                        "AcDbMText",
                    ]:
                        self._extract_text(entity)

                    # 提取线条元素
                    elif (
                        extract_config.get("extract_lines", True)
                        and entity_type == "AcDbLine"
                    ):
                        self._extract_line(entity)

                    # 提取多段线（可能是矩形）
                    elif extract_config.get("extract_rects", True) and entity_type in [
                        "AcDbPolyline",
                        "AcDb2dPolyline",
                        "AcDbLwPolyline",
                    ]:
                        self._extract_polyline(entity)

                    # 提取圆形
                    elif (
                        extract_config.get("extract_circles", True)
                        and entity_type == "AcDbCircle"
                    ):
                        self._extract_circle(entity)

                except Exception as e:
                    self.logger.warning(
                        f"提取实体时出错: {entity_type if 'entity_type' in locals() else 'Unknown'}, "
                        f"错误: {str(e)}"
                    )
                    continue

            self.logger.info(
                f"提取完成 - 文本: {len(self.elements['texts'])}, "
                f"线条: {len(self.elements['lines'])}, "
                f"矩形: {len(self.elements['rects'])}, "
                f"圆形: {len(self.elements['circles'])}"
            )

            return self.elements

        except Exception as e:
            self.logger.error(f"读取 DWG 文件失败: {str(e)}")
            raise

        finally:
            # 关闭打开的文档
            if doc is not None:
                try:
                    doc.Close(False)  # False = 不保存更改
                    self.logger.info("已关闭 DWG 文件")
                except Exception as e:
                    self.logger.warning(f"关闭文档时出错: {str(e)}")

            # 恢复原始文档
            if (
                "acad_app" in locals()
                and acad_app is not None
                and original_doc is not None
            ):
                try:
                    acad_app.ActiveDocument = original_doc
                except:
                    pass

    def _safe_get_attribute(self, entity, attr_name, default=None, max_retries=3):
        """安全地获取COM对象属性，带重试机制"""
        for attempt in range(max_retries):
            try:
                if hasattr(entity, attr_name):
                    return getattr(entity, attr_name)
                return default
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.01)  # 等待10毫秒后重试
                    continue
                # 最后一次尝试仍失败，返回默认值
                return default

    def _extract_text(self, entity):
        """提取文本元素"""
        try:
            text_elem = TextElement()

            # 获取文本内容
            text_elem.content = self._safe_get_attribute(entity, "TextString", "")

            # 如果文本为空，跳过
            if not text_elem.content:
                return

            # 获取插入点
            insert_point = self._safe_get_attribute(entity, "InsertionPoint")
            if insert_point:
                text_elem.x = insert_point[0]
                text_elem.y = insert_point[1]
                text_elem.z = insert_point[2] if len(insert_point) > 2 else 0.0
            else:
                origin = self._safe_get_attribute(entity, "Origin")
                if origin:
                    text_elem.x = origin[0]
                    text_elem.y = origin[1]
                    text_elem.z = origin[2] if len(origin) > 2 else 0.0

            # 获取其他属性
            text_elem.height = self._safe_get_attribute(entity, "Height", 0.0)
            text_elem.rotation = self._safe_get_attribute(entity, "Rotation", 0.0)
            text_elem.color = self._safe_get_attribute(entity, "Color", 7)
            text_elem.layer = self._safe_get_attribute(entity, "Layer", "")
            text_elem.style = self._safe_get_attribute(entity, "StyleName", "")

            self.elements["texts"].append(asdict(text_elem))

        except Exception as e:
            self.logger.warning(f"提取文本元素失败: {str(e)}")

    def _extract_line(self, entity):
        """提取线条元素"""
        try:
            line_elem = LineElement()

            # 获取起点和终点
            start = self._safe_get_attribute(entity, "StartPoint")
            if start:
                line_elem.start_x = start[0]
                line_elem.start_y = start[1]
                line_elem.start_z = start[2] if len(start) > 2 else 0.0

            end = self._safe_get_attribute(entity, "EndPoint")
            if end:
                line_elem.end_x = end[0]
                line_elem.end_y = end[1]
                line_elem.end_z = end[2] if len(end) > 2 else 0.0

            # 获取其他属性
            line_elem.color = self._safe_get_attribute(entity, "Color", 7)
            line_elem.layer = self._safe_get_attribute(entity, "Layer", "")
            line_elem.linetype = self._safe_get_attribute(entity, "Linetype", "")
            line_elem.lineweight = self._safe_get_attribute(entity, "Lineweight", -1)

            self.elements["lines"].append(asdict(line_elem))

        except Exception as e:
            self.logger.warning(f"提取线条元素失败: {str(e)}")

    def _extract_polyline(self, entity):
        """提取多段线元素，识别矩形"""
        try:
            # 获取顶点坐标
            vertices = []
            if hasattr(entity, "Coordinates"):
                coords = entity.Coordinates
                # coords 是扁平数组 [x1, y1, x2, y2, ...]
                for i in range(0, len(coords), 2):
                    if i + 1 < len(coords):
                        vertices.append([coords[i], coords[i + 1], 0.0])

            # 检查是否为闭合多段线
            is_closed = entity.Closed if hasattr(entity, "Closed") else False

            # 如果是闭合的4个顶点，可能是矩形
            if is_closed and len(vertices) == 4:
                rect_elem = RectElement()

                # 计算边界框
                xs = [v[0] for v in vertices]
                ys = [v[1] for v in vertices]

                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)

                rect_elem.x = min_x
                rect_elem.y = min_y
                rect_elem.z = vertices[0][2] if len(vertices[0]) > 2 else 0.0
                rect_elem.width = max_x - min_x
                rect_elem.height = max_y - min_y
                rect_elem.color = entity.Color if hasattr(entity, "Color") else 7
                rect_elem.layer = entity.Layer if hasattr(entity, "Layer") else ""
                rect_elem.is_closed = is_closed

                self.elements["rects"].append(asdict(rect_elem))
            else:
                # 存储为一般多段线
                polyline_data = {
                    "type": "POLYLINE",
                    "vertices": vertices,
                    "is_closed": is_closed,
                    "color": entity.Color if hasattr(entity, "Color") else 7,
                    "layer": entity.Layer if hasattr(entity, "Layer") else "",
                }
                self.elements["polylines"].append(polyline_data)

        except Exception as e:
            self.logger.warning(f"提取多段线元素失败: {str(e)}")

    def _extract_circle(self, entity):
        """提取圆形元素"""
        try:
            circle_elem = CircleElement()

            # 获取圆心和半径
            if hasattr(entity, "Center"):
                center = entity.Center
                circle_elem.center_x = center[0]
                circle_elem.center_y = center[1]
                circle_elem.center_z = center[2] if len(center) > 2 else 0.0

            circle_elem.radius = entity.Radius if hasattr(entity, "Radius") else 0.0

            # 获取其他属性
            circle_elem.color = entity.Color if hasattr(entity, "Color") else 7
            circle_elem.layer = entity.Layer if hasattr(entity, "Layer") else ""

            self.elements["circles"].append(asdict(circle_elem))

        except Exception as e:
            self.logger.warning(f"提取圆形元素失败: {str(e)}")

    def get_all_elements(self) -> List[Dict[str, Any]]:
        """
        获取所有元素的扁平列表。

        :return: 包含所有元素的列表
        """
        all_elements = []

        for element_list in [
            self.elements["texts"],
            self.elements["lines"],
            self.elements["rects"],
            self.elements["circles"],
        ]:
            all_elements.extend(element_list)

        return all_elements

    def save_to_csv(self, filepath: str) -> str:
        """
        保存提取的元素到CSV文件。

        :param filepath: 输出文件路径
        :return: 保存的文件路径
        """
        import csv

        all_elements = self.get_all_elements()

        if not all_elements:
            self.logger.warning("没有元素数据需要保存")
            return ""

        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # 获取所有可能的字段名
            fieldnames = set()
            for elem in all_elements:
                fieldnames.update(elem.keys())
            fieldnames = sorted(list(fieldnames))

            # 写入 CSV 文件
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_elements)

            self.logger.info(f"成功保存 {len(all_elements)} 个元素到 {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"保存CSV文件失败: {str(e)}")
            raise
