"""
元素关联分析模块。

分析 DWG 元素之间的空间关系、颜色关联等。
"""

import logging
import math
from typing import List, Dict, Any, Tuple


class ElementAnalyzer:
    """元素关联分析器类"""

    def __init__(self, max_distance: float = 100.0, alignment_tolerance: float = 5.0):
        """
        初始化分析器。

        :param max_distance: 空间关系最大距离阈值
        :param alignment_tolerance: 对齐容差
        """
        self.logger = logging.getLogger(__name__)
        self.max_distance = max_distance
        self.alignment_tolerance = alignment_tolerance
        self.relationships = []

    def analyze_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析元素之间的关联关系。

        :param elements: 元素列表
        :return: 关联关系列表
        """
        self.logger.info("开始分析元素关联关系，共 %d 个元素", len(elements))
        self.relationships = []

        # 按类型分组元素
        elements_by_type = self._group_by_type(elements)

        # 分析文本和矩形的包含关系
        if "TEXT" in elements_by_type and "RECT" in elements_by_type:
            self._analyze_text_rect_containment(
                elements_by_type["TEXT"], elements_by_type["RECT"]
            )

        # 分析文本和线条的邻近关系
        if "TEXT" in elements_by_type and "LINE" in elements_by_type:
            self._analyze_text_line_proximity(
                elements_by_type["TEXT"], elements_by_type["LINE"]
            )

        # 分析线条和矩形的相交关系
        if "LINE" in elements_by_type and "RECT" in elements_by_type:
            self._analyze_line_rect_intersection(
                elements_by_type["LINE"], elements_by_type["RECT"]
            )

        # 分析颜色关联
        self._analyze_color_relationships(elements)

        # 分析图层关联
        self._analyze_layer_relationships(elements)

        # 分析对齐关系
        self._analyze_alignment(elements)

        self.logger.info("分析完成，找到 %d 个关联关系", len(self.relationships))
        return self.relationships

    def _group_by_type(
        self, elements: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """按类型分组元素"""
        grouped = {}
        for elem in elements:
            elem_type = elem.get("type", "UNKNOWN")
            if elem_type not in grouped:
                grouped[elem_type] = []
            grouped[elem_type].append(elem)
        return grouped

    def _analyze_text_rect_containment(
        self, texts: List[Dict[str, Any]], rects: List[Dict[str, Any]]
    ):
        """分析文本是否包含在矩形内"""
        for i, text in enumerate(texts):
            text_x = text.get("x", 0)
            text_y = text.get("y", 0)

            for j, rect in enumerate(rects):
                rect_x = rect.get("x", 0)
                rect_y = rect.get("y", 0)
                rect_width = rect.get("width", 0)
                rect_height = rect.get("height", 0)

                # 检查文本点是否在矩形内
                if (
                    rect_x <= text_x <= rect_x + rect_width
                    and rect_y <= text_y <= rect_y + rect_height
                ):
                    self.relationships.append(
                        {
                            "type": "CONTAINMENT",
                            "source_index": i,
                            "source_type": "TEXT",
                            "target_index": j,
                            "target_type": "RECT",
                            "description": "文本包含在矩形内",
                            "text_content": text.get("content", ""),
                            "rect_bounds": (
                                f"({rect_x}, {rect_y}, " f"{rect_width}, {rect_height})"
                            ),
                        }
                    )

    def _analyze_text_line_proximity(
        self, texts: List[Dict[str, Any]], lines: List[Dict[str, Any]]
    ):
        """分析文本和线条的邻近关系"""
        for i, text in enumerate(texts):
            text_x = text.get("x", 0)
            text_y = text.get("y", 0)

            for j, line in enumerate(lines):
                # 计算文本点到线段的距离
                distance = self._point_to_line_distance(
                    text_x,
                    text_y,
                    line.get("start_x", 0),
                    line.get("start_y", 0),
                    line.get("end_x", 0),
                    line.get("end_y", 0),
                )

                if distance <= self.max_distance:
                    self.relationships.append(
                        {
                            "type": "PROXIMITY",
                            "source_index": i,
                            "source_type": "TEXT",
                            "target_index": j,
                            "target_type": "LINE",
                            "description": "文本靠近线条",
                            "distance": round(distance, 2),
                            "text_content": text.get("content", ""),
                        }
                    )

    def _analyze_line_rect_intersection(
        self, lines: List[Dict[str, Any]], rects: List[Dict[str, Any]]
    ):
        """分析线条和矩形的相交关系"""
        for i, line in enumerate(lines):
            line_start_x = line.get("start_x", 0)
            line_start_y = line.get("start_y", 0)
            line_end_x = line.get("end_x", 0)
            line_end_y = line.get("end_y", 0)

            for j, rect in enumerate(rects):
                rect_x = rect.get("x", 0)
                rect_y = rect.get("y", 0)
                rect_width = rect.get("width", 0)
                rect_height = rect.get("height", 0)

                # 简单检查：线段端点是否在矩形内或附近
                start_in = (
                    rect_x <= line_start_x <= rect_x + rect_width
                    and rect_y <= line_start_y <= rect_y + rect_height
                )
                end_in = (
                    rect_x <= line_end_x <= rect_x + rect_width
                    and rect_y <= line_end_y <= rect_y + rect_height
                )

                if start_in or end_in:
                    self.relationships.append(
                        {
                            "type": "INTERSECTION",
                            "source_index": i,
                            "source_type": "LINE",
                            "target_index": j,
                            "target_type": "RECT",
                            "description": "线条与矩形相交",
                            "intersection_type": (
                                "both_inside" if start_in and end_in else "partial"
                            ),
                        }
                    )

    def _analyze_color_relationships(self, elements: List[Dict[str, Any]]):
        """分析颜色关联"""
        color_groups = {}

        for i, elem in enumerate(elements):
            color = elem.get("color", -1)
            if color not in color_groups:
                color_groups[color] = []
            color_groups[color].append((i, elem))

        # 记录相同颜色的元素组
        for color, group in color_groups.items():
            if len(group) > 1 and color != -1:
                for idx, (i, elem_i) in enumerate(group):
                    for j, elem_j in group[idx + 1 :]:
                        self.relationships.append(
                            {
                                "type": "COLOR_MATCH",
                                "source_index": i,
                                "source_type": elem_i.get("type", "UNKNOWN"),
                                "target_index": j,
                                "target_type": elem_j.get("type", "UNKNOWN"),
                                "description": "相同颜色",
                                "color": color,
                            }
                        )

    def _analyze_layer_relationships(self, elements: List[Dict[str, Any]]):
        """分析图层关联"""
        layer_groups = {}

        for i, elem in enumerate(elements):
            layer = elem.get("layer", "")
            if layer:
                if layer not in layer_groups:
                    layer_groups[layer] = []
                layer_groups[layer].append((i, elem))

        # 记录相同图层的元素
        for layer, group in layer_groups.items():
            if len(group) > 1:
                for idx, (i, elem_i) in enumerate(group):
                    for j, elem_j in group[idx + 1 :]:
                        self.relationships.append(
                            {
                                "type": "LAYER_MATCH",
                                "source_index": i,
                                "source_type": elem_i.get("type", "UNKNOWN"),
                                "target_index": j,
                                "target_type": elem_j.get("type", "UNKNOWN"),
                                "description": "相同图层",
                                "layer": layer,
                            }
                        )

    def _analyze_alignment(self, elements: List[Dict[str, Any]]):
        """分析元素对齐关系"""
        for i, elem_i in enumerate(elements):
            x_i, y_i = self._get_position(elem_i)
            if x_i is None or y_i is None:
                continue

            for j, elem_j in enumerate(elements[i + 1 :], start=i + 1):
                x_j, y_j = self._get_position(elem_j)
                if x_j is None or y_j is None:
                    continue

                # 检查水平对齐
                if abs(y_i - y_j) <= self.alignment_tolerance:
                    self.relationships.append(
                        {
                            "type": "HORIZONTAL_ALIGNMENT",
                            "source_index": i,
                            "source_type": elem_i.get("type", "UNKNOWN"),
                            "target_index": j,
                            "target_type": elem_j.get("type", "UNKNOWN"),
                            "description": "水平对齐",
                            "y_coordinate": round(y_i, 2),
                        }
                    )

                # 检查垂直对齐
                if abs(x_i - x_j) <= self.alignment_tolerance:
                    self.relationships.append(
                        {
                            "type": "VERTICAL_ALIGNMENT",
                            "source_index": i,
                            "source_type": elem_i.get("type", "UNKNOWN"),
                            "target_index": j,
                            "target_type": elem_j.get("type", "UNKNOWN"),
                            "description": "垂直对齐",
                            "x_coordinate": round(x_i, 2),
                        }
                    )

    def _get_position(self, elem: Dict[str, Any]) -> Tuple[float, float]:
        """获取元素位置"""
        elem_type = elem.get("type", "")

        if elem_type == "TEXT":
            return elem.get("x"), elem.get("y")
        elif elem_type == "LINE":
            # 使用中点
            start_x = elem.get("start_x", 0)
            start_y = elem.get("start_y", 0)
            end_x = elem.get("end_x", 0)
            end_y = elem.get("end_y", 0)
            return (start_x + end_x) / 2, (start_y + end_y) / 2
        elif elem_type == "RECT":
            # 使用中心点
            x = elem.get("x", 0)
            y = elem.get("y", 0)
            width = elem.get("width", 0)
            height = elem.get("height", 0)
            return x + width / 2, y + height / 2
        elif elem_type == "CIRCLE":
            return elem.get("center_x"), elem.get("center_y")

        return None, None

    def _point_to_line_distance(
        self, px: float, py: float, x1: float, y1: float, x2: float, y2: float
    ) -> float:
        """计算点到线段的距离"""
        # 线段长度
        line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if line_length == 0:
            # 线段退化为点
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

        # 计算投影参数
        t = max(
            0,
            min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_length**2)),
        )

        # 计算投影点
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)

        # 返回距离
        return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)

    def generate_report(self) -> str:
        """
        生成关联分析报告。

        :return: 报告文本
        """
        if not self.relationships:
            return "没有发现元素之间的关联关系。"

        report_lines = ["=" * 60]
        report_lines.append("元素关联性分析报告")
        report_lines.append("=" * 60)
        report_lines.append("")

        # 按类型统计
        type_counts = {}
        for rel in self.relationships:
            rel_type = rel.get("type", "UNKNOWN")
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1

        report_lines.append("关联类型统计：")
        for rel_type, count in sorted(type_counts.items()):
            report_lines.append(f"  - {rel_type}: {count} 个")

        report_lines.append("")
        report_lines.append(f"总关联关系数: {len(self.relationships)}")
        report_lines.append("=" * 60)

        return "\n".join(report_lines)
