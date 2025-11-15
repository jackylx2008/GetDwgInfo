"""
测试 pyautocad 连接脚本。

用于验证 pyautocad 是否正确安装，以及能否连接到 AutoCAD。
"""

import sys


def test_pyautocad():
    """测试 pyautocad 是否可用"""
    print("=" * 60)
    print("测试 pyautocad 连接")
    print("=" * 60)

    # 测试导入
    print("\n1. 测试导入 pyautocad...")
    try:
        from pyautocad import Autocad, APoint

        print("   ✓ pyautocad 导入成功")
    except ImportError as e:
        print(f"   ✗ pyautocad 导入失败: {e}")
        print("\n请运行: pip install pyautocad pywin32")
        return False

    # 测试连接 AutoCAD
    print("\n2. 测试连接 AutoCAD...")
    try:
        acad = Autocad(create_if_not_exists=True)
        print("   ✓ 成功连接到 AutoCAD")

        # 获取版本信息
        try:
            version = acad.app.Version
            print(f"   AutoCAD 版本: {version}")
        except:
            print("   无法获取 AutoCAD 版本")

        # 获取当前文档信息
        try:
            doc = acad.doc
            if doc:
                doc_name = doc.Name
                print(f"   当前文档: {doc_name}")
            else:
                print("   没有打开的文档")
        except:
            print("   无法获取当前文档信息")

        print("\n✓ 所有测试通过!")
        print("\npyautocad 已正确配置，可以使用 GetDwgInfo 工具。")
        return True

    except Exception as e:
        print(f"   ✗ 连接 AutoCAD 失败: {e}")
        print("\n可能的原因:")
        print("  1. AutoCAD 未安装")
        print("  2. AutoCAD 版本不兼容")
        print("  3. COM 接口被禁用")
        print("  4. 权限不足（尝试以管理员身份运行）")
        return False


if __name__ == "__main__":
    success = test_pyautocad()
    sys.exit(0 if success else 1)
