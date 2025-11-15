"""
DXF 文件元素提取器

使用 ezdxf 库从 DXF 文件中提取各种元素（文本、线条、矩形、圆形等）
"""

import os
import csv
import logging
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
import ezdxf
from ezdxf.document import Drawing
from ezdxf.entities import Text, MText, Line, LWPolyline, Polyline, Circle


@dataclass
class TextElement:
    """文本元素数据类"""

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

    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    color: int = 7
    layer: str = ""


@dataclass
class CircleElement:
    """圆形元素数据类"""

    center_x: float = 0.0
    center_y: float = 0.0
    center_z: float = 0.0
    radius: float = 0.0
    color: int = 7
    layer: str = ""


@dataclass
class PolylineElement:
    """多段线元素数据类"""

    vertices: List[tuple] = field(default_factory=list)
    is_closed: bool = False
    color: int = 7
    layer: str = ""


class DXFExtractor:
    """DXF 文件元素提取器"""

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
        self, dxf_path: str, extract_config: Optional[Dict[str, bool]] = None
    ) -> Dict[str, List]:
        """
        从 DXF 文件中提取元素

        Args:
            dxf_path: DXF 文件路径
            extract_config: 提取配置，指定要提取的元素类型
                {
                    "extract_text": True,    # 是否提取文本
                    "extract_lines": True,   # 是否提取线条
                    "extract_rects": True,   # 是否提取矩形
                    "extract_circles": True, # 是否提取圆形
                }

        Returns:
            包含各类元素的字典
        """
        # 默认配置
        if extract_config is None:
            extract_config = {
                "extract_text": True,
                "extract_lines": True,
                "extract_rects": True,
                "extract_circles": True,
            }

        try:
            self.logger.info(f"开始提取 DXF 文件: {dxf_path}")

            # 检查文件是否存在
            if not os.path.exists(dxf_path):
                raise FileNotFoundError(f"DXF 文件不存在: {dxf_path}")

            # 获取绝对路径
            dxf_path = os.path.abspath(dxf_path)

            # 打开 DXF 文件
            try:
                doc = ezdxf.readfile(dxf_path)
                self.logger.info(f"成功打开文件: {dxf_path}")
            except Exception as e:
                raise RuntimeError(f"无法打开 DXF 文件: {str(e)}")

            # 重置元素列表
            self.elements = {
                "texts": [],
                "lines": [],
                "rects": [],
                "circles": [],
                "polylines": [],
            }

            # 获取模型空间
            msp = doc.modelspace()

            # 统计实体数量
            entity_count = len(list(msp))
            self.logger.info(f"模型空间中共有 {entity_count} 个实体")

            # 遍历所有实体
            for entity in msp:
                try:
                    entity_type = entity.dxftype()

                    # 提取文本元素
                    if extract_config.get("extract_text", True) and entity_type in [
                        "TEXT",
                        "MTEXT",
                    ]:
                        self._extract_text(entity)

                    # 提取线条元素
                    elif (
                        extract_config.get("extract_lines", True)
                        and entity_type == "LINE"
                    ):
                        self._extract_line(entity)

                    # 提取多段线（可能是矩形）
                    elif extract_config.get("extract_rects", True) and entity_type in [
                        "LWPOLYLINE",
                        "POLYLINE",
                    ]:
                        self._extract_polyline(entity)

                    # 提取圆形
                    elif (
                        extract_config.get("extract_circles", True)
                        and entity_type == "CIRCLE"
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
            self.logger.error(f"读取 DXF 文件失败: {str(e)}")
            raise

    def _extract_text(self, entity):
        """提取文本元素"""
        try:
            text_elem = TextElement()

            # 获取文本内容
            text_elem.content = entity.dxf.text if hasattr(entity.dxf, "text") else ""

            # 如果文本为空，跳过
            if not text_elem.content:
                return

            # 获取插入点
            if hasattr(entity.dxf, "insert"):
                insert_point = entity.dxf.insert
                text_elem.x = insert_point[0]
                text_elem.y = insert_point[1]
                text_elem.z = insert_point[2] if len(insert_point) > 2 else 0.0

            # 获取其他属性
            text_elem.height = (
                entity.dxf.height if hasattr(entity.dxf, "height") else 0.0
            )
            text_elem.rotation = (
                entity.dxf.rotation if hasattr(entity.dxf, "rotation") else 0.0
            )
            text_elem.color = entity.dxf.color if hasattr(entity.dxf, "color") else 7
            text_elem.layer = entity.dxf.layer if hasattr(entity.dxf, "layer") else ""
            text_elem.style = entity.dxf.style if hasattr(entity.dxf, "style") else ""

            self.elements["texts"].append(asdict(text_elem))

        except Exception as e:
            self.logger.warning(f"提取文本元素失败: {str(e)}")

    def _extract_line(self, entity):
        """提取线条元素"""
        try:
            line_elem = LineElement()

            # 获取起点和终点
            if hasattr(entity.dxf, "start"):
                start = entity.dxf.start
                line_elem.start_x = start[0]
                line_elem.start_y = start[1]
                line_elem.start_z = start[2] if len(start) > 2 else 0.0

            if hasattr(entity.dxf, "end"):
                end = entity.dxf.end
                line_elem.end_x = end[0]
                line_elem.end_y = end[1]
                line_elem.end_z = end[2] if len(end) > 2 else 0.0

            # 获取其他属性
            line_elem.color = entity.dxf.color if hasattr(entity.dxf, "color") else 7
            line_elem.layer = entity.dxf.layer if hasattr(entity.dxf, "layer") else ""
            line_elem.linetype = (
                entity.dxf.linetype if hasattr(entity.dxf, "linetype") else ""
            )
            line_elem.lineweight = (
                entity.dxf.lineweight if hasattr(entity.dxf, "lineweight") else -1
            )

            self.elements["lines"].append(asdict(line_elem))

        except Exception as e:
            self.logger.warning(f"提取线条元素失败: {str(e)}")

    def _extract_polyline(self, entity):
        """提取多段线元素，识别矩形"""
        try:
            # 获取顶点
            vertices = []
            if hasattr(entity, "get_points"):
                # LWPOLYLINE - get_points() 返回 'format' 格式的点
                # 需要指定格式，默认 'xyb' 包含 x, y, bulge
                points = list(entity.get_points('xy'))  # 只获取 x, y
                vertices = [(p[0], p[1], 0.0) for p in points]
            elif hasattr(entity, "points"):
                # POLYLINE
                points = list(entity.points())
                vertices = [
                    (p[0], p[1], p[2] if len(p) > 2 else 0.0) for p in points
                ]

            if len(vertices) < 3:
                return

            # 检查是否闭合
            is_closed = entity.is_closed if hasattr(entity, "is_closed") else False

            # 如果是闭合的4边形，尝试识别为矩形
            if is_closed and len(vertices) == 4:
                # 检查是否为矩形（简化判断：检查是否有水平和垂直边）
                x_coords = [v[0] for v in vertices]
                y_coords = [v[1] for v in vertices]

                min_x, max_x = min(x_coords), max(x_coords)
                min_y, max_y = min(y_coords), max(y_coords)

                # 检查是否所有点都在边界上
                tolerance = 0.01
                is_rect = True
                for x, y, _ in vertices:
                    on_edge = (
                        abs(x - min_x) < tolerance
                        or abs(x - max_x) < tolerance
                        or abs(y - min_y) < tolerance
                        or abs(y - max_y) < tolerance
                    )
                    if not on_edge:
                        is_rect = False
                        break

                if is_rect:
                    rect_elem = RectElement()
                    rect_elem.x = min_x
                    rect_elem.y = min_y
                    rect_elem.width = max_x - min_x
                    rect_elem.height = max_y - min_y
                    rect_elem.color = (
                        entity.dxf.color if hasattr(entity.dxf, "color") else 7
                    )
                    rect_elem.layer = (
                        entity.dxf.layer if hasattr(entity.dxf, "layer") else ""
                    )

                    self.elements["rects"].append(asdict(rect_elem))
                    return

            # 否则作为普通多段线保存
            polyline_elem = PolylineElement()
            polyline_elem.vertices = vertices
            polyline_elem.is_closed = is_closed
            polyline_elem.color = (
                entity.dxf.color if hasattr(entity.dxf, "color") else 7
            )
            polyline_elem.layer = (
                entity.dxf.layer if hasattr(entity.dxf, "layer") else ""
            )

            self.elements["polylines"].append(asdict(polyline_elem))

        except Exception as e:
            self.logger.warning(f"提取多段线元素失败: {str(e)}")

    def _extract_circle(self, entity):
        """提取圆形元素"""
        try:
            circle_elem = CircleElement()

            # 获取圆心
            if hasattr(entity.dxf, "center"):
                center = entity.dxf.center
                circle_elem.center_x = center[0]
                circle_elem.center_y = center[1]
                circle_elem.center_z = center[2] if len(center) > 2 else 0.0

            # 获取半径
            circle_elem.radius = (
                entity.dxf.radius if hasattr(entity.dxf, "radius") else 0.0
            )

            # 获取其他属性
            circle_elem.color = entity.dxf.color if hasattr(entity.dxf, "color") else 7
            circle_elem.layer = entity.dxf.layer if hasattr(entity.dxf, "layer") else ""

            self.elements["circles"].append(asdict(circle_elem))

        except Exception as e:
            self.logger.warning(f"提取圆形元素失败: {str(e)}")

    def get_all_elements(self) -> List[Dict[str, Any]]:
        """
        获取所有元素的扁平列表

        Returns:
            包含所有元素的列表，每个元素都有 type 字段标识类型
        """
        all_elements = []

        # 添加文本元素
        for text in self.elements["texts"]:
            element = text.copy()
            element["type"] = "text"
            all_elements.append(element)

        # 添加线条元素
        for line in self.elements["lines"]:
            element = line.copy()
            element["type"] = "line"
            all_elements.append(element)

        # 添加矩形元素
        for rect in self.elements["rects"]:
            element = rect.copy()
            element["type"] = "rect"
            all_elements.append(element)

        # 添加圆形元素
        for circle in self.elements["circles"]:
            element = circle.copy()
            element["type"] = "circle"
            all_elements.append(element)

        return all_elements

    def save_to_csv(self, output_path: str) -> None:
        """
        将提取的元素保存到 CSV 文件

        Args:
            output_path: 输出 CSV 文件路径
        """
        try:
            # 获取所有元素
            all_elements = self.get_all_elements()

            if not all_elements:
                self.logger.warning("没有元素可保存")
                return

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 获取所有可能的字段
            fieldnames = set()
            for element in all_elements:
                fieldnames.update(element.keys())

            # 确保 type 字段在第一列
            fieldnames = ["type"] + sorted([f for f in fieldnames if f != "type"])

            # 写入 CSV
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_elements)

            self.logger.info(f"成功保存 {len(all_elements)} 个元素到: {output_path}")

        except Exception as e:
            self.logger.error(f"保存 CSV 文件失败: {str(e)}")
            raise


# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 创建提取器
    extractor = DXFExtractor()

    # 提取 DXF 文件
    try:
        elements = extractor.extract_from_file("input/test.dxf")

        print(f"\n提取结果:")
        print(f"文本: {len(elements['texts'])} 个")
        print(f"线条: {len(elements['lines'])} 个")
        print(f"矩形: {len(elements['rects'])} 个")
        print(f"圆形: {len(elements['circles'])} 个")

        # 保存到 CSV
        extractor.save_to_csv("output/dxf_elements.csv")
        print(f"\n✓ 已保存到 output/dxf_elements.csv")

    except Exception as e:
        print(f"\n✗ 提取失败: {e}")
