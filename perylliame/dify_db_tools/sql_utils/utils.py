import json
import re


def format_json_string(json_str):
    json_str = re.sub(r'\u00A0', '', json_str)
    return json_str


def array_json_encoder(val):
    return json.dumps(val)


def array_json_decoder(val):
    try:
        return json.loads(val)
    except json.JSONDecodeError:
        return ""


def array_string_encoder(val):
    return ",".join(val) if isinstance(val, list) else val


def array_string_decoder(val):
    return val.split(",") if isinstance(val, str) else val


MODULE_CONVERT_TYPE_ARRAY_JSON = 'arrayjson'
MODULE_CONVERT_TYPE_ARRAY_STRING = 'arraystring'

ConvertTypes = {
    "arrayjson": {
        "encode": array_json_encoder,
        "decode": array_json_decoder,
    },
    "arraystring": {
        "encode": array_string_encoder,
        "decode": array_string_decoder,
    }
}


def create_convertor(config):
    convert_columns = [(col_name, col_config) for col_name, col_config in config["columns"].items() if col_config.get("convert")]

    # print('convert_columns ==>>', convert_columns)

    def encode_list(list_):
        if not len(convert_columns):
            return
        for item in list_:
            for col_name, col_config in convert_columns:
                if get_value(item, col_name, None) is not None:
                    if not isinstance(item[col_name], str):
                        item[col_name] = ConvertTypes[col_config["convert"]]["encode"](item[col_name])

    def decode_list(list_):
        if not len(convert_columns):
            return
        for item in list_:
            for col_name, col_config in convert_columns:
                if get_value(item, col_name, None) is not None:
                    if isinstance(item[col_name], str):
                        item[col_name] = ConvertTypes[col_config["convert"]]["decode"](item[col_name])

    return {
        "encode_list": encode_list,
        "decode_list": decode_list
    }


def to_line(hump_name: str) -> str:
    return re.sub(r'([A-Z])', r'_\1', hump_name).lower()


def format_columns(columns):
    hump_to_columns = {}
    line_to_columns = {}

    for hump_name, col_config in columns.items():
        line_name = to_line(hump_name)
        query = get_value(col_config, "query", None) or f"t1.{line_name}"
        info = {
            **col_config,
            "hump_name": hump_name,
            "line_name": line_name,
            "query": query,
            "col_name": query.split('.')[1]
        }
        hump_to_columns[hump_name] = info
        line_to_columns[line_name] = info
    return {
        # 通过下划线命令查找列信息
        "hump_to_columns": hump_to_columns,
        # 通过驼峰命名查找列信息
        "line_to_columns": line_to_columns,
    }


# 通用的获取属性值的方法
def get_value(obj, attr_name, default=None):
    if isinstance(obj, dict):
        return obj.get(attr_name, default)
    else:
        return getattr(obj, attr_name, default)


def get_value_sql(value, value_type, sql_values):
    if value_type == 'string' or value_type == 'number':
        sql_values.append(value)
        return '?'
    elif value_type == 'date':
        sql_values.append(value)
        return "str_to_date(?, '%Y-%m-%d')"
    elif value_type == 'datetime':
        sql_values.append(value)
        return "str_to_date(?, '%Y-%m-%d %H:%i:%%s')"
    elif value_type == 'time':
        sql_values.append(value)
        return "str_to_date(?, '%H:%i:%%s')";


show_sql = True


def log_sql(sql, values):
    if show_sql:
        print("\n/*---------------------------------------log sql-------------------------------------------*/\n")
        print("\nsource sql-->>\n")
        print(sql)
        print("\nsql params-->>\n")
        print(values)
        count = 0

        def replace_callback(match):
            nonlocal count
            val = values[count]
            count = count + 1
            if isinstance(val, str):
                return val
            if isinstance(val, list):
                return ', '.join(map(str, val))
            return str(val)

        import re
        target_sql = re.sub(r'\?+', replace_callback, sql)
        print("\ntarget sql-->>\n")
        print(target_sql)
        print("\n")
