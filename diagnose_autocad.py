"""
AutoCAD COM 诊断工具

检查系统上 AutoCAD 的 COM 注册情况
"""

import sys


def diagnose_autocad_com():
    """诊断 AutoCAD COM 接口"""
    print("=" * 70)
    print("AutoCAD COM 接口诊断")
    print("=" * 70)

    # 1. 检查 win32com 是否可用
    print("\n1. 检查 win32com 模块...")
    try:
        import win32com.client

        print("   ✓ win32com.client 可用")
    except ImportError as e:
        print(f"   ✗ win32com.client 不可用: {e}")
        print("\n   请运行: pip install pywin32")
        return False

    # 2. 尝试列出可能的 AutoCAD ProgID
    print("\n2. 搜索 AutoCAD ProgID...")
    possible_progids = [
        "AutoCAD.Application",
        "AutoCAD.Application.24",  # AutoCAD 2020
        "AutoCAD.Application.23",  # AutoCAD 2019
        "AutoCAD.Application.22",  # AutoCAD 2018
        "AutoCAD.Application.21",  # AutoCAD 2017
        "AutoCAD.Application.20",  # AutoCAD 2016
        "AutoCAD.Application.19",  # AutoCAD 2015
        "AutoCAD.Application.18",  # AutoCAD 2014
    ]

    found_progids = []
    for progid in possible_progids:
        try:
            obj = win32com.client.Dispatch(progid)
            print(f"   ✓ 找到: {progid}")
            try:
                version = obj.Version
                print(f"     版本: {version}")
            except Exception:
                pass
            found_progids.append(progid)
            # 关闭
            try:
                obj.Quit()
            except Exception:
                pass
        except Exception:
            print(f"   ✗ {progid}: 不可用")

    if not found_progids:
        print("\n   ✗ 未找到任何 AutoCAD COM 对象")
        print("\n   可能的原因:")
        print("   - AutoCAD 未安装")
        print("   - AutoCAD 安装损坏")
        print("   - COM 注册失败")
        print("\n   解决方法:")
        print("   1. 确认 AutoCAD 已正确安装")
        print("   2. 以管理员身份运行 AutoCAD 一次")
        print("   3. 重新注册 COM 组件")
        return False

    # 3. 尝试连接到运行中的实例
    print("\n3. 检查运行中的 AutoCAD 实例...")
    for progid in found_progids:
        try:
            acad = win32com.client.GetActiveObject(progid)
            print(f"   ✓ 找到运行中的实例: {progid}")
            try:
                print(f"     文档数量: {acad.Documents.Count}")
            except Exception:
                pass
            break
        except Exception:
            print(f"   - {progid}: 未运行")

    # 4. 测试创建新实例
    print("\n4. 测试启动新 AutoCAD 实例...")
    print("   (这可能需要几秒钟...)")
    try:
        acad = win32com.client.Dispatch(found_progids[0])
        acad.Visible = True
        print("   ✓ 成功启动 AutoCAD")
        print(f"   版本: {acad.Version}")
        print(f"   名称: {acad.Name}")

        # 关闭
        try:
            acad.Quit()
            print("   ✓ 成功关闭 AutoCAD")
        except Exception:
            print("   - 无法自动关闭 AutoCAD，请手动关闭")

        return True

    except Exception as e:
        print(f"   ✗ 启动失败: {e}")
        return False

    print("\n" + "=" * 70)
    print("诊断完成")
    print("=" * 70)


def check_registry():
    """检查注册表中的 AutoCAD 信息"""
    print("\n5. 检查 AutoCAD 注册表信息...")
    try:
        import winreg

        # 检查常见的 AutoCAD 注册表路径
        paths = [
            r"SOFTWARE\Autodesk\AutoCAD",
            r"SOFTWARE\WOW6432Node\Autodesk\AutoCAD",
        ]

        for path in paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                print(f"   ✓ 找到注册表项: {path}")

                # 尝试枚举子键
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        print(f"     - {subkey_name}")
                        i += 1
                    except WindowsError:
                        break

                winreg.CloseKey(key)
            except OSError:
                print(f"   ✗ 未找到: {path}")

    except Exception as e:
        print(f"   ✗ 检查注册表失败: {e}")


if __name__ == "__main__":
    print("\n此工具将诊断系统上的 AutoCAD COM 接口配置\n")

    success = diagnose_autocad_com()

    # 额外检查注册表
    try:
        check_registry()
    except Exception:
        pass

    print("\n" + "=" * 70)
    if success:
        print("✓ AutoCAD COM 接口可用")
        print("\n您可以继续使用 GetDwgInfo 工具")
    else:
        print("✗ AutoCAD COM 接口不可用")
        print("\n请按照上述建议解决问题后再试")
    print("=" * 70)

    sys.exit(0 if success else 1)
