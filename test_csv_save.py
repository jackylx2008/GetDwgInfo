"""简单测试CSV保存功能"""

from dwg_extractor import DWGExtractor

print("创建提取器...")
extractor = DWGExtractor()

print("提取DWG文件...")
config = {
    "extract_text": True,
    "extract_lines": False,
    "extract_rects": False,
    "extract_circles": False,
}

elements = extractor.extract_from_file("input/test.dwg", config)

print(f"提取的文本元素: {len(elements['texts'])} 个")

print("保存到CSV...")
csv_path = extractor.save_to_csv("output/test_elements.csv")

print(f"✓ 已保存到: {csv_path}")

# 验证文件
import os

if os.path.exists(csv_path):
    size = os.path.getsize(csv_path)
    print(f"✓ 文件大小: {size} 字节")

    # 读取前几行
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()[:5]
        print(f"✓ CSV前5行:")
        for line in lines:
            print(f"  {line.strip()}")
else:
    print("✗ 文件未生成!")
