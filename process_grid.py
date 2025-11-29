import os
import math
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
from dxf_extractor import DXFExtractor
from logging_config import setup_logger


@dataclass
class GridAxis:
    """
    定义一根完整的建筑轴线
    """

    label: str  # 轴号 (例如 "1", "A", "1-1")
    start_point: Tuple[float, float]  # 轴线起点 (x, y)
    end_point: Tuple[float, float]  # 轴线终点 (x, y)
    is_vertical: bool  # True=纵向轴线(定X), False=横向轴线(定Y)
    coordinate: float  # 排序用的主坐标值 (纵向为X值，横向为Y值)

    def __repr__(self):
        dir_str = "纵" if self.is_vertical else "横"
        return f"<轴线 {self.label} [{dir_str}] @ {self.coordinate:.4f} (len={self.length:.2f})>"

    @property
    def length(self) -> float:
        return math.sqrt(
            (self.end_point[0] - self.start_point[0]) ** 2
            + (self.end_point[1] - self.start_point[1]) ** 2
        )


class GridNetwork:
    """
    建筑轴网数据结构
    """

    def __init__(self):
        # 与 dxf_extractor.py 保持一致的 logger 使用方式
        # 具体的 handler / 格式由 logging_config.setup_logger 统一配置
        self.logger = logging.getLogger(__name__)
        self.raw_lines: List[Dict[str, Any]] = []
        self.raw_texts: List[Dict[str, Any]] = []
        self.raw_circles: List[Dict[str, Any]] = []

        # 最终提取的轴线列表
        self.axes: List[GridAxis] = []

    def to_dict(self) -> Dict[str, Any]:
        """将轴网信息转换为可序列化的字典结构"""
        return {
            "x_axes": [
                {
                    "label": a.label,
                    "start_point": list(a.start_point),
                    "end_point": list(a.end_point),
                    "is_vertical": a.is_vertical,
                    "coordinate": a.coordinate,
                }
                for a in self.x_axes
            ],
            "y_axes": [
                {
                    "label": a.label,
                    "start_point": list(a.start_point),
                    "end_point": list(a.end_point),
                    "is_vertical": a.is_vertical,
                    "coordinate": a.coordinate,
                }
                for a in self.y_axes
            ],
        }

    def save_to_json(self, output_path: str) -> None:
        """将轴网信息保存为 JSON 文件"""
        logger = logging.getLogger(__name__)
        data = self.to_dict()

        # 确保输出目录存在
        directory = os.path.dirname(output_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info("已将轴网信息保存为 JSON: %s", output_path)

    @property
    def x_axes(self) -> List[GridAxis]:
        """返回所有纵向轴线 (按 X 坐标排序)"""
        return sorted(
            [a for a in self.axes if a.is_vertical], key=lambda x: x.coordinate
        )

    @property
    def y_axes(self) -> List[GridAxis]:
        """返回所有横向轴线 (按 Y 坐标排序)"""
        return sorted(
            [a for a in self.axes if not a.is_vertical], key=lambda x: x.coordinate
        )

    def load_from_dxf(
        self, dxf_path: str, axis_layer_keywords: Optional[List[str]] = None
    ):
        """
        从 DXF 文件加载并构建轴网
        :param dxf_path: DXF 文件路径
        :param axis_layer_keywords: 轴线图层关键字列表，如 ['DOTE', 'AXIS']。如果为 None，则使用所有线。
        """
        if not os.path.exists(dxf_path):
            self.logger.error("找不到文件: %s", dxf_path)
            raise FileNotFoundError(f"找不到文件: {dxf_path}")

        self.logger.info("正在加载轴网文件: %s ...", dxf_path)
        extractor = DXFExtractor(dxf_path)
        extractor.extract()

        self.raw_lines = extractor.get_lines()
        self.raw_texts = extractor.get_texts()
        self.raw_circles = extractor.get_circles()

        self.logger.info(
            "原始数据: %d 线条, %d 文本", len(self.raw_lines), len(self.raw_texts)
        )

        self._analyze_structure(axis_layer_keywords)

    def _analyze_structure(self, layer_keywords: Optional[List[str]] = None):
        """
        核心算法：分析原始线条和文本，构建 GridAxis 对象
        """
        self.logger.info("正在分析轴网结构...")

        # 1. 过滤潜在的轴线 (根据图层关键字)
        candidate_lines = []
        if layer_keywords:
            keywords = [k.upper() for k in layer_keywords]
            for line in self.raw_lines:
                layer = line.get("layer", "").upper()
                if any(k in layer for k in keywords):
                    candidate_lines.append(line)
        else:
            # 如果没指定图层，使用所有线条 (可能会有干扰，建议指定)
            candidate_lines = self.raw_lines

        self.logger.info("筛选出 %d 条潜在轴线段", len(candidate_lines))

        # 2. 线条聚类 (合并共线线段)
        # 容差值 (单位: 图纸单位，通常是mm)
        TOLERANCE = 100.0  # 坐标归并容差

        vertical_groups = defaultdict(list)  # Key: round(x), Value: list of lines
        horizontal_groups = defaultdict(list)  # Key: round(y), Value: list of lines

        for line in candidate_lines:
            # 注意：dxf_extractor 返回的已经是字符串格式的数字了，需要转回 float 计算
            try:
                x1 = float(line["start_x"])
                y1 = float(line["start_y"])
                x2 = float(line["end_x"])
                y2 = float(line["end_y"])
            except ValueError:
                continue

            # 判断方向
            if abs(x1 - x2) < 1.0:  # 垂直线
                key = round((x1 + x2) / 2 / TOLERANCE) * TOLERANCE  # 归一化坐标
                vertical_groups[key].append(
                    {"start_x": x1, "start_y": y1, "end_x": x2, "end_y": y2}
                )
            elif abs(y1 - y2) < 1.0:  # 水平线
                key = round((y1 + y2) / 2 / TOLERANCE) * TOLERANCE
                horizontal_groups[key].append(
                    {"start_x": x1, "start_y": y1, "end_x": x2, "end_y": y2}
                )

        # 3. 构建逻辑轴线 (不含标签)
        temp_axes: List[GridAxis] = []

        # 处理纵向轴线
        for x_key, lines in vertical_groups.items():
            # 找到这组线的最小Y和最大Y
            ys = []
            for line_data in lines:
                ys.append(line_data["start_y"])
                ys.append(line_data["end_y"])

            if not ys:
                continue

            min_y, max_y = min(ys), max(ys)
            # 计算平均 X 坐标
            avg_x = sum(
                line_data["start_x"] + line_data["end_x"] for line_data in lines
            ) / (2 * len(lines))

            # 忽略太短的轴线 (例如小于 2米)
            if abs(max_y - min_y) < 2000:
                continue

            axis = GridAxis(
                label="?",
                start_point=(avg_x, min_y),
                end_point=(avg_x, max_y),
                is_vertical=True,
                coordinate=avg_x,
            )
            temp_axes.append(axis)

        # 处理横向轴线
        for y_key, lines in horizontal_groups.items():
            xs = []
            for line_data in lines:
                xs.append(line_data["start_x"])
                xs.append(line_data["end_x"])

            if not xs:
                continue

            min_x, max_x = min(xs), max(xs)
            avg_y = sum(
                line_data["start_y"] + line_data["end_y"] for line_data in lines
            ) / (2 * len(lines))

            if abs(max_x - min_x) < 2000:
                continue

            axis = GridAxis(
                label="?",
                start_point=(min_x, avg_y),
                end_point=(max_x, avg_y),
                is_vertical=False,
                coordinate=avg_y,
            )
            temp_axes.append(axis)

        self.logger.info("合并后得到 %d 条逻辑轴线，正在匹配轴号...", len(temp_axes))

        # 4. 匹配轴号 (寻找端点附近的文本)
        # 搜索半径 (例如 5000mm，涵盖轴号圈的大小)
        SEARCH_RADIUS = 5000.0

        matched_count = 0
        for axis in temp_axes:
            # 寻找距离起点或终点最近的文本
            best_label = None
            min_dist = float("inf")

            # 检查所有文本
            for text in self.raw_texts:
                try:
                    tx = float(text["x"])
                    ty = float(text["y"])
                except ValueError:
                    continue

                content = text["content"].strip()

                # 过滤掉非轴号的文本 (简单的长度过滤，轴号通常很短)
                if len(content) > 8:
                    continue

                # 计算到起点的距离
                d1 = math.sqrt(
                    (tx - axis.start_point[0]) ** 2 + (ty - axis.start_point[1]) ** 2
                )
                # 计算到终点的距离
                d2 = math.sqrt(
                    (tx - axis.end_point[0]) ** 2 + (ty - axis.end_point[1]) ** 2
                )

                dist = min(d1, d2)

                if dist < SEARCH_RADIUS and dist < min_dist:
                    min_dist = dist
                    best_label = content

            if best_label:
                axis.label = best_label
                matched_count += 1

        # 5. 保存结果 (按坐标排序)
        self.axes = temp_axes
        self.logger.info(
            "分析完成: 识别出 %d 条轴线，其中 %d 条成功匹配到轴号。",
            len(self.axes),
            matched_count,
        )

    def print_grid_info(self):
        """打印轴网信息（通过日志输出表格形式）"""
        logger = logging.getLogger(__name__)

        logger.info("\n%s", "=" * 30)
        logger.info("      建筑轴网信息表")
        logger.info("%s", "=" * 30)

        logger.info("\n[纵向轴线 (X定位)] 共 %d 条", len(self.x_axes))
        logger.info("%s", f"{'轴号':<8} {'X坐标':<12} {'范围 (Y1 -> Y2)'}")
        logger.info("%s", "-" * 40)
        for axis in self.x_axes:
            y_range = f"{axis.start_point[1]:.1f} -> {axis.end_point[1]:.1f}"
            logger.info("%s", f"{axis.label:<8} {axis.coordinate:<12.4f} {y_range}")

        logger.info("\n[横向轴线 (Y定位)] 共 %d 条", len(self.y_axes))
        logger.info("%s", f"{'轴号':<8} {'Y坐标':<12} {'范围 (X1 -> X2)'}")
        logger.info("%s", "-" * 40)
        for axis in self.y_axes:
            x_range = f"{axis.start_point[0]:.1f} -> {axis.end_point[0]:.1f}"
            logger.info("%s", f"{axis.label:<8} {axis.coordinate:<12.4f} {x_range}")
        logger.info("%s\n", "=" * 30)


def main():
    input_file = "input/2025-11-28_国家会议中心二期主体轴网图.dxf"

    try:
        # 使用项目统一的日志配置；与 dxf_extractor __main__ 区域保持一致思路
        setup_logger(
            log_level=logging.INFO,
            log_file="./logs/process_grid.log",
            filemode="w",
        )

        grid = GridNetwork()
        logger = logging.getLogger(__name__)

        # 注意：这里最好传入轴线所在的图层关键字，例如 ['DOTE', 'AXIS', 'S-GRID']
        # 如果不传，会尝试分析所有线条，可能会有杂线干扰
        # 建议先运行一次看图层统计，然后填入这里
        logger.info("开始从 DXF 构建轴网: %s", input_file)
        grid.load_from_dxf(input_file, axis_layer_keywords=None)

        logger.info("轴网解析完成，开始输出轴网信息表")
        grid.print_grid_info()
        logger.info("轴网信息表输出完成")

        # 保存轴网信息为 JSON
        json_output = os.path.join("output", "grid_axes.json")
        grid.save_to_json(json_output)

    except Exception as e:
        logging.getLogger(__name__).error("发生错误: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
