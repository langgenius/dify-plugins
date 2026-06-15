"""
通用 ECharts HTML 渲染工具 - 完全离线版
ECharts 5.6.0 + echarts-gl 2.1.0 + Shine 主题，全部内嵌，零网络依赖。
"""

import json
import os

_ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_assets"
)

def _read(filename: str) -> str:
    with open(os.path.join(_ASSETS_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()

def _read_geo(filename: str) -> str:
    with open(os.path.join(_ASSETS_DIR, "geo", filename), "r", encoding="utf-8") as f:
        return f.read()

try:
    _ECHARTS_JS      = _read("echarts.min.js")
    _ECHARTS_GL_JS   = _read("echarts-gl.min.js")
    _CHINA_GEO_JSON  = _read("china.json")
    _GEO_INDEX       = json.loads(_read("geo_index.json"))
except FileNotFoundError as e:
    raise RuntimeError(f"缺少资源文件: {e}")


SHINE_THEME_JS = """
(function(root,factory){
  if(typeof define==='function'&&define.amd){define(['exports','echarts'],factory);}
  else if(typeof exports==='object'&&typeof exports.nodeName!=='string'){factory(exports,require('echarts'));}
  else{factory({},root.echarts);}
}(this,function(exports,echarts){
  if(!echarts){return;}
  echarts.registerTheme('shine',{
    "color":["#c12e34","#e6b600","#0098d9","#2b821d","#005eaa","#339ca8","#cda819","#32a487"],
    "backgroundColor":"rgba(0,0,0,0)","textStyle":{},
    "title":{"textStyle":{"color":"#008acd"},"subtextStyle":{"color":"#aaaaaa"}},
    "line":{"itemStyle":{"borderWidth":1},"lineStyle":{"width":2},"symbolSize":3,"symbol":"emptyCircle","smooth":false},
    "radar":{"itemStyle":{"borderWidth":1},"lineStyle":{"width":2},"symbolSize":3,"symbol":"emptyCircle","smooth":false},
    "bar":{"itemStyle":{"barBorderWidth":0,"barBorderColor":"#ccc"}},
    "pie":{"itemStyle":{"borderWidth":0,"borderColor":"#ccc"}},
    "scatter":{"itemStyle":{"borderWidth":0,"borderColor":"#ccc"}},
    "boxplot":{"itemStyle":{"borderWidth":0,"borderColor":"#ccc"}},
    "parallel":{"itemStyle":{"borderWidth":0,"borderColor":"#ccc"}},
    "sankey":{"itemStyle":{"borderWidth":0,"borderColor":"#ccc"}},
    "funnel":{"itemStyle":{"borderWidth":0,"borderColor":"#ccc"}},
    "gauge":{"itemStyle":{"borderWidth":0,"borderColor":"#ccc"}},
    "candlestick":{"itemStyle":{"color":"#c12e34","color0":"#2b821d","borderColor":"#c12e34","borderColor0":"#2b821d","borderWidth":1}},
    "graph":{"itemStyle":{"borderWidth":0,"borderColor":"#ccc"},"lineStyle":{"width":1,"color":"#aaa"},"symbolSize":3,"symbol":"emptyCircle","smooth":false,"color":["#c12e34","#e6b600","#0098d9","#2b821d","#005eaa","#339ca8","#cda819","#32a487"],"label":{"color":"#ffffff"}},
    "map":{"itemStyle":{"areaColor":"#ddd","borderColor":"#eee","borderWidth":0.5},"label":{"color":"#c12e34"},"emphasis":{"itemStyle":{"areaColor":"rgba(193,46,52,0.25)","borderColor":"#c12e34","borderWidth":1},"label":{"color":"#c12e34"}}},
    "geo":{"itemStyle":{"areaColor":"#ddd","borderColor":"#eee","borderWidth":0.5},"label":{"color":"#c12e34"},"emphasis":{"itemStyle":{"areaColor":"rgba(193,46,52,0.25)","borderColor":"#c12e34","borderWidth":1},"label":{"color":"#c12e34"}}},
    "categoryAxis":{"axisLine":{"show":true,"lineStyle":{"color":"#008acd"}},"axisTick":{"show":true,"lineStyle":{"color":"#008acd"}},"axisLabel":{"show":true,"color":"#333"},"splitLine":{"show":false,"lineStyle":{"color":["#eee"]}},"splitArea":{"show":false}},
    "valueAxis":{"axisLine":{"show":false,"lineStyle":{"color":"#008acd"}},"axisTick":{"show":false},"axisLabel":{"show":true,"color":"#333"},"splitLine":{"show":true,"lineStyle":{"color":["#eee"]}},"splitArea":{"show":false}},
    "logAxis":{"axisLine":{"show":false},"axisTick":{"show":false},"axisLabel":{"show":true,"color":"#333"},"splitLine":{"show":true,"lineStyle":{"color":["#eee"]}}},
    "timeAxis":{"axisLine":{"show":true,"lineStyle":{"color":"#008acd"}},"axisTick":{"show":true},"axisLabel":{"show":true,"color":"#333"},"splitLine":{"show":true,"lineStyle":{"color":["#eee"]}}},
    "toolbox":{"iconStyle":{"borderColor":"#2ec7c9"},"emphasis":{"iconStyle":{"borderColor":"#18a4a6"}}},
    "legend":{"textStyle":{"color":"#333333"}},
    "tooltip":{"axisPointer":{"lineStyle":{"color":"#008acd","width":1},"crossStyle":{"color":"#008acd","width":1}}},
    "visualMap":{"color":["#5ab1ef","#e0f0ff"]},
    "dataZoom":{"backgroundColor":"rgba(47,69,84,0)","dataBackgroundColor":"#efefff","fillerColor":"rgba(182,162,222,0.2)","handleColor":"#008acd","handleSize":"100%","textStyle":{"color":"#333"}},
    "markPoint":{"label":{"color":"#ffffff"},"emphasis":{"label":{"color":"#ffffff"}}}
  });
}));
"""


def build_html(title: str, option: dict, width: int = 900, height: int = 500,
               use_gl: bool = False, geo_json: str = None) -> str:
    """
    构建完全离线 ECharts HTML。
    use_gl=True 时额外内嵌 echarts-gl。
    geo_json 非空时注册地图数据。
    """
    option_json = json.dumps(option, ensure_ascii=False, indent=2)

    gl_script = f"<script>\n{_ECHARTS_GL_JS}\n</script>" if use_gl else ""

    geo_register = ""
    if geo_json:
        geo_register = f"""
<script>
echarts.registerMap('geoMap', {geo_json});
</script>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{background:#ffffff;font-family:'Microsoft YaHei',Arial,sans-serif;}}
  #chart{{width:{width}px;height:{height}px;}}
</style>
</head>
<body>
<div id="chart"></div>
<script>{_ECHARTS_JS}</script>
{gl_script}
<script>{SHINE_THEME_JS}</script>
{geo_register}
<script>
var chart = echarts.init(document.getElementById('chart'), 'shine');
var option = {option_json};
chart.setOption(option);
window.addEventListener('resize', function(){{chart.resize();}});
</script>
</body>
</html>"""


def get_geo_json(region: str = "China") -> str:
    """返回指定地区的 GeoJSON 字符串，默认中国全图。"""
    if region == "China" or region not in _GEO_INDEX:
        return _CHINA_GEO_JSON
    fname = _GEO_INDEX[region]
    try:
        return _read_geo(fname)
    except FileNotFoundError:
        return _CHINA_GEO_JSON


def list_regions() -> list:
    """返回支持的地区列表。"""
    return list(_GEO_INDEX.keys())
