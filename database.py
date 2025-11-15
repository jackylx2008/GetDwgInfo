"""
数据库管理模块。

负责将提取的元素数据保存到 CSV 文件，并提供数据读取功能。
"""

import csv
import logging
import os
from typing import List, Dict, Any
from datetime import datetime


class CSVDatabase:
    """CSV 数据库管理类"""

    def __init__(self, output_dir: str = "./output"):
        """
        初始化数据库管理器。

        :param output_dir: 输出目录路径
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def save_elements(
        self, elements: List[Dict[str, Any]], filename: str = None
    ) -> str:
        """
        保存元素数据到 CSV 文件。

        :param elements: 元素数据列表
        :param filename: 输出文件名，默认自动生成
        :return: 保存的文件路径
        """
        if not elements:
            self.logger.warning("没有元素数据需要保存")
            return ""

        # 生成文件名
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"elements_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        try:
            # 获取所有可能的字段名
            fieldnames = set()
            for elem in elements:
                fieldnames.update(elem.keys())
            fieldnames = sorted(list(fieldnames))

            # 写入 CSV 文件
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(elements)

            self.logger.info("成功保存 %d 个元素到 %s", len(elements), filepath)
            return filepath

        except Exception as e:
            self.logger.error("保存元素数据失败: %s", str(e))
            raise

    def save_relationships(
        self, relationships: List[Dict[str, Any]], filename: str = None
    ) -> str:
        """
        保存关联关系数据到 CSV 文件。

        :param relationships: 关联关系数据列表
        :param filename: 输出文件名，默认自动生成
        :return: 保存的文件路径
        """
        if not relationships:
            self.logger.warning("没有关联关系数据需要保存")
            return ""

        # 生成文件名
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relationships_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        try:
            # 获取所有可能的字段名
            fieldnames = set()
            for rel in relationships:
                fieldnames.update(rel.keys())
            fieldnames = sorted(list(fieldnames))

            # 写入 CSV 文件
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(relationships)

            self.logger.info(
                "成功保存 %d 个关联关系到 %s", len(relationships), filepath
            )
            return filepath

        except Exception as e:
            self.logger.error("保存关联关系数据失败: %s", str(e))
            raise

    def load_elements(self, filepath: str) -> List[Dict[str, Any]]:
        """
        从 CSV 文件加载元素数据。

        :param filepath: CSV 文件路径
        :return: 元素数据列表
        """
        try:
            elements = []
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 转换数值类型
                    converted_row = self._convert_types(row)
                    elements.append(converted_row)

            self.logger.info("成功加载 %d 个元素从 %s", len(elements), filepath)
            return elements

        except Exception as e:
            self.logger.error("加载元素数据失败: %s", str(e))
            raise

    def load_relationships(self, filepath: str) -> List[Dict[str, Any]]:
        """
        从 CSV 文件加载关联关系数据。

        :param filepath: CSV 文件路径
        :return: 关联关系数据列表
        """
        try:
            relationships = []
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 转换数值类型
                    converted_row = self._convert_types(row)
                    relationships.append(converted_row)

            self.logger.info(
                "成功加载 %d 个关联关系从 %s", len(relationships), filepath
            )
            return relationships

        except Exception as e:
            self.logger.error("加载关联关系数据失败: %s", str(e))
            raise

    def _convert_types(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        转换 CSV 行中的数据类型。

        :param row: CSV 行数据
        :return: 转换后的数据
        """
        converted = {}
        for key, value in row.items():
            if value == "":
                converted[key] = None
            elif value.lower() == "true":
                converted[key] = True
            elif value.lower() == "false":
                converted[key] = False
            else:
                try:
                    # 尝试转换为整数
                    converted[key] = int(value)
                except ValueError:
                    try:
                        # 尝试转换为浮点数
                        converted[key] = float(value)
                    except ValueError:
                        # 保持为字符串
                        converted[key] = value
        return converted

    def get_all_csv_files(self) -> List[str]:
        """
        获取输出目录中的所有 CSV 文件。

        :return: CSV 文件路径列表
        """
        csv_files = []
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                if filename.endswith(".csv"):
                    csv_files.append(os.path.join(self.output_dir, filename))
        return csv_files
