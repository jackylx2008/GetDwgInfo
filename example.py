"""
GetDwgInfo 快速使用示例。

演示如何使用各个模块提取和分析 DWG 文件。
"""

import logging
from dwg_extractor import DWGExtractor
from database import CSVDatabase
from analyzer import ElementAnalyzer
from logging_config import setup_logger


def example_basic_extraction():
    """基本提取示例"""
    print("\n" + "=" * 60)
    print("示例 1: 基本 DWG 元素提取")
    print("=" * 60)

    # 设置日志
    logger = setup_logger(log_level=logging.INFO)

    # 创建提取器
    extractor = DWGExtractor()

    # 提取 DWG 文件（请替换为您的文件路径）
    dwg_file = "input/test.dwg"

    try:
        elements_dict = extractor.extract_from_file(dwg_file)

        # 显示统计信息
        print(f"\n提取结果:")
        print(f"  文本元素: {len(elements_dict['texts'])} 个")
        print(f"  线条元素: {len(elements_dict['lines'])} 个")
        print(f"  矩形元素: {len(elements_dict['rects'])} 个")
        print(f"  圆形元素: {len(elements_dict['circles'])} 个")

        # 显示前几个文本元素
        if elements_dict["texts"]:
            print(f"\n前 3 个文本元素:")
            for i, text in enumerate(elements_dict["texts"][:3], 1):
                print(
                    f"  {i}. \"{text['content']}\" at ({text['x']:.2f}, {text['y']:.2f})"
                )

    except Exception as e:
        print(f"\n错误: {e}")


def example_save_to_csv():
    """保存到 CSV 示例"""
    print("\n" + "=" * 60)
    print("示例 2: 提取并保存到 CSV")
    print("=" * 60)

    # 设置日志
    logger = setup_logger(log_level=logging.INFO)

    # 创建提取器和数据库
    extractor = DWGExtractor()
    db = CSVDatabase(output_dir="./output")

    dwg_file = "input/test.dwg"

    try:
        # 提取元素
        elements_dict = extractor.extract_from_file(dwg_file)
        all_elements = extractor.get_all_elements()

        # 保存到 CSV
        csv_file = db.save_elements(all_elements, "example_elements.csv")
        print(f"\n✓ 数据已保存到: {csv_file}")
        print("  可以使用 Excel 打开查看")

    except Exception as e:
        print(f"\n错误: {e}")


def example_full_analysis():
    """完整分析示例"""
    print("\n" + "=" * 60)
    print("示例 3: 完整提取和关联分析")
    print("=" * 60)

    # 设置日志
    logger = setup_logger(log_level=logging.INFO)

    # 创建所需对象
    extractor = DWGExtractor()
    db = CSVDatabase(output_dir="./output")
    analyzer = ElementAnalyzer(max_distance=100.0, alignment_tolerance=5.0)

    dwg_file = "input/test.dwg"

    try:
        # 1. 提取元素
        print("\n步骤 1: 提取元素...")
        elements_dict = extractor.extract_from_file(dwg_file)
        all_elements = extractor.get_all_elements()

        if not all_elements:
            print("  未找到任何元素")
            return

        # 2. 保存元素
        print("\n步骤 2: 保存元素数据...")
        elements_file = db.save_elements(all_elements, "example_elements.csv")
        print(f"  保存到: {elements_file}")

        # 3. 分析关联关系
        print("\n步骤 3: 分析元素关联...")
        relationships = analyzer.analyze_elements(all_elements)

        if relationships:
            # 保存关联关系
            rel_file = db.save_relationships(relationships, "example_relationships.csv")
            print(f"  保存到: {rel_file}")

            # 生成报告
            report = analyzer.generate_report()
            print(f"\n{report}")
        else:
            print("  未发现关联关系")

    except Exception as e:
        print(f"\n错误: {e}")


def example_custom_extraction():
    """自定义提取示例"""
    print("\n" + "=" * 60)
    print("示例 4: 自定义提取配置")
    print("=" * 60)

    # 设置日志
    logger = setup_logger(log_level=logging.INFO)

    extractor = DWGExtractor()
    dwg_file = "input/test.dwg"

    # 只提取文本元素
    config = {
        "extract_text": True,
        "extract_lines": False,
        "extract_rects": False,
        "extract_circles": False,
    }

    try:
        print("\n配置: 仅提取文本元素")
        elements_dict = extractor.extract_from_file(dwg_file, config)

        print(f"\n提取结果:")
        print(f"  文本元素: {len(elements_dict['texts'])} 个")
        print(f"  其他元素: 0 个（已禁用）")

    except Exception as e:
        print(f"\n错误: {e}")


if __name__ == "__main__":
    print("\nGetDwgInfo 使用示例")
    print("=" * 60)
    print("请确保:")
    print("1. AutoCAD 已安装")
    print("2. input/test.dwg 文件存在")
    print("3. 已运行 pip install -r requirements.txt")

    # 运行示例（取消注释您想运行的示例）

    # example_basic_extraction()
    # example_save_to_csv()
    # example_full_analysis()
    # example_custom_extraction()

    print("\n" + "=" * 60)
    print("取消注释上面的函数调用来运行示例")
    print("或直接使用: python main.py input/test.dwg")
    print("=" * 60)
