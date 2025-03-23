# chart_tool.py

import csv
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import logging
import math
import argparse
import sys

# 定义日志配置函数
def setup_logging(enable_console: bool):
    """
    配置日志记录。

    :param enable_console: 是否启用控制台日志输出
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # 设置根日志级别为DEBUG

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # 清除现有的处理器，以防止重复日志
    if logger.hasHandlers():
        logger.handlers.clear()

    # 创建文件处理器
    file_handler = logging.FileHandler("chart_generator.log", encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 如果启用控制台，添加流处理器
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

# 自定义异常类
class ChartGeneratorError(Exception):
    """基础异常类，用于图表生成器相关错误"""
    pass

class CSVFormatError(ChartGeneratorError):
    """CSV格式错误"""
    pass

class UnsupportedChartTypeError(ChartGeneratorError):
    """不支持的图表类型错误"""
    pass

class DataConversionError(ChartGeneratorError):
    """数据转换错误"""
    pass

# 基础图表类
class BaseChart(ABC):
    def __init__(
        self,
        title: str,
        data: List[Dict[str, Any]],
        metrics: List[str],
        categories: List[str],
        color_map: Optional[Dict[str, str]] = None,
        categories_field: str = "InnerIP"
    ):
        """
        初始化基础图表。

        :param title: 图表标题
        :param data: 原始数据列表，每个元素为一个字典
        :param metrics: 指标列表（例如 ['Cpu', 'Disk', 'Mem']）
        :param categories: 类别列表（例如 InnerIP 列表）
        :param color_map: 指标到颜色的映射
        :param categories_field: 类别字段名（例如 'InnerIP'）
        """
        self.title = title
        self.data = data
        self.metrics = metrics
        self.categories = categories
        self.color_map = color_map or self._default_color_map()
        self.categories_field = categories_field

    @abstractmethod
    def generate_config(self) -> Dict[str, Any]:
        """
        生成 ECharts 配置。

        :return: ECharts 配置字典
        """
        pass

    def _default_color_map(self) -> Dict[str, str]:
        """
        提供默认的颜色映射。

        :return: 指标到颜色的字典
        """
        default_colors = [
            "#5470C6", "#91CC75", "#EE6666", "#FAC858", 
            "#73C0DE", "#3BA272", "#FC8452", "#9A60B4", "#EA7CCC",
            "#FF7F50", "#87CEFA", "#32CD32", "#BA55D3", "#7B68EE",
            "#00FA9A", "#FFD700", "#FF69B4", "#CD5C5C", "#4B0082"
        ]
        return {metric: default_colors[idx % len(default_colors)] for idx, metric in enumerate(self.metrics)}

# 辅助函数：计算图表的中心位置和半径
def calculate_chart_layout(n: int, cols: int, rows: int, padding_x: float, padding_y: float) -> List[Tuple[float, float, float]]:
    """
    计算每个图表的中心位置和半径。

    :param n: 图表数量
    :param cols: 每行图表数量
    :param rows: 总行数
    :param padding_x: 水平间距（百分比）
    :param padding_y: 垂直间距（百分比）
    :return: 每个图表的 (center_x, center_y, radius)
    """
    layout = []
    chart_width = 100 / cols
    chart_height = 100 / rows
    for idx in range(n):
        row_idx = idx // cols
        col_idx = idx % cols
        center_x = (col_idx + 0.5) * chart_width
        center_y = (row_idx + 0.5) * chart_height
        # 半径设为单元格宽度和高度中的较小值的30%
        radius = min(chart_width, chart_height) * 0.3
        layout.append((center_x, center_y, radius))
    return layout

# 具体图表类
class PieChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        series = []
        num_metrics = len(self.metrics)
        if num_metrics == 0:
            logging.warning("没有可用的指标生成饼图。")
            return {}
        
        # 动态计算网格布局
        cols = math.ceil(math.sqrt(num_metrics))
        rows = math.ceil(num_metrics / cols)
        padding_x = 5  # 水平间距，单位百分比
        padding_y = 5  # 垂直间距，单位百分比

        # 计算布局
        layout = calculate_chart_layout(num_metrics, cols, rows, padding_x, padding_y)
        
        for idx, metric in enumerate(self.metrics):
            try:
                data_for_pie = [{"name": row[self.categories_field], "value": row[metric]} for row in self.data]
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            
            center_x, center_y, radius = layout[idx]
            
            pie_series = {
                "name": metric,
                "type": "pie",
                "radius": f"{radius}%",
                "center": [f"{center_x}%", f"{center_y}%"],
                "label": {
                    "formatter": "{b}: {c} ({d}%)"
                },
                "data": data_for_pie
            }
            series.append(pie_series)
            logging.debug(f"生成饼图系列: {metric}，数据量={len(data_for_pie)}，中心=({center_x}%, {center_y}%)，半径={radius}%")
        
        config = {
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "item"
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
                "data": self.metrics
            },
            "series": series
        }

        logging.info(f"生成饼图配置完成: {self.title}")
        return config

class RoseChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        series = []
        num_metrics = len(self.metrics)
        if num_metrics == 0:
            logging.warning("没有可用的指标生成南丁格尔玫瑰图。")
            return {}
        
        # 动态计算网格布局
        cols = math.ceil(math.sqrt(num_metrics))
        rows = math.ceil(num_metrics / cols)
        padding_x = 5  # 水平间距，单位百分比
        padding_y = 5  # 垂直间距，单位百分比

        # 计算布局
        layout = calculate_chart_layout(num_metrics, cols, rows, padding_x, padding_y)
        
        for idx, metric in enumerate(self.metrics):
            try:
                data_for_rose = [{"name": row[self.categories_field], "value": row[metric]} for row in self.data]
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            
            center_x, center_y, radius = layout[idx]
            
            rose_series = {
                "name": metric,
                "type": "pie",
                "radius": f"{radius * 0.8}%",  # 调整南丁格尔玫瑰图的半径为基础饼图的80%
                "center": [f"{center_x}%", f"{center_y}%"],
                "label": {
                    "formatter": "{b}: {c} ({d}%)"
                },
                "roseType": "radius",
                "data": data_for_rose
            }
            series.append(rose_series)
            logging.debug(f"生成南丁格尔玫瑰图系列: {metric}，数据量={len(data_for_rose)}，中心=({center_x}%, {center_y}%)，半径={radius * 0.8}%")

        config = {
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "item"
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
                "data": self.metrics
            },
            "series": series
        }

        logging.info(f"生成南丁格尔玫瑰图配置完成: {self.title}")
        return config

class StackedLineChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        config = {
            "color": [self.color_map[metric] for metric in self.metrics],
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "line"
                }
            },
            "legend": {
                "top": 30,
                "data": self.metrics
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "boundaryGap": False,
                "data": self.categories
            },
            "yAxis": {
                "type": "value"
            },
            "series": []
        }

        for metric in self.metrics:
            try:
                data_values = [row[metric] for row in self.data]
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            series_entry = {
                "name": metric,
                "type": "line",
                "stack": "总量",
                "smooth": True,
                "itemStyle": {
                    "color": self.color_map[metric]
                },
                "emphasis": {
                    "focus": "series"
                },
                "data": data_values
            }
            config["series"].append(series_entry)
            logging.debug(f"添加折线图堆叠系列: {metric}，数据点数={len(data_values)}")

        logging.info(f"生成折线图堆叠配置完成: {self.title}")
        return config

class BarChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        config = {
            "color": [self.color_map[metric] for metric in self.metrics],
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "shadow"
                }
            },
            "legend": {
                "top": 30,
                "data": self.metrics
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "data": self.categories
            },
            "yAxis": {
                "type": "value"
            },
            "series": []
        }

        for metric in self.metrics:
            try:
                data_values = [row[metric] for row in self.data]
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            series_entry = {
                "name": metric,
                "type": "bar",
                "stack": "总量",
                "itemStyle": {
                    "color": self.color_map[metric]
                },
                "data": data_values
            }
            config["series"].append(series_entry)
            logging.debug(f"添加柱状图堆叠系列: {metric}，数据点数={len(data_values)}")

        logging.info(f"生成柱状图堆叠配置完成: {self.title}")
        return config

class GroupedBarChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        """
        生成分组柱状图 (Grouped Bar Chart) 配置。
        """
        config = {
            "color": [self.color_map[metric] for metric in self.metrics],
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "shadow"
                }
            },
            "legend": {
                "top": 30,
                "data": self.metrics
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "data": self.categories
            },
            "yAxis": {
                "type": "value"
            },
            "series": []
        }

        for metric in self.metrics:
            try:
                data_values = [row[metric] for row in self.data]
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            series_entry = {
                "name": metric,
                "type": "bar",
                "itemStyle": {
                    "color": self.color_map[metric]
                },
                "data": data_values
            }
            config["series"].append(series_entry)
            logging.debug(f"添加分组柱状图系列: {metric}，数据点数={len(data_values)}")

        logging.info(f"生成分组柱状图配置完成: {self.title}")
        return config

class HorizontalBarChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        """
        生成水平柱状图配置。
        """
        config = {
            "color": [self.color_map[metric] for metric in self.metrics],
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "shadow"
                }
            },
            "legend": {
                "top": 30,
                "data": self.metrics
            },
            "grid": {
                "left": "15%",  # 调整左侧留白，避免标签被截断
                "right": "4%",
                "bottom": "3%",
                "containLabel": True
            },
            "yAxis": {
                "type": "category",
                "data": self.categories
            },
            "xAxis": {
                "type": "value"
            },
            "series": []
        }

        for metric in self.metrics:
            try:
                data_values = [row[metric] for row in self.data]
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            series_entry = {
                "name": metric,
                "type": "bar",
                "stack": "总量",
                "itemStyle": {
                    "color": self.color_map[metric]
                },
                "data": data_values
            }
            config["series"].append(series_entry)
            logging.debug(f"添加水平柱状图堆叠系列: {metric}，数据点数={len(data_values)}")

        logging.info(f"生成水平柱状图堆叠配置完成: {self.title}")
        return config

class RoundedDonutChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        """
        生成圆角环形图配置。
        """
        series = []
        num_metrics = len(self.metrics)
        if num_metrics == 0:
            logging.warning("没有可用的指标生成圆角环形图。")
            return {}
        
        # 动态计算网格布局
        cols = math.ceil(math.sqrt(num_metrics))
        rows = math.ceil(num_metrics / cols)
        padding_x = 5  # 水平间距，单位百分比
        padding_y = 5  # 垂直间距，单位百分比

        # 计算布局
        layout = calculate_chart_layout(num_metrics, cols, rows, padding_x, padding_y)
        
        for idx, metric in enumerate(self.metrics):
            try:
                data_for_donut = [{"name": row[self.categories_field], "value": row[metric]} for row in self.data]
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            
            center_x, center_y, radius = layout[idx]
            
            donut_series = {
                "name": metric,
                "type": "pie",
                "radius": ["50%", f"{radius}%"],  # 设置内外半径
                "center": [f"{center_x}%", f"{center_y}%"],
                "label": {
                    "formatter": "{b}: {c} ({d}%)"
                },
                "itemStyle": {
                    "borderRadius": 5,  # 设置圆角
                    "borderColor": "#fff",  # 设置边框颜色
                    "borderWidth": 2  # 设置边框宽度
                },
                "data": data_for_donut
            }
            series.append(donut_series)
            logging.debug(f"生成圆角环形图系列: {metric}，数据量={len(data_for_donut)}，中心=({center_x}%, {center_y}%)，半径={radius}%")
        
        config = {
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "item"
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
                "data": self.metrics
            },
            "series": series
        }

        logging.info(f"生成圆角环形图配置完成: {self.title}")
        return config

class GapPieChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        """
        生成饼图扇区间隙配置。
        """
        series = []
        num_metrics = len(self.metrics)
        if num_metrics == 0:
            logging.warning("没有可用的指标生成带间隙的饼图。")
            return {}
        
        # 动态计算网格布局
        cols = math.ceil(math.sqrt(num_metrics))
        rows = math.ceil(num_metrics / cols)
        padding_x = 5  # 水平间距，单位百分比
        padding_y = 5  # 垂直间距，单位百分比

        # 计算布局
        layout = calculate_chart_layout(num_metrics, cols, rows, padding_x, padding_y)
        
        for idx, metric in enumerate(self.metrics):
            try:
                data_for_gap_pie = [{"name": row[self.categories_field], "value": row[metric]} for row in self.data]
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            
            center_x, center_y, radius = layout[idx]
            
            gap_pie_series = {
                "name": metric,
                "type": "pie",
                "radius": f"{radius}%",
                "center": [f"{center_x}%", f"{center_y}%"],
                "label": {
                    "formatter": "{b}: {c} ({d}%)"
                },
                "itemStyle": {
                    "borderWidth": 2,  # 设置边框宽度以创建间隙
                    "borderColor": "#fff"  # 设置边框颜色为白色，形成间隙
                },
                "data": data_for_gap_pie
            }
            series.append(gap_pie_series)
            logging.debug(f"生成带间隙的饼图系列: {metric}，数据量={len(data_for_gap_pie)}，中心=({center_x}%, {center_y}%)，半径={radius}%")
        
        config = {
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "item"
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
                "data": self.metrics
            },
            "series": series
        }

        logging.info(f"生成带间隙的饼图配置完成: {self.title}")
        return config

class SemiDonutChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        """
        生成半环形图（半Donut Chart）配置。
        """
        series = []
        num_metrics = len(self.metrics)
        if num_metrics == 0:
            logging.warning("没有可用的指标生成半环形图。")
            return {}
        
        # 动态计算网格布局
        cols = math.ceil(math.sqrt(num_metrics))
        rows = math.ceil(num_metrics / cols)
        padding_x = 5  # 水平间距，单位百分比
        padding_y = 5  # 垂直间距，单位百分比

        # 计算布局
        layout = calculate_chart_layout(num_metrics, cols, rows, padding_x, padding_y)
        
        for idx, metric in enumerate(self.metrics):
            try:
                data_for_semi_donut = [{"name": row[self.categories_field], "value": row[metric]} for row in self.data]
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            
            center_x, center_y, radius = layout[idx]
            
            semi_donut_series = {
                "name": metric,
                "type": "pie",
                "radius": ["50%", f"{radius}%"],  # 设置内外半径
                "center": [f"{center_x}%", f"{center_y}%"],
                "startAngle": 180,  # 开始角度
                "endAngle": 0,      # 结束角度，形成半环形
                "label": {
                    "formatter": "{b}: {c} ({d}%)"
                },
                "itemStyle": {
                    "borderWidth": 2,
                    "borderColor": "#fff"
                },
                "data": data_for_semi_donut
            }
            series.append(semi_donut_series)
            logging.debug(f"生成半环形图系列: {metric}，数据量={len(data_for_semi_donut)}，中心=({center_x}%, {center_y}%)，半径={radius}%")
        
        config = {
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "item"
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
                "data": self.metrics
            },
            "series": series
        }

        logging.info(f"生成半环形图配置完成: {self.title}")
        return config

class LineChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        config = {
            "color": [self.color_map[metric] for metric in self.metrics],
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "cross"
                }
            },
            "legend": {
                "top": 30,
                "data": self.metrics
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "boundaryGap": False,
                "data": self.categories
            },
            "yAxis": {
                "type": "value"
            },
            "series": []
        }

        for metric in self.metrics:
            try:
                data_values = [row[metric] for row in self.data]
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            series_entry = {
                "name": metric,
                "type": "line",
                "smooth": False,
                "symbol": "circle",
                "symbolSize": 8,
                "itemStyle": {
                    "color": self.color_map[metric]
                },
                "emphasis": {
                    "focus": "series"
                },
                "data": data_values
            }
            config["series"].append(series_entry)
            logging.debug(f"添加折线图系列: {metric}，数据点数={len(data_values)}")

        logging.info(f"生成折线图配置完成: {self.title}")
        return config

class ScatterChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        series = []
        for metric in self.metrics:
            try:
                # 散点图需要数值类型的x和y轴，这里假设x轴为类别对应的索引
                data_points = [[idx, row[metric]] for idx, row in enumerate(self.data)]
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            scatter_series = {
                "name": metric,
                "type": "scatter",
                "symbolSize": 10,
                "data": data_points,
                "itemStyle": {
                    "color": self.color_map[metric]
                }
            }
            series.append(scatter_series)
            logging.debug(f"生成散点图系列: {metric}，数据点数={len(data_points)}")

        config = {
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "item",
                "formatter": "Metric: {a}<br/>Index: {b} <br/>Value: {c}"
            },
            "legend": {
                "data": self.metrics,
                "top": 30
            },
            "xAxis": {
                "type": "category",
                "name": self.categories_field,
                "data": self.categories
            },
            "yAxis": {
                "type": "value",
                "name": "Value"
            },
            "series": series
        }

        logging.info(f"生成散点图配置完成: {self.title}")
        return config

class BubbleChart(BaseChart):
    def generate_config(self) -> Dict[str, Any]:
        """
        生成气泡图配置。
        假设使用第一个指标作为X轴，第二个指标作为Y轴，第三个指标作为气泡大小。
        """
        if len(self.metrics) < 3:
            logging.error("气泡图需要至少三个指标来映射为X轴、Y轴和气泡大小。")
            raise ChartGeneratorError("气泡图需要至少三个指标来映射为X轴、Y轴和气泡大小。")
        
        x_metric = self.metrics[0]
        y_metric = self.metrics[1]
        size_metric = self.metrics[2]

        series_data = []
        size_values = []

        for row in self.data:
            try:
                x_value = float(row[x_metric])
                y_value = float(row[y_metric])
                size_value = float(row[size_metric])
            except KeyError as e:
                logging.error(f"字段 '{e.args[0]}' 在数据中不存在。")
                raise DataConversionError(f"字段 '{e.args[0]}' 在数据中不存在。")
            except ValueError as e:
                logging.warning(f"无法转换数据为浮点数: {e}. 设置为0.")
                x_value = 0.0
                y_value = 0.0
                size_value = 0.0
            size_values.append(size_value)
            series_data.append([x_value, y_value, size_value])
            logging.debug(f"气泡图数据点 - {row[self.categories_field]}: X={x_value}, Y={y_value}, Size={size_value}")

        if not size_values:
            logging.error("气泡图的数据为空。")
            raise ChartGeneratorError("气泡图的数据为空。")

        max_size = max(size_values)
        if max_size == 0:
            max_size = 1  # 防止除以零

        # 预计算气泡大小
        precomputed_sizes = [ (size / max_size) * 40 + 10 for size in size_values ]
        # 将预计算的大小添加到数据中
        series_data_with_size = [
            [series_data[idx][0], series_data[idx][1], precomputed_sizes[idx]] 
            for idx in range(len(series_data))
        ]

        series = {
            "name": self.title,
            "type": "scatter",
            "symbolSize": 20,  # 默认大小，可根据需要调整
            "data": series_data_with_size,
            "itemStyle": {
                "color": "#FF5733",  # 可根据需要自定义气泡颜色或映射
                "borderColor": "#fff",
                "borderWidth": 1
            }
        }

        config = {
            "title": {
                "text": self.title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "item",
                "formatter": (
                    f"{self.categories_field}: {{b}}<br/>"
                    f"{x_metric}: {{c[0]}}<br/>"
                    f"{y_metric}: {{c[1]}}<br/>"
                    f"{size_metric}: {{c[2]}}"
                )
            },
            "legend": {
                "data": [self.title],
                "top": 30
            },
            "xAxis": {
                "type": "value",
                "name": x_metric,
                "scale": True
            },
            "yAxis": {
                "type": "value",
                "name": y_metric,
                "scale": True
            },
            "series": [series]
        }

        logging.info(f"生成气泡图配置完成: {self.title}")
        return config

# 图表生成器类
class ChartGenerator:
    """
    图表生成器，支持多种图表类型并可扩展。
    """

    def __init__(self, csv_string: str, default_color_list: Optional[List[str]] = None):
        """
        初始化图表生成器。

        :param csv_string: CSV 数据字符串
        :param default_color_list: 默认颜色列表，可选
        """
        self.default_color_list = default_color_list or [
            "#5470C6", "#91CC75", "#EE6666", "#FAC858",
            "#73C0DE", "#3BA272", "#FC8452", "#9A60B4", "#EA7CCC",
            "#FF7F50", "#87CEFA", "#32CD32", "#BA55D3", "#7B68EE",
            "#00FA9A", "#FFD700", "#FF69B4", "#CD5C5C", "#4B0082"
        ]
        # 解析CSV并获取数据和头部
        self.data, self.headers = self._parse_csv(csv_string)
        if not self.headers:
            logging.critical("CSV头部信息缺失。")
            raise CSVFormatError("CSV头部信息缺失。")
        self.metrics = self.headers[1:]  # 假设第一列是类别
        self.categories_field = self.headers[0]  # 类别字段名
        self.categories = [row[self.categories_field].strip() for row in self.data]
        logging.debug(f"初始化图表生成器，指标={self.metrics}，类别数={len(self.categories)}")

    def _parse_csv(self, csv_string: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        解析CSV字符串为字典列表，并获取头部信息。

        :param csv_string: CSV 数据字符串
        :return: (数据列表, 头部列表)
        """
        try:
            lines = csv_string.strip().split('\n')
            # Strip each line to remove leading/trailing whitespaces
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            reader = csv.DictReader(cleaned_lines)
            headers = reader.fieldnames
            if not headers:
                logging.error("CSV头部缺失。")
                raise CSVFormatError("CSV头部缺失。")
            data = list(reader)
            if not data:
                logging.error("CSV数据为空或格式不正确。")
                raise CSVFormatError("CSV数据为空或格式不正确。")
            # 检查每行是否包含所有字段
            for idx, row in enumerate(data, start=2):
                if any(row[field] == '' for field in headers):
                    logging.warning(f"第 {idx} 行存在空字段。")
            logging.info("CSV数据成功解析。")
            return data, headers
        except csv.Error as e:
            logging.error(f"CSV解析错误: {e}")
            raise CSVFormatError(f"CSV解析错误: {e}")

    def _convert_data(self) -> List[Dict[str, Any]]:
        """
        转换CSV数据中的数值字段为浮点数，处理缺失或错误的数据。

        :return: 转换后的数据列表
        """
        converted_data = []
        for idx, row in enumerate(self.data, start=2):
            converted_row = {}
            for key, value in row.items():
                if key == self.categories_field:  # 类别字段保持为字符串
                    converted_row[key] = value.strip()
                else:
                    try:
                        converted_row[key] = float(value)
                    except ValueError:
                        logging.warning(f"第 {idx} 行，字段 '{key}' 的值 '{value}' 无法转换为浮点数，设置为0.")
                        converted_row[key] = 0.0
            converted_data.append(converted_row)
        logging.debug("数据转换完成。")
        return converted_data

    def _assign_colors(self) -> Dict[str, str]:
        """
        为每个指标分配颜色，使用默认颜色列表循环分配。

        :return: 指标到颜色的字典
        """
        color_map = {}
        for idx, metric in enumerate(self.metrics):
            color_map[metric] = self.default_color_list[idx % len(self.default_color_list)]
            logging.debug(f"分配颜色: {metric} -> {color_map[metric]}")
        return color_map

    def generate_echarts_config(self, chart_type: str, title: str) -> Dict[str, Any]:
        """
        生成ECharts配置。

        :param chart_type: 图表类型（'pie', 'rose', 'stacked_line', 'bar', 'grouped_bar', 'horizontal_bar', 'rounded_donut', 'gap_pie', 'semi_donut', 'bubble', 'line', 'scatter'）
        :param title: 图表标题
        :return: ECharts配置字典
        """
        chart_type = chart_type.lower()
        color_map = self._assign_colors()
        converted_data = self._convert_data()

        try:
            chart_instance = self._create_chart_instance(chart_type, title, converted_data, color_map)
            config = chart_instance.generate_config()
            logging.info(f"成功生成图表配置: {title} ({chart_type})")
            return config
        except ChartGeneratorError as e:
            logging.error(f"生成图表配置失败: {e}")
            raise

    def _create_chart_instance(
        self,
        chart_type: str,
        title: str,
        data: List[Dict[str, Any]],
        color_map: Dict[str, str]
    ) -> BaseChart:
        """
        根据图表类型创建相应的图表实例。

        :param chart_type: 图表类型
        :param title: 图表标题
        :param data: 转换后的数据
        :param color_map: 指标到颜色的映射
        :return: 图表实例
        """
        if chart_type == 'pie':
            return PieChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        elif chart_type == 'rose':
            return RoseChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        elif chart_type == 'stacked_line':
            return StackedLineChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        elif chart_type == 'bar':
            return BarChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        elif chart_type == 'grouped_bar':
            return GroupedBarChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        elif chart_type == 'horizontal_bar':
            return HorizontalBarChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        elif chart_type == 'rounded_donut':
            return RoundedDonutChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        elif chart_type == 'gap_pie':
            return GapPieChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        elif chart_type == 'semi_donut':
            return SemiDonutChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        elif chart_type == 'bubble':
            return BubbleChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        elif chart_type == 'line':
            return LineChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        elif chart_type == 'scatter':
            return ScatterChart(title, data, self.metrics, self.categories, color_map, self.categories_field)
        else:
            logging.error(f"不支持的图表类型: {chart_type}")
            raise UnsupportedChartTypeError(f"不支持的图表类型: {chart_type}")

    def export_to_markdown_codeblock(self, config: Dict[str, Any]) -> str:
        """
        将配置导出为Markdown代码块。

        :param config: ECharts配置字典
        :return: Markdown代码块字符串
        """
        if not config:
            logging.warning("导出空的配置。")
            return "```json\n{}\n```"
        markdown_code = f"```echarts\n{json.dumps(config, indent=2, ensure_ascii=False)}\n```"
        logging.debug("将配置导出为Markdown代码块。")
        return markdown_code

def get_echarts_config(csv_data: str, chart_type: str, title: str,enable_console: bool = False) -> str:
     # 配置日志记录
    setup_logging(enable_console=enable_console)
    try:
        chart_gen = ChartGenerator(csv_data)
        config = chart_gen.generate_echarts_config(chart_type, title)
        markdown_code = chart_gen.export_to_markdown_codeblock(config)
        return markdown_code
    except CSVFormatError as e:
        logging.critical(f"无法初始化图表生成器: {e}")
        return f"无法初始化图表生成器: {e}"
    except ChartGeneratorError as e:
        logging.error(f"图表生成错误: {e}")
        return f"图表生成错误: {e}"
