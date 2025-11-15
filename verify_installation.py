"""
最终验证脚本 - 验证 GetDwgInfo 项目的所有核心功能
"""

import os
import sys


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70 + "\n")


def test_imports():
    """测试所有必要的导入"""
    print_section("1. 测试模块导入")

    modules = [
        ("win32com.client", "pywin32"),
        ("yaml", "PyYAML"),
        ("dwg_extractor", "本地模块"),
    ]

    all_ok = True
    for module_name, package_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name:20} - 已安装 ({package_name})")
        except ImportError as e:
            print(f"✗ {module_name:20} - 未找到! 请安装: pip install {package_name}")
            all_ok = False

    return all_ok


def test_autocad_connection():
    """测试 AutoCAD 连接"""
    print_section("2. 测试 AutoCAD 连接")

    try:
        import win32com.client

        progids = [
            "AutoCAD.Application",
            "AutoCAD.Application.24",
            "AutoCAD.Application.23",
            "AutoCAD.Application.22",
            "AutoCAD.Application.21",
            "AutoCAD.Application.20",
        ]

        acad_found = False
        for progid in progids:
            try:
                acad = win32com.client.GetActiveObject(progid)
                print(f"✓ 找到运行中的 AutoCAD: {progid}")
                version = acad.Version
                print(f"  版本: {version}")
                acad_found = True
                break
            except:
                continue

        if not acad_found:
            # 尝试启动新实例
            for progid in progids:
                try:
                    acad = win32com.client.Dispatch(progid)
                    print(f"✓ 成功启动 AutoCAD: {progid}")
                    version = acad.Version
                    print(f"  版本: {version}")
                    # 不退出 AutoCAD,保持运行状态
                    acad_found = True
                    break
                except:
                    continue

        if acad_found:
            print("\n✓ AutoCAD 连接测试通过")
            # 不退出 AutoCAD,让它保持运行状态供后续测试使用
            return True
        else:
            print("\n✗ 无法连接到 AutoCAD")
            print("  请确保 AutoCAD 已安装并可以正常启动")
            return False

    except Exception as e:
        print(f"\n✗ AutoCAD 连接测试失败: {e}")
        return False


def test_dwg_extractor():
    """测试 DWG 提取器"""
    print_section("3. 测试 DWG 提取器")

    try:
        from dwg_extractor import DWGExtractor

        # 创建提取器
        extractor = DWGExtractor()
        print("✓ DWGExtractor 创建成功")

        # 检查测试文件
        test_file = "input/test.dwg"
        if not os.path.exists(test_file):
            print(f"⚠ 测试文件不存在: {test_file}")
            print("  跳过文件提取测试")
            return True

        # 测试提取
        print(f"\n测试提取文件: {test_file}")
        config = {
            "extract_text": True,
            "extract_lines": False,
            "extract_rects": False,
            "extract_circles": False,
        }

        elements = extractor.extract_from_file(test_file, config)

        text_count = len(elements.get("texts", []))
        print(f"✓ 成功提取 {text_count} 个文本元素")

        # 测试 CSV 导出
        output_file = "output/验证测试.csv"
        os.makedirs("output", exist_ok=True)
        extractor.save_to_csv(output_file)

        if os.path.exists(output_file):
            print(f"✓ CSV 文件已导出: {output_file}")
            file_size = os.path.getsize(output_file)
            print(f"  文件大小: {file_size} 字节")
            # 清理测试文件
            os.remove(output_file)
            print(f"  (测试文件已清理)")
        else:
            print(f"✗ CSV 文件未生成")
            return False

        print("\n✓ DWG 提取器测试通过")
        return True

    except Exception as e:
        print(f"\n✗ DWG 提取器测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_file_structure():
    """测试文件结构"""
    print_section("4. 测试项目文件结构")

    required_files = [
        "dwg_extractor.py",
        "requirements.txt",
        "README.md",
        "config.yaml",
        "logging_config.py",
    ]

    optional_files = [
        "test_connection.py",
        "test_dwg_extractor.py",
        "diagnose_autocad.py",
        "example.py",
        "MIGRATION.md",
        "CHANGES.md",
        "UPDATE_SUMMARY.md",
        "QUICKSTART.md",
    ]

    all_ok = True

    print("必需文件:")
    for filename in required_files:
        if os.path.exists(filename):
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} - 缺失!")
            all_ok = False

    print("\n可选文件(文档和测试):")
    for filename in optional_files:
        if os.path.exists(filename):
            print(f"  ✓ {filename}")
        else:
            print(f"  - {filename} - 未找到")

    print("\n必需目录:")
    required_dirs = ["input", "output"]
    for dirname in required_dirs:
        if os.path.exists(dirname):
            print(f"  ✓ {dirname}/")
        else:
            print(f"  ! {dirname}/ - 不存在,将创建")
            os.makedirs(dirname, exist_ok=True)
            print(f"    ✓ 已创建 {dirname}/")

    return all_ok


def test_config():
    """测试配置文件"""
    print_section("5. 测试配置文件")

    try:
        import yaml

        if os.path.exists("config.yaml"):
            with open("config.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            print("✓ config.yaml 加载成功")
            print(f"  配置项: {len(config) if config else 0} 个")

            if config:
                for key, value in config.items():
                    print(f"    - {key}: {value}")

            return True
        else:
            print("⚠ config.yaml 不存在")
            return True  # 配置文件是可选的

    except Exception as e:
        print(f"✗ 配置文件测试失败: {e}")
        return False


def main():
    """主验证流程"""
    print("=" * 70)
    print("GetDwgInfo 项目最终验证")
    print("=" * 70)

    results = {
        "模块导入": test_imports(),
        "AutoCAD 连接": test_autocad_connection(),
        "文件结构": test_file_structure(),
        "配置文件": test_config(),
        "DWG 提取器": test_dwg_extractor(),
    }

    # 打印总结
    print_section("验证总结")

    all_passed = True
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:15} - {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 所有验证通过! 项目已准备就绪。")
        print("\n快速开始:")
        print("  python example.py              # 查看使用示例")
        print("  python test_dwg_extractor.py   # 运行完整测试")
        print("  阅读 QUICKSTART.md 了解更多用法")
    else:
        print("⚠ 部分验证未通过,请检查上述错误信息。")
        print("\n故障排除:")
        print("  1. 确保已安装所有依赖: pip install -r requirements.txt")
        print("  2. 确保 AutoCAD 已安装并激活")
        print("  3. 运行 python diagnose_autocad.py 获取详细诊断")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
