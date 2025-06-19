# excel_tool

**作者 / Author:** wangpengfei44  
**版本 / Version:** 0.0.1  
**类型 / Type:** 工具插件 / Tool Plugin  

**| [中文版本](#zh) | [English Version](#en) |**  
**最后更新 / Last Updated:** 2024-06-18

---

<a id="zh"></a>
## 中文版本

### 描述

`excel_tool` 是一个轻量级插件，可以将二维数组（以 JSON 字符串形式传入）转换成 Excel 文件（.xlsx）。  
支持设置列宽和合并单元格。

### 使用方法

传入名为 `data_json` 的 JSON 字符串参数，包含以下字段：

- `data`：二维数组，表示表格的行和列  
- `col_widths`（可选）：列宽配置，字典格式，键为列号（从1开始），值为宽度数值  
- `merges`（可选）：合并单元格列表，每个元素包含 `start_row`、`start_col`、`end_row`、`end_col`
- 示例输入 JSON：
```json
{
  "data": [
    ["姓名", "年龄", "城市"],
    ["张三", "25", "北京"],
    ["李四", "30", "上海"]
  ],
  "col_widths": {
    "1": 20,
    "2": 10,
    "3": 15
  },
  "merges": [
    {"start_row": 1, "start_col": 1, "end_row": 1, "end_col": 3}
  ]
}
```

### 功能

- 将 JSON 格式的二维数组转换为 Excel 文件  
- 支持自定义列宽  
- 支持合并单元格

### 运行环境

- Python 3.12 及以上版本  
- 依赖库：`openpyxl`

### 安装与使用

将插件文件放入你的环境，并通过平台安装  
使用时传入 JSON 字符串参数 `data_json` 即可

---

<a id="en"></a>
## English Version

### Description

`excel_tool` is a lightweight plugin that converts 2D arrays (provided as JSON strings) into Excel (.xlsx) files.  
It supports setting column widths and merging cells.

### Usage

Pass a JSON string parameter named `data_json` with the following fields:

- `data`: a 2D array representing rows and columns  
- `col_widths` (optional): dictionary of column widths; keys are column numbers (starting from 1), values are width values  
- `merges` (optional): list of merged cell ranges, each with `start_row`, `start_col`, `end_row`, `end_col`

### Features

- Convert JSON-based 2D array into Excel file  
- Supports custom column widths  
- Supports merged cells

### Requirements

- Python 3.12 or above  
- Dependency: `openpyxl`

### Installation & Usage

Place the plugin file in your environment and install via platform  
Call it by passing the `data_json` JSON string parameter
