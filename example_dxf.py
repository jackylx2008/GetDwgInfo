"""
DXF 提取器使用示例

演示如何使用 dxf_extractor.py 从 DXF 文件中提取元素
"""

import logging
from dxf_extractor import DXFExtractor


def example_basic_usage():
    """示例 1: 基本用法"""
    print("\n" + "=" * 70)
    print("示例 1: 基本用法 - 提取所有元素")
    print("=" * 70 + "\n")

    # 创建提取器
    extractor = DXFExtractor()

    # 提取 DXF 文件
    try:
        elements = extractor.extract_from_file("input/test.dxf")

        print("提取结果:")
        print(f"  文本: {len(elements['texts'])} 个")
        print(f"  线条: {len(elements['lines'])} 个")
        print(f"  矩形: {len(elements['rects'])} 个")
        print(f"  圆形: {len(elements['circles'])} 个")
        print(f"  多段线: {len(elements['polylines'])} 个")

        # 保存到 CSV
        extractor.save_to_csv("output/example_all_elements.csv")
        print("\n✓ 已保存到 output/example_all_elements.csv")

    except FileNotFoundError:
        print("⚠ 文件 input/test.dxf 不存在")
    except Exception as e:
        print(f"✗ 提取失败: {e}")


def example_text_only():
    """示例 2: 只提取文本"""
    print("\n" + "=" * 70)
    print("示例 2: 只提取文本元素")
    print("=" * 70 + "\n")

    extractor = DXFExtractor()

    # 自定义配置 - 只提取文本
    config = {
        "extract_text": True,
        "extract_lines": False,
        "extract_rects": False,
        "extract_circles": False,
    }

    try:
        elements = extractor.extract_from_file("input/test.dxf", config)

        print("提取的文本元素:")
        for i, text in enumerate(elements["texts"][:5], 1):
            print(f'  {i}. "{text["content"]}" at ({text["x"]:.2f}, {text["y"]:.2f})')

        if len(elements["texts"]) > 5:
            print(f"  ... 还有 {len(elements['texts']) - 5} 个文本")

        extractor.save_to_csv("output/example_texts_only.csv")
        print("\n✓ 已保存到 output/example_texts_only.csv")

    except FileNotFoundError:
        print("⚠ 文件 input/test.dxf 不存在")
    except Exception as e:
        print(f"✗ 提取失败: {e}")


def example_filter_by_layer():
    """示例 3: 按图层过滤元素"""
    print("\n" + "=" * 70)
    print("示例 3: 按图层过滤元素")
    print("=" * 70 + "\n")

    extractor = DXFExtractor()

    try:
        elements = extractor.extract_from_file("input/test.dxf")

        # 统计各图层的文本数量
        layer_counts = {}
        for text in elements["texts"]:
            layer = text["layer"]
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        print("各图层的文本数量:")
        for layer, count in sorted(layer_counts.items(), key=lambda x: -x[1])[:5]:
            print(f"  {layer}: {count} 个")

        # 提取特定图层的文本
        target_layer = list(layer_counts.keys())[0] if layer_counts else ""
        if target_layer:
            filtered_texts = [
                text for text in elements["texts"] if text["layer"] == target_layer
            ]
            print(f"\n图层 '{target_layer}' 的文本: {len(filtered_texts)} 个")

    except FileNotFoundError:
        print("⚠ 文件 input/test.dxf 不存在")
    except Exception as e:
        print(f"✗ 提取失败: {e}")


def example_analyze_geometry():
    """示例 4: 几何分析"""
    print("\n" + "=" * 70)
    print("示例 4: 几何分析 - 计算图形边界")
    print("=" * 70 + "\n")

    extractor = DXFExtractor()

    try:
        elements = extractor.extract_from_file("input/test.dxf")

        # 计算所有元素的边界框
        all_x = []
        all_y = []

        # 收集文本坐标
        for text in elements["texts"]:
            all_x.append(text["x"])
            all_y.append(text["y"])

        # 收集线条坐标
        for line in elements["lines"]:
            all_x.extend([line["start_x"], line["end_x"]])
            all_y.extend([line["start_y"], line["end_y"]])

        # 收集圆心坐标
        for circle in elements["circles"]:
            all_x.append(circle["center_x"])
            all_y.append(circle["center_y"])

        if all_x and all_y:
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)

            print("图纸边界:")
            print(f"  X 范围: {min_x:.2f} 到 {max_x:.2f} (宽度: {max_x - min_x:.2f})")
            print(f"  Y 范围: {min_y:.2f} 到 {max_y:.2f} (高度: {max_y - min_y:.2f})")
            print(f"  中心点: ({(min_x + max_x) / 2:.2f}, {(min_y + max_y) / 2:.2f})")

    except FileNotFoundError:
        print("⚠ 文件 input/test.dxf 不存在")
    except Exception as e:
        print(f"✗ 提取失败: {e}")


def example_export_summary():
    """示例 5: 导出统计摘要"""
    print("\n" + "=" * 70)
    print("示例 5: 导出统计摘要")
    print("=" * 70 + "\n")

    extractor = DXFExtractor()

    try:
        elements = extractor.extract_from_file("input/test.dxf")

        # 准备统计数据
        summary = {
            "总元素数": (
                len(elements["texts"])
                + len(elements["lines"])
                + len(elements["rects"])
                + len(elements["circles"])
            ),
            "文本数量": len(elements["texts"]),
            "线条数量": len(elements["lines"]),
            "矩形数量": len(elements["rects"]),
            "圆形数量": len(elements["circles"]),
            "多段线数量": len(elements["polylines"]),
        }

        # 图层统计
        all_layers = set()
        for elem_list in [
            elements["texts"],
            elements["lines"],
            elements["rects"],
            elements["circles"],
        ]:
            for elem in elem_list:
                all_layers.add(elem.get("layer", ""))

        summary["图层数量"] = len(all_layers)

        # 打印摘要
        print("DXF 文件统计摘要:")
        for key, value in summary.items():
            print(f"  {key}: {value}")

        # 保存完整数据
        extractor.save_to_csv("output/example_summary.csv")
        print("\n✓ 完整数据已保存到 output/example_summary.csv")

    except FileNotFoundError:
        print("⚠ 文件 input/test.dxf 不存在")
    except Exception as e:
        print(f"✗ 提取失败: {e}")


def main():
    """运行所有示例"""
    # 配置日志
    logging.basicConfig(
        level=logging.WARNING,  # 只显示警告和错误
        format="%(levelname)s - %(message)s",
    )

    print("=" * 70)
    print("DXF 提取器使用示例")
    print("=" * 70)

    # 运行所有示例
    example_basic_usage()
    example_text_only()
    example_filter_by_layer()
    example_analyze_geometry()
    example_export_summary()

    print("\n" + "=" * 70)
    print("所有示例已完成!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
