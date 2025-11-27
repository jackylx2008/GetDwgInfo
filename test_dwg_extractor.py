"""
测试 dwg_extractor.py 模块。

验证 DWG 元素提取功能是否正常工作。
"""

import logging
import sys
from dwg_extractor import DWGExtractor
from logging_config import setup_logger


def test_dwg_extractor():
    """测试 DWG 提取器"""
    print("=" * 70)
    print("测试 DWG 元素提取模块")
    print("=" * 70)

    # 设置日志
    setup_logger(
        log_level=logging.INFO,
        log_file="./logs/test_dwg_extractor.log",
        filemode="w",
    )

    # 测试文件路径
    dwg_file = "input/test.dwg"

    print(f"\n测试文件: {dwg_file}")
    print("-" * 70)

    # 创建提取器
    print("\n[1/5] 创建 DWGExtractor 实例...")
    try:
        extractor = DWGExtractor()
        print("✓ DWGExtractor 创建成功")
    except Exception as e:
        print(f"✗ 创建失败: {e}")
        return False

    # 测试连接和提取
    print("\n[2/5] 连接 AutoCAD 并打开文件...")
    try:
        elements_dict = extractor.extract_from_file(
            dwg_file, extract_config={}  # 使用默认配置
        )
        print("✓ 文件提取成功")
    except FileNotFoundError as e:
        print(f"✗ 文件不存在: {e}")
        print(f"\n请确保文件 '{dwg_file}' 存在")
        return False
    except RuntimeError as e:
        print(f"✗ AutoCAD 连接失败: {e}")
        print("\n可能的原因:")
        print("  1. AutoCAD 未安装")
        print("  2. 无法启动 AutoCAD")
        print("  3. COM 接口问题")
        return False
    except Exception as e:
        print(f"✗ 提取失败: {e}")
        import traceback

        traceback.print_exc()
        return False

    # 检查提取结果
    print("\n[3/5] 检查提取的元素...")
    try:
        texts = elements_dict.get("texts", [])
        lines = elements_dict.get("lines", [])
        rects = elements_dict.get("rects", [])
        circles = elements_dict.get("circles", [])
        polylines = elements_dict.get("polylines", [])

        print(f"✓ 文本元素: {len(texts)} 个")
        print(f"✓ 线条元素: {len(lines)} 个")
        print(f"✓ 矩形元素: {len(rects)} 个")
        print(f"✓ 圆形元素: {len(circles)} 个")
        print(f"✓ 多段线: {len(polylines)} 个")

        total = len(texts) + len(lines) + len(rects) + len(circles) + len(polylines)
        print(f"\n总计: {total} 个元素")

        if total == 0:
            print("\n⚠ 警告: 未提取到任何元素")
            print("  可能原因:")
            print("  1. DWG 文件为空")
            print("  2. 元素类型不支持")
            print("  3. 元素在布局空间而非模型空间")
    except Exception as e:
        print(f"✗ 检查结果失败: {e}")
        return False

    # 显示示例数据
    print("\n[4/5] 显示示例数据...")
    try:
        if texts:
            print("\n文本元素示例（前3个）:")
            for i, text in enumerate(texts[:3], 1):
                content = text.get("content", "")
                x = text.get("x", 0)
                y = text.get("y", 0)
                layer = text.get("layer", "")
                print(f'  {i}. "{content}" at ({x:.2f}, {y:.2f}) [图层: {layer}]')

        if lines:
            print("\n线条元素示例（前3个）:")
            for i, line in enumerate(lines[:3], 1):
                sx = line.get("start_x", 0)
                sy = line.get("start_y", 0)
                ex = line.get("end_x", 0)
                ey = line.get("end_y", 0)
                layer = line.get("layer", "")
                print(
                    f"  {i}. ({sx:.2f}, {sy:.2f}) → ({ex:.2f}, {ey:.2f}) [图层: {layer}]"
                )

        if circles:
            print("\n圆形元素示例（前3个）:")
            for i, circle in enumerate(circles[:3], 1):
                cx = circle.get("center_x", 0)
                cy = circle.get("center_y", 0)
                r = circle.get("radius", 0)
                layer = circle.get("layer", "")
                print(f"  {i}. 圆心({cx:.2f}, {cy:.2f}) 半径{r:.2f} [图层: {layer}]")

        if rects:
            print("\n矩形元素示例（前3个）:")
            for i, rect in enumerate(rects[:3], 1):
                x = rect.get("x", 0)
                y = rect.get("y", 0)
                w = rect.get("width", 0)
                h = rect.get("height", 0)
                layer = rect.get("layer", "")
                print(
                    f"  {i}. 位置({x:.2f}, {y:.2f}) 大小{w:.2f}×{h:.2f} [图层: {layer}]"
                )
    except Exception as e:
        print(f"✗ 显示数据失败: {e}")
        return False

    # 测试 get_all_elements 方法
    print("\n[5/5] 测试 get_all_elements() 方法...")
    try:
        all_elements = extractor.get_all_elements()
        print(f"✓ get_all_elements() 返回 {len(all_elements)} 个元素")

        # 验证扁平列表的正确性
        expected_total = len(texts) + len(lines) + len(rects) + len(circles)
        if len(all_elements) == expected_total:
            print("✓ 元素数量匹配")
        else:
            print(f"⚠ 元素数量不匹配: 期望 {expected_total}, 实际 {len(all_elements)}")
    except Exception as e:
        print(f"✗ 测试 get_all_elements() 失败: {e}")
        return False

    # 测试成功
    print("\n" + "=" * 70)
    print("✓ 所有测试通过!")
    print("=" * 70)
    print("\ndwg_extractor.py 模块工作正常。")
    return True


def test_custom_config():
    """测试自定义提取配置"""
    print("\n" + "=" * 70)
    print("测试自定义提取配置")
    print("=" * 70)

    setup_logger(log_level=logging.INFO)
    extractor = DWGExtractor()
    dwg_file = "input/test.dwg"

    # 只提取文本
    print("\n测试配置: 仅提取文本元素")
    print("-" * 70)

    config = {
        "extract_text": True,
        "extract_lines": False,
        "extract_rects": False,
        "extract_circles": False,
    }

    try:
        elements_dict = extractor.extract_from_file(dwg_file, config)

        texts = len(elements_dict.get("texts", []))
        lines = len(elements_dict.get("lines", []))
        rects = len(elements_dict.get("rects", []))
        circles = len(elements_dict.get("circles", []))

        print(f"文本元素: {texts} 个")
        print(f"线条元素: {lines} 个")
        print(f"矩形元素: {rects} 个")
        print(f"圆形元素: {circles} 个")

        if texts > 0 and lines == 0 and rects == 0 and circles == 0:
            print("\n✓ 配置生效，仅提取了文本元素")
            return True
        elif texts == 0:
            print("\n⚠ 警告: 未提取到文本元素（可能文件中没有文本）")
            return True
        else:
            print("\n⚠ 警告: 提取了其他类型的元素（配置可能未生效）")
            return False

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DWG 元素提取器测试套件")
    print("=" * 70)

    # 运行基本测试
    test1_result = test_dwg_extractor()

    # 运行配置测试
    if test1_result:
        test2_result = test_custom_config()
    else:
        test2_result = False
        print("\n跳过配置测试（基本测试失败）")

    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"基本功能测试: {'✓ 通过' if test1_result else '✗ 失败'}")
    print(f"配置功能测试: {'✓ 通过' if test2_result else '✗ 失败'}")
    print("=" * 70)

    sys.exit(0 if (test1_result and test2_result) else 1)
