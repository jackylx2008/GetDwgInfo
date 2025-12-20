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
import json
from pathlib import Path


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
    """DXF 文件元素提取器

    一个实例对应一个 DXF 文件。构造时打开文件并初始化元素容器。
    """

    def __init__(self, dxf_path: Optional[str] = None):
        """初始化提取器

        Args:
            dxf_path: 可选，DXF 文件路径。传入时会立即打开文件。
        """
        self.logger = logging.getLogger(__name__)
        self.doc = None
        self.msp = None
        self._dxf_path: Optional[str] = None
        self.elements: Dict[str, List[Dict[str, Any]]] = {
            "texts": [],
            "lines": [],
            "rects": [],
            "circles": [],
            "polylines": [],
        }

        if dxf_path:
            self.open(dxf_path)

    def _round_coord(self, value: float) -> float:
        """保留4位小数，绝对值小于0.0001则为0.0"""
        if abs(value) < 0.0001:
            return 0.0
        return float(f"{value:.4f}")

    def open(self, dxf_path: str) -> None:
        """打开 DXF 文件并准备模型空间"""
        if not os.path.exists(dxf_path):
            raise FileNotFoundError(f"DXF 文件不存在: {dxf_path}")
        self._dxf_path = os.path.abspath(dxf_path)
        try:
            self.doc = ezdxf.readfile(self._dxf_path)  # type: ignore
            self.msp = self.doc.modelspace()
            self.logger.info("成功打开文件: %s", self._dxf_path)
        except Exception as e:
            self.doc = None
            self.msp = None
            raise RuntimeError(f"无法打开 DXF 文件: {str(e)}")

    def extract(
        self, extract_config: Optional[Dict[str, bool]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """从已打开的 DXF 文件中提取元素"""
        if self.msp is None:
            raise RuntimeError("DXF 文件尚未打开，请先调用 open() 或在构造函数传入路径")

        # 默认配置
        if extract_config is None:
            extract_config = {
                "extract_text": True,
                "extract_lines": True,
                "extract_rects": True,
                "extract_circles": True,
            }

        try:
            # 重置元素列表
            self.elements = {
                "texts": [],
                "lines": [],
                "rects": [],
                "circles": [],
                "polylines": [],
            }

            # 统计实体数量
            entity_count = len(list(self.msp))
            self.logger.info("模型空间中共有 %d 个实体", entity_count)

            # 遍历所有实体
            for entity in self.msp:
                entity_type = "Unknown"  # 初始化默认值
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
                        "提取实体时出错: %s, 错误: %s", entity_type, str(e)
                    )
                    continue

            self.logger.info(
                "提取完成 - 文本: %d, 线条: %d, 矩形: %d, 圆形: %d",
                len(self.elements["texts"]),
                len(self.elements["lines"]),
                len(self.elements["rects"]),
                len(self.elements["circles"]),
            )

            return self.elements

        except Exception as e:
            self.logger.error("读取 DXF 文件失败: %s", str(e))
            raise

    # 输出方法：按元素类型返回
    def get_texts(self) -> List[Dict[str, Any]]:
        return self.elements.get("texts", [])

    def get_lines(self) -> List[Dict[str, Any]]:
        return self.elements.get("lines", [])

    def get_rects(self) -> List[Dict[str, Any]]:
        return self.elements.get("rects", [])

    def get_circles(self) -> List[Dict[str, Any]]:
        return self.elements.get("circles", [])

    def get_polylines(self) -> List[Dict[str, Any]]:
        return self.elements.get("polylines", [])

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
                text_elem.x = self._round_coord(insert_point[0])
                text_elem.y = self._round_coord(insert_point[1])
                text_elem.z = self._round_coord(
                    insert_point[2] if len(insert_point) > 2 else 0.0
                )

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
            self.logger.warning("提取文本元素失败: %s", str(e))

    def _extract_line(self, entity):
        """提取线条元素"""
        try:
            line_elem = LineElement()

            # 获取起点和终点
            if hasattr(entity.dxf, "start"):
                start = entity.dxf.start
                line_elem.start_x = self._round_coord(start[0])
                line_elem.start_y = self._round_coord(start[1])
                line_elem.start_z = self._round_coord(
                    start[2] if len(start) > 2 else 0.0
                )

            if hasattr(entity.dxf, "end"):
                end = entity.dxf.end
                line_elem.end_x = self._round_coord(end[0])
                line_elem.end_y = self._round_coord(end[1])
                line_elem.end_z = self._round_coord(end[2] if len(end) > 2 else 0.0)

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
            self.logger.warning("提取线条元素失败: %s", str(e))

    def _extract_polyline(self, entity):
        """提取多段线元素，识别矩形"""
        try:
            # 获取顶点
            vertices = []
            if hasattr(entity, "get_points"):
                # LWPOLYLINE - get_points() 返回 'format' 格式的点
                # 需要指定格式，默认 'xyb' 包含 x, y, bulge
                points = list(entity.get_points("xy"))  # 只获取 x, y
                vertices = [
                    (self._round_coord(p[0]), self._round_coord(p[1]), 0.0)
                    for p in points
                ]
            elif hasattr(entity, "points"):
                # POLYLINE
                points = list(entity.points())
                vertices = [
                    (
                        self._round_coord(p[0]),
                        self._round_coord(p[1]),
                        self._round_coord(p[2] if len(p) > 2 else 0.0),
                    )
                    for p in points
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
                    rect_elem.x = self._round_coord(min_x)
                    rect_elem.y = self._round_coord(min_y)
                    rect_elem.width = self._round_coord(max_x - min_x)
                    rect_elem.height = self._round_coord(max_y - min_y)
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
            self.logger.warning("提取多段线元素失败: %s", str(e))

    def _extract_circle(self, entity):
        """提取圆形元素"""
        try:
            circle_elem = CircleElement()

            # 获取圆心
            if hasattr(entity.dxf, "center"):
                center = entity.dxf.center
                circle_elem.center_x = self._round_coord(center[0])
                circle_elem.center_y = self._round_coord(center[1])
                circle_elem.center_z = self._round_coord(
                    center[2] if len(center) > 2 else 0.0
                )

            # 获取半径
            circle_elem.radius = self._round_coord(
                entity.dxf.radius if hasattr(entity.dxf, "radius") else 0.0
            )

            # 获取其他属性
            circle_elem.color = entity.dxf.color if hasattr(entity.dxf, "color") else 7
            circle_elem.layer = entity.dxf.layer if hasattr(entity.dxf, "layer") else ""

            self.elements["circles"].append(asdict(circle_elem))

        except Exception as e:
            self.logger.warning("提取圆形元素失败: %s", str(e))

    def get_all_elements(self) -> List[Dict[str, Any]]:
        all_elements = []
        for k, v in self.elements.items():
            type_name = k.rstrip("s")  # 将 texts 转为 text
            for item in v:
                new_item = item.copy()
                new_item["type"] = type_name
                all_elements.append(new_item)
        return all_elements

    def save_to_csv(self, file_path: str) -> None:
        """
        旧接口，准备废弃
        将所有元素保存到一个 CSV 文件
        """
        all_elements = []
        for k, v in self.elements.items():
            type_name = k.rstrip("s")
            for item in v:
                new_item = item.copy()
                new_item["type"] = type_name
                all_elements.append(new_item)
        if not all_elements:
            return
        # 获取所有字段
        fieldnames = set()
        for item in all_elements:
            fieldnames.update(item.keys())
        fieldnames = list(fieldnames)
        # 写入 CSV
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in all_elements:
                writer.writerow(item)

    def _write_csv(
        self, file_path: str, data: List[Dict[str, Any]], type_name: str
    ) -> None:
        """将单一类型元素保存到 CSV 文件"""
        if not data:
            return
        # 获取所有字段
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = list(fieldnames)
        # 写入 CSV
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item)

    def _write_json(self, file_path: str, data: List[Dict[str, Any]]) -> None:
        """将单一类型元素保存到 JSON 文件"""
        if not data:
            return
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_elements(
        self, output_dir: str, format: str = "csv", types: Optional[List[str]] = None
    ):
        """分类导出主方法"""
        type_mapping = {
            "text": "texts",
            "line": "lines",
            "rect": "rects",
            "circle": "circles",
            "polyline": "polylines",
        }
        target_types = types if types else type_mapping.keys()

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)  # 自动创建目录

        for t in target_types:
            data = self.elements.get(type_mapping.get(t, ""), [])
            if not data:
                continue

            file_name = out_path / f"{t}s.{format}"
            if format.lower() == "csv":
                self._write_csv(str(file_name), data, t)
            elif format.lower() == "json":
                self._write_json(str(file_name), data)


# 示例用法
if __name__ == "__main__":
    # 配置日志 (保持不变)
    try:
        from logging_config import setup_logger

        setup_logger(
            log_level=logging.INFO,
            log_file="./logs/dxf_extractor.log",
            filemode="w",
        )
    except ImportError:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    "./logs/dxf_extractor.log", mode="w", encoding="utf-8"
                ),
                logging.StreamHandler(),
            ],
        )

    # 定义输入输出目录
    input_dir = Path("input")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # 获取所有 DXF 文件
    dxf_files = list(input_dir.glob("*.dxf"))

    if not dxf_files:
        print("未在 input 目录下找到 DXF 文件")
    else:
        print(f"找到 {len(dxf_files)} 个 DXF 文件，准备提取文本信息...\n")

        success_count = 0
        fail_count = 0

        for dxf_file in dxf_files:
            print(f"正在处理: {dxf_file.name}")

            try:
                # 1. 创建提取器
                extractor = DXFExtractor(str(dxf_file))

                # 2. 【关键修改】：配置仅提取文本，关闭其他类型以提高效率
                text_only_config = {
                    "extract_text": True,
                    "extract_lines": False,
                    "extract_rects": False,
                    "extract_circles": False,
                }
                elements = extractor.extract(extract_config=text_only_config)

                print(f"  - 提取到文本实体: {len(elements['texts'])} 个")

                # 3. 【关键修改】：使用 save_elements 仅导出文本到 CSV
                # 为每个 DXF 文件创建一个子目录存放结果，或直接存入 output_dir
                # 这里建议为每个文件建个子文件夹，避免多个 DXF 的 texts.csv 互相覆盖
                file_output_path = output_dir / dxf_file.stem
                extractor.save_elements(
                    output_dir=str(file_output_path), format="csv", types=["text"]
                )

                print(f"  [SUCCESS] 文本已保存至: {file_output_path}/texts.csv\n")
                success_count += 1

            except Exception as e:
                print(f"  [FAILED] 提取失败: {e}\n")
                fail_count += 1

        # 输出总结
        print("=" * 50)
        print("处理完成!")
        print(f"成功: {success_count} 个文件")
        print(f"失败: {fail_count} 个文件")
        print("=" * 50)
