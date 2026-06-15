# ECharts Shine 图表插件

基于 ECharts Shine 主题的 Dify 图表插件，支持 **12 种图表类型**，适用于内网离线 ARM64 私有化部署环境。

## 支持的图表类型

| 工具名 | 图表类型 | 适用场景 |
|--------|----------|----------|
| `bar_chart` | 柱状图 | 对比分析、销售报表 |
| `line_chart` | 折线图 / 面积图 | 趋势分析、时序数据 |
| `pie_chart` | 饼图 / 环形图 | 占比分析、结构展示 |
| `scatter_chart` | 散点图 | 相关性分析、分布展示 |
| `radar_chart` | 雷达图 | 多维评估、能力雷达 |
| `heatmap_chart` | 热力图 | 密度分布、时间矩阵 |
| `funnel_chart` | 漏斗图 | 转化率分析、流程分析 |
| `gauge_chart` | 仪表盘 | KPI展示、完成率 |
| `candlestick_chart` | K线图 | 金融数据、OHLC数据 |
| `sankey_chart` | 桑基图 | 流向分析、能量流 |
| `tree_chart` | 树图 | 组织架构、层级结构 |
| `treemap_chart` | 矩形树图 | 比例层级、市场份额 |

## 部署步骤

### 1. 准备离线依赖（有网络的 ARM64 机器上执行）

```bash
cd echarts_shine/
bash wheels/download_wheels.sh
```

### 2. 内网部署

将整个目录（含 `wheels/`）拷贝到内网机器后打包：

```bash
cd echarts_shine/
zip -r ../echarts_shine.difypkg . -x "*/__pycache__/*"
```

### 3. 上传到 Dify

在 Dify 管理界面 → 插件 → 上传 `echarts_shine.difypkg`



默认使用 jsDelivr CDN 加载 ECharts。**内网环境**请将各工具中的 CDN 地址替换为内网静态服务器地址：

```python
# chart_renderer.py 第 5 行
DEFAULT_ECHARTS_CDN = "http://your-intranet-server/echarts.min.js"
```

或者下载 ECharts 到 Dify 静态资源目录后引用本地路径。

## 数据格式示例

### 柱状图
```json
categories: ["Q1","Q2","Q3","Q4"]
series_data: [{"name":"销售额","data":[120,200,150,80]},{"name":"利润","data":[60,80,70,30]}]
```

### 折线图（平滑面积图）
```json
categories: ["1月","2月","3月","4月","5月"]
series_data: [{"name":"访问量","data":[820,932,901,934,1290]}]
smooth: true
area: true
```

### 饼图（环形）
```json
data: [{"name":"直接访问","value":335},{"name":"邮件营销","value":310},{"name":"搜索引擎","value":400}]
donut: true
```

### 雷达图
```json
indicators: [{"name":"销售","max":100},{"name":"管理","max":100},{"name":"技术","max":100},{"name":"客服","max":100},{"name":"研发","max":100}]
series_data: [{"name":"产品A","value":[80,70,90,60,85]},{"name":"产品B","value":[60,85,70,80,65]}]
```

### 热力图
```json
x_categories: ["周一","周二","周三","周四","周五"]
y_categories: ["早晨","下午","晚上"]
data: [[0,0,5],[0,1,8],[0,2,2],[1,0,7],[1,1,3],[1,2,9],[2,0,1],[2,1,6],[2,2,4]]
```

### 仪表盘
```json
data: [{"name":"完成率","value":78}]
min_value: 0
max_value: 100
```

### K线图
```json
dates: ["2024-01-01","2024-01-02","2024-01-03"]
ohlc_data: [[20,34,10,38],[32,28,25,45],[28,36,22,40]]
```

### 桑基图
```json
nodes: [{"name":"来源A"},{"name":"来源B"},{"name":"目标X"},{"name":"目标Y"}]
links: [{"source":"来源A","target":"目标X","value":20},{"source":"来源B","target":"目标Y","value":30},{"source":"来源A","target":"目标Y","value":10}]
```

### 树图
```json
tree_data: {"name":"公司","children":[{"name":"技术部","children":[{"name":"前端组"},{"name":"后端组"}]},{"name":"市场部","children":[{"name":"销售组"},{"name":"品牌组"}]}]}
```

### 矩形树图
```json
data: [{"name":"技术","value":300,"children":[{"name":"前端","value":120},{"name":"后端","value":180}]},{"name":"市场","value":200},{"name":"运营","value":150}]
```

## 离线说明

本插件完全离线运行，**无需任何网络请求**：

- `_assets/echarts.min.js`：ECharts 5.6.0 完整版（~1MB），在 HTML 渲染时直接内嵌到 `<script>` 标签
- `_assets/icon.svg`：插件图标
- `wheels/`：Python 依赖离线包

每次生成图表时，HTML 输出中已包含完整的 ECharts JS，浏览器直接渲染，无任何外部依赖。
