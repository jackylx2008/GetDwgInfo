"""
GetDwgInfo 主程序。

整合 DWG 元素提取、数据库保存和关联分析功能。
"""

import argparse
import logging
import os
import sys
import yaml

from dwg_extractor import DWGExtractor
from database import CSVDatabase
from analyzer import ElementAnalyzer
from logging_config import setup_logger


def load_config(config_path: str = "config.yaml") -> dict:
    """
    加载配置文件。

    :param config_path: 配置文件路径
    :return: 配置字典
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return {}


def main():
    """主程序入口"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="DWG 元素提取与关联分析工具")
    parser.add_argument("dwg_file", help="DWG 文件路径")
    parser.add_argument(
        "-c", "--config", default="config.yaml", help="配置文件路径 (默认: config.yaml)"
    )
    parser.add_argument("-o", "--output", help="输出文件名前缀 (可选)")
    parser.add_argument("--no-analysis", action="store_true", help="不进行关联分析")
    parser.add_argument("--text-only", action="store_true", help="仅提取文本元素")
    parser.add_argument("--lines-only", action="store_true", help="仅提取线条元素")
    args = parser.parse_args()

    # 加载配置
    config = load_config(args.config)

    # 设置日志
    log_level_str = config.get("log_level", "INFO")
    log_level = getattr(logging, log_level_str, logging.INFO)
    log_file = config.get("log_file", "./logs/app.log")
    logger = setup_logger(log_level=log_level, log_file=log_file)

    logger.info("=" * 60)
    logger.info("GetDwgInfo - DWG 元素提取与分析工具")
    logger.info("=" * 60)

    # 检查文件是否存在
    if not os.path.exists(args.dwg_file):
        logger.error("DWG 文件不存在: %s", args.dwg_file)
        sys.exit(1)

    try:
        # 配置提取选项
        extract_config = {
            "extract_text": True,
            "extract_lines": True,
            "extract_rects": True,
            "extract_circles": True,
        }

        if args.text_only:
            extract_config = {
                "extract_text": True,
                "extract_lines": False,
                "extract_rects": False,
                "extract_circles": False,
            }
        elif args.lines_only:
            extract_config = {
                "extract_text": False,
                "extract_lines": True,
                "extract_rects": False,
                "extract_circles": False,
            }
        else:
            # 从配置文件读取
            dwg_config = config.get("dwg", {})
            extract_config.update(
                {
                    "extract_text": dwg_config.get("extract_text", True),
                    "extract_lines": dwg_config.get("extract_lines", True),
                    "extract_rects": dwg_config.get("extract_rects", True),
                    "extract_circles": dwg_config.get("extract_circles", True),
                }
            )

        # 步骤 1: 提取 DWG 元素
        logger.info("步骤 1: 提取 DWG 元素")
        extractor = DWGExtractor()
        elements_dict = extractor.extract_from_file(args.dwg_file, extract_config)

        # 获取所有元素的扁平列表
        all_elements = extractor.get_all_elements()

        if not all_elements:
            logger.warning("未提取到任何元素")
            sys.exit(0)

        # 步骤 2: 保存元素到数据库
        logger.info("步骤 2: 保存元素数据")
        paths_config = config.get("paths", {})
        output_dir = paths_config.get("output_dir", "./output")
        db = CSVDatabase(output_dir=output_dir)

        # 生成输出文件名
        base_name = os.path.splitext(os.path.basename(args.dwg_file))[0]
        if args.output:
            elements_filename = f"{args.output}_elements.csv"
        else:
            elements_filename = f"{base_name}_elements.csv"

        elements_file = db.save_elements(all_elements, elements_filename)
        logger.info("元素数据已保存到: %s", elements_file)

        # 步骤 3: 分析元素关联关系 (可选)
        if not args.no_analysis and len(all_elements) > 1:
            logger.info("步骤 3: 分析元素关联关系")

            analysis_config = config.get("analysis", {})
            analyzer = ElementAnalyzer(
                max_distance=analysis_config.get("max_distance", 100.0),
                alignment_tolerance=analysis_config.get("alignment_tolerance", 5.0),
            )

            relationships = analyzer.analyze_elements(all_elements)

            if relationships:
                # 保存关联关系
                if args.output:
                    rel_filename = f"{args.output}_relationships.csv"
                else:
                    rel_filename = f"{base_name}_relationships.csv"

                rel_file = db.save_relationships(relationships, rel_filename)
                logger.info("关联关系已保存到: %s", rel_file)

                # 生成并显示报告
                report = analyzer.generate_report()
                logger.info("\n%s", report)
            else:
                logger.info("未发现元素关联关系")

        logger.info("=" * 60)
        logger.info("处理完成!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error("处理过程中出错: %s", str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
