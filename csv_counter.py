import csv
import logging
import os
import glob
from typing import Any, Dict, Optional, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "需要安装 PyYAML 才能解析 config.yaml，请执行 `pip install pyyaml`"
    ) from exc

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


def scan_csv_folder(
    folder: str,
    column: str,
    value: str,
    *,
    delimiter: str,
    encoding: str,
    recursive: bool,
    logger: logging.Logger,
) -> Tuple[int, int, int]:
    pattern = "**/*.csv" if recursive else "*.csv"
    csv_files = glob.glob(os.path.join(folder, pattern), recursive=recursive)
    if not csv_files:
        logger.warning("目录下未找到 CSV 文件: %s", folder)
        return 0, 0, 0

    total_rows = 0
    matched_rows = 0
    processed_files = 0

    for csv_path in csv_files:
        try:
            with open(csv_path, "r", newline="", encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                if not reader.fieldnames or column not in reader.fieldnames:
                    logger.warning("文件缺少目标列，已跳过: %s", csv_path)
                    continue
                processed_files += 1
                for row in reader:
                    total_rows += 1
                    if str(row.get(column, "")) == value:
                        matched_rows += 1
        except FileNotFoundError:
            logger.warning("文件不存在，已跳过: %s", csv_path)
        except Exception:
            logger.exception("读取 CSV 失败: %s", csv_path)

    return processed_files, total_rows, matched_rows


def main() -> None:
    config = load_config()
    counter_cfg = config.get("csv_counter", {})
    log_cfg = counter_cfg.get("log", {})

    log_level = parse_log_level(log_cfg.get("level"), default=logging.INFO)
    log_file = resolve_path(log_cfg.get("file")) or os.path.join(
        BASE_DIR, "logs", "csv_counter.log"
    )
    filemode = log_cfg.get("filemode", "w")

    setup_logger(log_level=log_level, log_file=log_file, filemode=filemode)
    logger = logging.getLogger(__name__)

    folder = resolve_path(counter_cfg.get("folder"))
    if not folder:
        folder = resolve_path(config.get("paths", {}).get("output_dir"))
    if not folder or not os.path.isdir(folder):
        raise FileNotFoundError(
            "未找到有效的 CSV 目录，请检查 config.yaml/csv_counter.folder"
        )

    column = counter_cfg.get("column")
    value = counter_cfg.get("value")
    if not column or value is None:
        raise ValueError("csv_counter.column 与 csv_counter.value 均需配置")

    delimiter = counter_cfg.get("delimiter", ",")
    encoding = counter_cfg.get("encoding", "utf-8")
    recursive = bool(counter_cfg.get("recursive", False))

    logger.info("读取配置: column=%s, value=%s", column, value)
    logger.info(
        "开始统计 CSV: 目录=%s, 列=%s, 目标值=%s, 递归=%s",
        folder,
        column,
        value,
        recursive,
    )

    files, rows, matched = scan_csv_folder(
        folder,
        column,
        str(value),
        delimiter=delimiter,
        encoding=encoding,
        recursive=recursive,
        logger=logger,
    )

    logger.info("统计完成: 文件数=%d, 行数=%d, 匹配行数=%d", files, rows, matched)


if __name__ == "__main__":
    main()
