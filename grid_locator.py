import csv
import json
import logging
import os
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "需要安装 PyYAML 才能解析 config.yaml，请执行 `pip install pyyaml`"
    ) from exc

from dxf_extractor import DXFExtractor
from logging_config import setup_logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
PRIVATE_CONFIG_PATH = os.path.join(BASE_DIR, "private.yaml")


def _load_yaml(path: str, *, required: bool = False) -> Dict[str, Any]:
    if not os.path.exists(path):
        if required:
            raise FileNotFoundError(f"配置文件不存在: {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _deep_update(target: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)  # type: ignore[index]
        else:
            target[key] = value
    return target


def load_config(
    path: str = CONFIG_PATH, private_path: str = PRIVATE_CONFIG_PATH
) -> Dict[str, Any]:
    base_cfg = _load_yaml(path, required=True)
    private_cfg = _load_yaml(private_path)
    if private_cfg:
        base_cfg = _deep_update(base_cfg, private_cfg)
    return base_cfg


def resolve_path(path_value: Optional[str]) -> Optional[str]:
    if not path_value:
        return None
    if os.path.isabs(path_value):
        return os.path.normpath(path_value)
    return os.path.normpath(os.path.join(BASE_DIR, path_value))


def parse_log_level(level_name: Optional[str], default: int = logging.INFO) -> int:
    if not level_name:
        return default
    return getattr(logging, str(level_name).upper(), default)


class AxisGrid:
    """根据轴网 JSON 计算任意实体的轴位信息"""

    def __init__(self, grid_source: Any):
        if isinstance(grid_source, str):
            if not os.path.exists(grid_source):
                raise FileNotFoundError(f"轴网 JSON 文件不存在: {grid_source}")
            with open(grid_source, "r", encoding="utf-8") as f:
                grid_data = json.load(f)
        else:
            grid_data = grid_source or {}

        self.x_axes = sorted(grid_data.get("x_axes", []), key=lambda a: a["coordinate"])
        self.y_axes = sorted(grid_data.get("y_axes", []), key=lambda a: a["coordinate"])

    @classmethod
    def from_file(cls, grid_json_path: str) -> "AxisGrid":
        return cls(grid_json_path)

    @classmethod
    def load_grid(cls, grid_json: str, logger: logging.Logger) -> "AxisGrid":
        grid = cls.from_file(grid_json)
        logger.info(
            "载入轴网数据: X轴 %d 条, Y轴 %d 条",
            len(grid.x_axes),
            len(grid.y_axes),
        )
        return grid

    @classmethod
    def locate_texts_on_grid(
        cls,
        dxf_path: str,
        grid_json: str,
        output_csv: str,
        logger: logging.Logger,
    ) -> None:
        texts = extract_texts(dxf_path, logger)
        grid = cls.load_grid(grid_json, logger)

        results: List[Dict[str, Any]] = []
        for text in texts:
            try:
                x = float(text["x"])
                y = float(text["y"])
            except (KeyError, ValueError, TypeError):
                logger.debug("跳过无法解析坐标的文字: %s", text)
                continue

            location = grid.locate_entity(
                {"type": "text", "content": text.get("content"), "x": x, "y": y}
            )
            results.append(
                {
                    "content": text.get("content", "").strip(),
                    "x": f"{x:.4f}",
                    "y": f"{y:.4f}",
                    **location,
                }
            )

        if not results:
            logger.warning("未生成任何文字定位结果")
            return

        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        fieldnames = [
            "content",
            "x",
            "y",
            "nearest_x_axis",
            "nearest_y_axis",
            "x_span_start",
            "x_span_end",
            "y_span_start",
            "y_span_end",
        ]

        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        logger.info("已输出 %d 条文字的轴网定位: %s", len(results), output_csv)

    @staticmethod
    def _nearest_axis(
        axes: List[Dict[str, Any]], coord: float
    ) -> Optional[Dict[str, Any]]:
        if not axes:
            return None
        return min(axes, key=lambda axis: abs(axis["coordinate"] - coord))

    @staticmethod
    def _span(
        axes: List[Dict[str, Any]], coord: float
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        if not axes:
            return None, None
        previous = None
        for axis in axes:
            if coord < axis["coordinate"]:
                return previous, axis
            previous = axis
        return previous, None

    def locate_point(self, x: float, y: float) -> Dict[str, Optional[str]]:
        vx_prev, vx_next = self._span(self.x_axes, x)
        vy_prev, vy_next = self._span(self.y_axes, y)
        nearest_x = self._nearest_axis(self.x_axes, x)
        nearest_y = self._nearest_axis(self.y_axes, y)

        def axis_label(axis: Optional[Dict[str, Any]]) -> Optional[str]:
            return axis.get("label") if axis else None

        return {
            "nearest_x_axis": axis_label(nearest_x),
            "nearest_y_axis": axis_label(nearest_y),
            "x_span_start": axis_label(vx_prev),
            "x_span_end": axis_label(vx_next),
            "y_span_start": axis_label(vy_prev),
            "y_span_end": axis_label(vy_next),
        }

    def locate_entity(self, entity: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """根据实体的空间信息返回轴网定位，目前支持文字（x,y)."""

        if "x" in entity and "y" in entity:
            try:
                x = float(entity["x"])
                y = float(entity["y"])
                return self.locate_point(x, y)
            except (TypeError, ValueError):
                pass

        # 预留：可在此扩展矩形/圆等类型
        raise ValueError("无法根据实体数据推断坐标，请确认包含 x/y 或实现其他形状解析")

    @classmethod
    def locate_line_spaces(
        cls,
        dxf_path: str,
        grid_json: str,
        logger: logging.Logger,
        *,
        min_lines: int = 4,
        tolerance: float = 1e-3,
    ) -> Dict[str, List[Dict[str, Any]]]:
        grid = cls.load_grid(grid_json, logger)
        extractor = DXFExtractor(dxf_path)
        extractor.extract(
            {
                "extract_text": False,
                "extract_lines": True,
                "extract_rects": False,
                "extract_circles": False,
            }
        )
        lines = extractor.get_lines()
        if not lines:
            logger.warning("DXF 中未找到线条实体")
            return {"closed_spaces": [], "open_lines": []}

        return grid._locate_line_spaces(
            lines, logger, min_lines=min_lines, tolerance=tolerance
        )

    @classmethod
    def locate_spaces_from_dxf(
        cls,
        dxf_path: str,
        grid_json: str,
        logger: logging.Logger,
        *,
        min_lines: int = 4,
        tolerance: float = 1e-3,
    ) -> Dict[str, List[Dict[str, Any]]]:
        return cls.locate_line_spaces(
            dxf_path,
            grid_json,
            logger,
            min_lines=min_lines,
            tolerance=tolerance,
        )

    def _locate_line_spaces(
        self,
        lines: List[Dict[str, Any]],
        logger: logging.Logger,
        *,
        min_lines: int,
        tolerance: float,
    ) -> Dict[str, List[Dict[str, Any]]]:
        line_geoms: List[Dict[str, Any]] = []
        point_to_lines: Dict[Tuple[float, float], List[int]] = defaultdict(list)
        point_coords: Dict[Tuple[float, float], Tuple[float, float]] = {}

        for raw_index, line in enumerate(lines):
            try:
                sx = float(line["start_x"])
                sy = float(line["start_y"])
                ex = float(line["end_x"])
                ey = float(line["end_y"])
            except (KeyError, TypeError, ValueError):
                logger.debug("跳过无效线条实体: %s", line)
                continue

            p1 = self._normalize_point(sx, sy, tolerance)
            p2 = self._normalize_point(ex, ey, tolerance)
            point_to_lines[p1].append(len(line_geoms))
            point_to_lines[p2].append(len(line_geoms))
            point_coords.setdefault(p1, (sx, sy))
            point_coords.setdefault(p2, (ex, ey))

            midpoint = ((sx + ex) / 2.0, (sy + ey) / 2.0)
            line_geoms.append(
                {
                    "nodes": (p1, p2),
                    "midpoint": midpoint,
                    "start": (sx, sy),
                    "end": (ex, ey),
                    "layer": line.get("layer"),
                    "raw_index": raw_index,
                }
            )

        if not line_geoms:
            return {"closed_spaces": [], "open_lines": []}

        closed_spaces: List[Dict[str, Any]] = []
        open_lines: List[Dict[str, Any]] = []
        visited: Set[int] = set()

        for idx in range(len(line_geoms)):
            if idx in visited:
                continue

            component_lines: Set[int] = set()
            component_nodes: Set[Tuple[float, float]] = set()
            queue = deque([idx])

            while queue:
                line_idx = queue.popleft()
                if line_idx in component_lines:
                    continue
                component_lines.add(line_idx)
                node_a, node_b = line_geoms[line_idx]["nodes"]
                component_nodes.update((node_a, node_b))
                for neighbor in point_to_lines[node_a]:
                    if neighbor not in component_lines:
                        queue.append(neighbor)
                for neighbor in point_to_lines[node_b]:
                    if neighbor not in component_lines:
                        queue.append(neighbor)

            visited.update(component_lines)

            node_degree: Dict[Tuple[float, float], int] = defaultdict(int)
            for line_idx in component_lines:
                node_a, node_b = line_geoms[line_idx]["nodes"]
                node_degree[node_a] += 1
                node_degree[node_b] += 1

            is_closed = (
                len(component_lines) >= min_lines
                and len(component_nodes) >= min_lines
                and all(degree == 2 for degree in node_degree.values())
            )

            if is_closed:
                centroid_x = sum(
                    point_coords[node][0] for node in component_nodes
                ) / len(component_nodes)
                centroid_y = sum(
                    point_coords[node][1] for node in component_nodes
                ) / len(component_nodes)
                location = self.locate_point(centroid_x, centroid_y)
                closed_spaces.append(
                    {
                        "line_count": len(component_lines),
                        "node_count": len(component_nodes),
                        "center_x": f"{centroid_x:.4f}",
                        "center_y": f"{centroid_y:.4f}",
                        **location,
                    }
                )
            else:
                for line_idx in component_lines:
                    midpoint = line_geoms[line_idx]["midpoint"]
                    location = self.locate_point(midpoint[0], midpoint[1])
                    open_lines.append(
                        {
                            "line_index": line_geoms[line_idx]["raw_index"],
                            "layer": line_geoms[line_idx]["layer"],
                            "mid_x": f"{midpoint[0]:.4f}",
                            "mid_y": f"{midpoint[1]:.4f}",
                            **location,
                        }
                    )

        logger.info(
            "闭合空间检测完成: 闭合空间 %d 个, 非闭合线段 %d 条",
            len(closed_spaces),
            len(open_lines),
        )
        return {"closed_spaces": closed_spaces, "open_lines": open_lines}

    @staticmethod
    def _normalize_point(x: float, y: float, tolerance: float) -> Tuple[float, float]:
        if tolerance <= 0:
            raise ValueError("tolerance 必须大于 0")
        snap = 1.0 / tolerance
        return (round(x * snap) / snap, round(y * snap) / snap)


def extract_texts(dxf_path: str, logger: logging.Logger) -> List[Dict[str, Any]]:
    extractor = DXFExtractor(dxf_path)
    extractor.extract(
        {
            "extract_text": True,
            "extract_lines": False,
            "extract_rects": False,
            "extract_circles": False,
        }
    )
    texts = extractor.get_texts()
    logger.info("共提取 %d 条文字元素", len(texts))
    return texts


def main() -> None:
    config = load_config()
    locator_cfg = config.get("grid_locator", {})
    log_cfg = locator_cfg.get("log", {})

    log_level = parse_log_level(log_cfg.get("level"), default=logging.INFO)
    log_file = resolve_path(log_cfg.get("file")) or os.path.join(
        BASE_DIR, "logs", "grid_locator.log"
    )
    filemode = log_cfg.get("filemode", "w")

    setup_logger(log_level=log_level, log_file=log_file, filemode=filemode)
    logger = logging.getLogger(__name__)

    dxf_path = resolve_path(locator_cfg.get("dxf_file"))
    grid_json = resolve_path(locator_cfg.get("grid_json"))
    output_csv = resolve_path(locator_cfg.get("output_csv"))

    if not dxf_path or not os.path.exists(dxf_path):
        raise FileNotFoundError("配置中的 dxf_file 不存在，请检查 config.yaml")
    if not grid_json or not os.path.exists(grid_json):
        raise FileNotFoundError("配置中的 grid_json 不存在，请先运行 process_grid")
    if not output_csv:
        output_csv = os.path.join(BASE_DIR, "output", "text_positions.csv")

    logger.info("开始处理 DXF 文字定位: %s", dxf_path)
    AxisGrid.locate_texts_on_grid(dxf_path, grid_json, output_csv, logger)
    logger.info("文字定位流程结束")

    space_cfg = locator_cfg.get("space_detection", {})
    if space_cfg.get("enabled", True):
        min_lines = int(space_cfg.get("min_lines", 4))
        tolerance = float(space_cfg.get("tolerance", 1e-3))
        logger.info(
            "开始闭合空间检测: 最少线段=%d, 坐标容差=%s",
            min_lines,
            tolerance,
        )
        try:
            spaces_result = AxisGrid.locate_line_spaces(
                dxf_path,
                grid_json,
                logger,
                min_lines=min_lines,
                tolerance=tolerance,
            )
            closed_spaces = spaces_result.get("closed_spaces", [])
            open_lines = spaces_result.get("open_lines", [])
            logger.info(
                "闭合空间检测结束: 闭合空间=%d, 非闭合线段=%d",
                len(closed_spaces),
                len(open_lines),
            )
        except Exception:
            logger.exception("闭合空间检测失败")

    logger.info("grid_locator 脚本执行完毕")


if __name__ == "__main__":
    main()
