"""
DWG 转 DXF 转换工具

将 dwg 目录下的所有 DWG 文件转换为 DXF 格式并保存到 dxf 目录。
需要 AutoCAD 支持。
"""

import sys
import logging
from pathlib import Path
from logging_config import setup_logger


def convert_dwg_to_dxf(dwg_dir="dwg", dxf_dir="dxf"):
    """
    将 DWG 文件批量转换为 DXF 格式

    Args:
        dwg_dir: 包含 DWG 文件的源目录
        dxf_dir: 保存 DXF 文件的目标目录

    Returns:
        转换成功的文件数量
    """
    logger = logging.getLogger(__name__)

    # 确保目录存在
    dwg_path = Path(dwg_dir)
    dxf_path = Path(dxf_dir)

    if not dwg_path.exists():
        logger.error("DWG 目录不存在: %s", dwg_path.absolute())
        return 0

    # 创建输出目录
    dxf_path.mkdir(exist_ok=True)
    logger.info("输出目录: %s", dxf_path.absolute())

    # 查找所有 DWG 文件
    dwg_files = list(dwg_path.glob("*.dwg"))
    if not dwg_files:
        logger.warning("在 %s 目录下没有找到 DWG 文件", dwg_path)
        return 0

    logger.info("找到 %d 个 DWG 文件", len(dwg_files))

    # 导入 AutoCAD 相关模块
    try:
        import win32com.client
    except ImportError:
        logger.error("未安装 pywin32，请运行: pip install pywin32")
        return 0

    # 连接 AutoCAD
    acad = None
    # 尝试多个可能的 AutoCAD 版本
    autocad_versions = [
        "AutoCAD.Application.24",  # AutoCAD 2024
        "AutoCAD.Application.23",  # AutoCAD 2023
        "AutoCAD.Application.22",  # AutoCAD 2022
        "AutoCAD.Application",  # 通用版本
    ]

    for version in autocad_versions:
        try:
            acad = win32com.client.Dispatch(version)
            acad.Visible = False  # 后台运行
            logger.info("成功连接到 AutoCAD (使用: %s)", version)
            break
        except Exception:
            continue

    if acad is None:
        logger.error("无法连接到 AutoCAD")
        logger.error("请确保 AutoCAD 已安装并正确注册")
        logger.error("尝试过的版本: %s", ", ".join(autocad_versions))
        logger.error("")
        logger.error("*** 重要提示 ***")
        logger.error("如果 AutoCAD 已安装但仍然连接失败，请尝试：")
        logger.error("1. 以管理员身份运行 VS Code 或命令提示符")
        logger.error("2. 或者以管理员身份运行此脚本")
        logger.error("   右键点击 PowerShell/CMD -> '以管理员身份运行'")
        logger.error("   然后执行: python convert_dwg_to_dxf.py")
        return 0

    success_count = 0
    failed_files = []

    # 转换每个文件
    for dwg_file in dwg_files:
        try:
            # 构建输出文件路径（不包含扩展名，让 AutoCAD 自动添加）
            dxf_file_stem = dwg_file.stem
            dxf_file = dxf_path / (dxf_file_stem + ".dxf")

            logger.info("转换: %s -> %s", dwg_file.name, dxf_file.name)

            # 打开 DWG 文件
            # 使用绝对路径，并设置为只读模式
            dwg_fullpath = str(dwg_file.absolute())

            # Open 参数: (FileName, [ReadOnly])
            # ReadOnly = True 以只读模式打开
            doc = acad.Documents.Open(dwg_fullpath, True)

            # 等待文档完全加载
            import time

            time.sleep(1)

            # 保存为 DXF
            dxf_fullpath = str(dxf_file.absolute())

            # 删除已存在的文件（如果有）
            if dxf_file.exists():
                dxf_file.unlink()

            # 使用 DXFOUT 命令导出 DXF
            # 这会弹出保存对话框，但能保证正确转换
            cmd = '_DXFOUT "' + dxf_fullpath + '" 16 \n'

            # 发送命令，增加重试机制
            retry_count = 3
            for attempt in range(retry_count):
                try:
                    doc.SendCommand(cmd)
                    break
                except Exception as send_error:
                    if attempt < retry_count - 1:
                        logger.warning(
                            "发送命令失败 (尝试 %d/%d): %s",
                            attempt + 1,
                            retry_count,
                            str(send_error),
                        )
                        time.sleep(1)
                    else:
                        raise

            # 等待命令完成（增加等待时间）
            time.sleep(3)

            # 关闭文档
            doc.Close(False)

            logger.info("[SUCCESS] 转换成功: %s", dwg_file.name)
            success_count += 1

        except Exception as e:
            logger.error("[FAILED] 转换失败 %s: %s", dwg_file.name, str(e))
            failed_files.append(dwg_file.name)

            # 尝试关闭可能打开的文档
            try:
                if "doc" in locals() and doc is not None:
                    doc.Close(False)
            except Exception:
                pass
            continue

    # 输出总结
    print("\n" + "=" * 70)
    print("转换完成")
    print("=" * 70)
    print(f"成功: {success_count}/{len(dwg_files)}")

    if failed_files:
        print(f"\n失败的文件 ({len(failed_files)}):")
        for filename in failed_files:
            print(f"  - {filename}")

    return success_count


def main():
    """主函数"""
    # 设置日志
    setup_logger(
        log_level=logging.INFO,
        log_file="./logs/convert_dwg_to_dxf.log",
        filemode="w",
    )

    print("=" * 70)
    print("DWG 转 DXF 批量转换工具")
    print("=" * 70)

    # 获取命令行参数
    dwg_dir = sys.argv[1] if len(sys.argv) > 1 else "dwg"
    dxf_dir = sys.argv[2] if len(sys.argv) > 2 else "dxf"

    print(f"\n源目录: {dwg_dir}")
    print(f"目标目录: {dxf_dir}")
    print("-" * 70)

    # 执行转换
    count = convert_dwg_to_dxf(dwg_dir, dxf_dir)

    if count > 0:
        print(f"\n[SUCCESS] 成功转换 {count} 个文件")
        return 0
    else:
        print("\n[FAILED] 没有文件被转换")
        return 1


if __name__ == "__main__":
    sys.exit(main())
