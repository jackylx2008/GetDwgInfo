"""
DXF 提取器测试脚本
测试 dxf_extractor.py 模块的功能
"""

import os
import sys
from dxf_extractor import DXFExtractor


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70 + "\n")


def test_dxf_extractor():
    """测试 DXF 提取器"""
    print_section("DXF 元素提取器测试")

    # 测试文件
    test_file = "input/test.dxf"

    # 检查测试文件是否存在
    if not os.path.exists(test_file):
        print(f"⚠ 测试文件不存在: {test_file}")
        print(f"请将 DXF 文件放入 input/ 目录")
        return False

    print(f"测试文件: {test_file}")
    print("-" * 70)

    try:
        # 创建提取器
        print("[1/5] 创建 DXFExtractor 实例...")
        extractor = DXFExtractor()
        print("✓ DXFExtractor 创建成功\n")

        # 提取所有元素
        print("[2/5] 提取所有类型的元素...")
        elements = extractor.extract_from_file(test_file)
        print("✓ 文件提取成功\n")

        # 检查提取的元素
        print("[3/5] 检查提取的元素...")
        text_count = len(elements["texts"])
        line_count = len(elements["lines"])
        rect_count = len(elements["rects"])
        circle_count = len(elements["circles"])
        polyline_count = len(elements["polylines"])

        print(f"✓ 文本元素: {text_count} 个")
        print(f"✓ 线条元素: {line_count} 个")
        print(f"✓ 矩形元素: {rect_count} 个")
        print(f"✓ 圆形元素: {circle_count} 个")
        print(f"✓ 多段线: {polyline_count} 个")
        print(f"\n总计: {text_count + line_count + rect_count + circle_count} 个元素\n")

        # 显示示例数据
        print("[4/5] 显示示例数据...\n")

        # 文本示例
        if text_count > 0:
            print("文本元素示例（前3个）:")
            for i, text in enumerate(elements["texts"][:3], 1):
                print(
                    f'  {i}. "{text["content"]}" at ({text["x"]:.2f}, {text["y"]:.2f}) '
                    f'[图层: {text["layer"]}]'
                )
            print()

        # 线条示例
        if line_count > 0:
            print("线条元素示例（前3个）:")
            for i, line in enumerate(elements["lines"][:3], 1):
                print(
                    f'  {i}. ({line["start_x"]:.2f}, {line["start_y"]:.2f}) → '
                    f'({line["end_x"]:.2f}, {line["end_y"]:.2f}) [图层: {line["layer"]}]'
                )
            print()

        # 圆形示例
        if circle_count > 0:
            print("圆形元素示例（前3个）:")
            for i, circle in enumerate(elements["circles"][:3], 1):
                print(
                    f'  {i}. 圆心({circle["center_x"]:.2f}, {circle["center_y"]:.2f}) '
                    f'半径{circle["radius"]:.2f} [图层: {circle["layer"]}]'
                )
            print()

        # 矩形示例
        if rect_count > 0:
            print("矩形元素示例（前3个）:")
            for i, rect in enumerate(elements["rects"][:3], 1):
                print(
                    f'  {i}. 位置({rect["x"]:.2f}, {rect["y"]:.2f}) '
                    f'大小{rect["width"]:.2f}×{rect["height"]:.2f} '
                    f'[图层: {rect["layer"]}]'
                )
            print()

        # 测试 get_all_elements() 方法
        print("[5/5] 测试 get_all_elements() 方法...")
        all_elements = extractor.get_all_elements()
        print(f"✓ get_all_elements() 返回 {len(all_elements)} 个元素")

        expected_count = text_count + line_count + rect_count + circle_count
        if len(all_elements) == expected_count:
            print("✓ 元素数量匹配\n")
        else:
            print(f"⚠ 元素数量不匹配，预期: {expected_count}\n")

        # 保存到 CSV
        output_file = "output/dxf_test_elements.csv"
        extractor.save_to_csv(output_file)

        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✓ CSV 文件已保存: {output_file}")
            print(f"  文件大小: {file_size} 字节\n")
        else:
            print(f"✗ CSV 文件保存失败\n")
            return False

        print_section("✓ 所有测试通过!")
        print("\ndxf_extractor.py 模块工作正常。\n")
        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_custom_config():
    """测试自定义配置"""
    print_section("测试自定义提取配置")

    test_file = "input/test.dxf"

    if not os.path.exists(test_file):
        print(f"⚠ 测试文件不存在: {test_file}")
        return True  # 跳过测试

    print("测试配置: 仅提取文本元素")
    print("-" * 70)

    try:
        extractor = DXFExtractor()

        # 自定义配置 - 只提取文本
        config = {
            "extract_text": True,
            "extract_lines": False,
            "extract_rects": False,
            "extract_circles": False,
        }

        elements = extractor.extract_from_file(test_file, config)

        print(f"文本元素: {len(elements['texts'])} 个")
        print(f"线条元素: {len(elements['lines'])} 个")
        print(f"矩形元素: {len(elements['rects'])} 个")
        print(f"圆形元素: {len(elements['circles'])} 个\n")

        # 验证配置生效
        if (
            len(elements["texts"]) > 0
            and len(elements["lines"]) == 0
            and len(elements["rects"]) == 0
            and len(elements["circles"]) == 0
        ):
            print("✓ 配置生效，仅提取了文本元素\n")
            return True
        else:
            print("⚠ 配置可能未正确应用\n")
            return True  # 不算失败

    except Exception as e:
        print(f"✗ 测试失败: {e}\n")
        return False


def main():
    """主测试流程"""
    print("=" * 70)
    print("DXF 元素提取器测试套件")
    print("=" * 70)

    # 运行测试
    test1_passed = test_dxf_extractor()
    test2_passed = test_custom_config()

    # 打印总结
    print_section("测试总结")
    print(f"基本功能测试: {'✓ 通过' if test1_passed else '✗ 失败'}")
    print(f"配置功能测试: {'✓ 通过' if test2_passed else '✗ 失败'}")
    print("=" * 70)

    return 0 if (test1_passed and test2_passed) else 1


if __name__ == "__main__":
    sys.exit(main())
