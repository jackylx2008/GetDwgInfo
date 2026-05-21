import math
import yaml
import logging
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

# 导入您提供的模块
from dxf_extractor import DXFExtractor
from logging_config import setup_logger


class DXFBatchProcessor:
    """
    DXF 批处理类：执行扫描、提取、匹配并根据距离阈值汇总。
    """

    def __init__(
        self,
        input_folder: Path,
        target_strings: List[str],
        output_file: Path,
        dist_threshold: float = 0.0,
        match_mode: str = "contains",
        recursive: bool = False,
        logger: "Optional[logging.Logger]" = None,
    ):
        """
        初始化处理器。
        :param dist_threshold: 直线距离阈值。若两个匹配项距离小于此值，则视为同一个。
        """
        self.input_folder = input_folder
        self.target_strings = target_strings
        self.output_file = output_file
        self.dist_threshold = dist_threshold
        self.match_mode = match_mode
        self.recursive = recursive
        self.logger = logger or logging.getLogger(__name__)
        self.all_results = []
        self.per_file_count = {}  # 新增

    def _calculate_distance(self, p1: Dict[str, Any], p2: Dict[str, Any]) -> float:
        """计算两个点之间的欧几里得距离 (x, y)"""
        return math.sqrt((p1["x"] - p2["x"]) ** 2 + (p1["y"] - p2["y"]) ** 2)

    def _is_match(self, content: str) -> bool:
        """匹配逻辑判断"""
        if self.match_mode == "strict":
            return any(target == content for target in self.target_strings)
        return any(target in content for target in self.target_strings)

    def _process_file(self, dxf_path: Path):
        """处理单个 DXF 文件，并进行空间去重"""
        try:
            extractor = DXFExtractor(str(dxf_path))
            extractor.extract(extract_config={"extract_text": True})

            raw_texts = extractor.get_texts()

            # 1. 首先提取所有符合关键字条件的文本
            matched_candidates = [
                t for t in raw_texts if self._is_match(t.get("content", ""))
            ]

            # 2. 空间去重逻辑 (Greedy Filtering)
            filtered_in_file = []
            for candidate in matched_candidates:
                is_duplicate = False
                for existing in filtered_in_file:
                    dist = self._calculate_distance(candidate, existing)
                    if dist <= self.dist_threshold:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    detail = candidate.copy()
                    detail["source_file"] = dxf_path.name
                    filtered_in_file.append(detail)

            # 3. 将过滤后的结果加入全局列表
            self.all_results.extend(filtered_in_file)

            if len(filtered_in_file) > 0:
                self.logger.info(
                    f"文件 {dxf_path.name}: 匹配到 {len(matched_candidates)} 处，去重后保留 {len(filtered_in_file)} 条记录"
                )
            self.per_file_count[dxf_path.name] = len(filtered_in_file)  # 新增

        except Exception as e:
            self.logger.error(f"处理文件 {dxf_path.name} 出错: {e}")

    def run(self):
        """启动批处理流程"""
        pattern = "**/*.dxf" if self.recursive else "*.dxf"
        dxf_files = list(self.input_folder.glob(pattern))

        if not dxf_files:
            self.logger.warning(f"目录 {self.input_folder} 下未发现 DXF 文件")
            return

        for dxf_path in dxf_files:
            self._process_file(dxf_path)

        if self.all_results:
            self._save_to_csv()

    def _save_to_csv(self):
        """保存汇总数据"""
        try:
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            fieldnames = [
                "source_file",
                "content",
                "x",
                "y",
                "z",
                "layer",
                "height",
                "rotation",
                "color",
                "style",
            ]
            with open(self.output_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(self.all_results)
            self.logger.info(
                f"汇总成功！保存至: {self.output_file} (总行数: {len(self.all_results)})"
            )
        except Exception as e:
            self.logger.error(f"保存 CSV 失败: {e}")


class DXFLayerTextExtractor:
    """
    DXF 批量提取指定图层文本的类
    """

    def __init__(
        self,
        input_folder: Path,
        target_layers: List[str],
        output_file: Path,
        recursive: bool = False,
        logger: "Optional[logging.Logger]" = None,
    ):
        """
        初始化处理器。
        :param target_layers: 需要提取的图层名称列表
        """
        self.input_folder = input_folder
        self.target_layers = target_layers
        self.output_file = output_file
        self.recursive = recursive
        self.logger = logger or logging.getLogger(__name__)
        self.all_results = []
        self.per_file_count = {}  # 新增

    def _process_file(self, dxf_path: Path):
        """处理单个 DXF 文件，提取指定图层的文本"""
        try:
            extractor = DXFExtractor(str(dxf_path))
            extractor.extract(extract_config={"extract_text": True})

            raw_texts = extractor.get_texts()

            # 只保留在目标图层上的文本
            filtered_texts = [
                t for t in raw_texts if t.get("layer", "") in self.target_layers
            ]

            for text in filtered_texts:
                detail = text.copy()
                detail["source_file"] = dxf_path.name
                self.all_results.append(detail)

            if filtered_texts:
                self.logger.info(
                    f"文件 {dxf_path.name}: 提取到 {len(filtered_texts)} 条目标图层文本"
                )
                self.per_file_count[dxf_path.name] = len(filtered_texts)  # 新增

        except Exception as e:
            self.logger.error(f"处理文件 {dxf_path.name} 出错: {e}")

    def run(self):
        """启动批处理流程"""
        pattern = "**/*.dxf" if self.recursive else "*.dxf"
        dxf_files = list(self.input_folder.glob(pattern))

        if not dxf_files:
            self.logger.warning(f"目录 {self.input_folder} 下未发现 DXF 文件")
            return

        for dxf_path in dxf_files:
            self._process_file(dxf_path)

        if self.all_results:
            self._save_to_csv()

    def _save_to_csv(self):
        """保存汇总数据"""
        try:
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            fieldnames = [
                "source_file",
                "content",
                "x",
                "y",
                "z",
                "layer",
                "height",
                "rotation",
                "color",
                "style",
            ]
            with open(self.output_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(self.all_results)
            self.logger.info(
                f"汇总成功！保存至: {self.output_file} (总行数: {len(self.all_results)})"
            )
        except Exception as e:
            self.logger.error(f"保存 CSV 失败: {e}")


def get_key_word(config_path: str = "config.yaml", logger=None) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)["get_key_word"]
    params = {
        "input_folder": Path(cfg["folder"]),
        "target_strings": cfg["target_strings"],
        "output_file": Path(cfg["output_file"]),
        "dist_threshold": float(100),
        "match_mode": cfg.get("match_mode", "contains"),
        "recursive": cfg.get("recursive", False),
        "logger": logger,
    }
    processor = DXFBatchProcessor(**params)
    processor.run()
    return processor.per_file_count


def get_layer_text(config_path: str = "config.yaml", logger=None) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)["get_layer_text"]
    params = {
        "input_folder": Path(cfg["folder"]),
        "target_layers": cfg["target_layers"],
        "output_file": Path(cfg["output_file"]),
        "recursive": cfg.get("recursive", False),
        "logger": logger,
    }
    extractor = DXFLayerTextExtractor(**params)
    extractor.run()
    return extractor.per_file_count


if __name__ == "__main__":
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    log_file = cfg["get_key_word"]["log"]["file"]
    custom_logger = setup_logger(log_level=logging.INFO, log_file=log_file)

    key_word_counts = get_key_word(logger=custom_logger)
    layer_text_counts = get_layer_text(logger=custom_logger)

    all_files = set(key_word_counts) | set(layer_text_counts)
    summary_rows = []
    for fname in sorted(all_files):
        kw = key_word_counts.get(fname, 0)
        lt = layer_text_counts.get(fname, 0)
        diff = kw - lt
        summary_rows.append([fname, kw, lt, diff])

    # 输出到日志
    for row in summary_rows:
        custom_logger.info(
            f"文件: {row[0]} | 关键字: {row[1]} | 图层: {row[2]} | 差值: {row[3]}"
        )

    with open("output/compare_summary.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["文件名", "关键字数量", "图层数量", "差值"])
        writer.writerows(summary_rows)
