import re

from sql_utils.utils import format_columns, get_value, log_sql


def query_format(query: str, value_type: str):
    if value_type == "string" or value_type == "number":
        return query
    elif value_type == "date":
        return date_format_sql(query)
    elif value_type == "datetime":
        return datetime_format_sql(query)
    elif value_type == "time":
        return time_format_sql(query)


def date_format_sql(query: str):
    return f"date_format({query}, '%Y-%m-%d')"


def datetime_format_sql(query: str):
    return f"date_format({query}, '%Y-%m-%d %H:%i:%%s')"


def time_format_sql(query: str):
    return f"date_format({query}, '%H:%i:%%s')"


def format_in(value, query, not_in, value_list):
    # value_list.append(query)
    # 如果 value 不是列表，将其按逗号分割成列表
    if not isinstance(value, list):
        list_ = value.split(',')
    else:
        list_ = value

    # 将 list_ 中的元素添加到 valueList 中
    value_list.extend(list_)

    # 生成格式化字符串
    result = f"{query} {'not ' if not_in else ''}in ({','.join('?' for _ in list_)})"
    return result


def format_in_like(value, query, not_like, value_list):
    # 如果 value 不是列表，将其按逗号分割成列表
    if not isinstance(value, list):
        list_ = value.split(',')
    else:
        list_ = value

    if not_like:
        result_list = []
        for item in list_:
            value_list.append(f"%{item}%")
            result_list.append(f"{query} not like ?")
        return f"({' and '.join(result_list)})"
    else:
        result_list = []
        for item in list_:
            value_list.append(f"%{item}%")
            result_list.append(f"{query} like ?")
        return f"({' or '.join(result_list)})"


def format_string2array(val):
    return val if isinstance(val, list) else val.split(',')


# 测试 convertor
# print(json.dumps(DEMO_QUERY_CONFIG, indent=4))
# convertor['encode_list'](DEMO_QUERY_CONFIG)
# print(json.dumps(DEMO_QUERY_CONFIG, indent=4))

# print(json.dumps(format_columns(DEMO_MODULE_CONFIG['columns']), indent=4))

def build_query_sql(query_config, module_config):
    column_info = format_columns(module_config["columns"])

    # print("column_info ==>>", column_info)

    distinct_fields = get_value(query_config, 'distinctFields', [])

    has_distinct = len(distinct_fields) > 0

    # /*---------------------------------------field sql-------------------------------------------*/
    field_sql_list = []
    field_sql_values = []

    if has_distinct:
        print("has_distinct", distinct_fields)
        field_sql_list.append("distinct")
        distinct_field_strings = []
        for item_distinct_field in distinct_fields:
            item_column_info = get_value(get_value(column_info, 'humpToColumns'), item_distinct_field)
            item_field_string = f"{query_format(item_column_info['query'], item_column_info['valueType'])}"

            if not get_value(query_config, 'onlyCount', False):
                item_field_string = f"{item_field_string} as '{item_column_info['hump_name']}'"
            distinct_field_strings.append(item_field_string)
        field_sql_list.append(','.join(distinct_field_strings))
    else:
        field_strings = []
        for hump_name, _ in module_config['columns'].items():
            item_column_info = column_info["hump_to_columns"][hump_name]
            field_strings.append(f"{query_format(item_column_info['query'], item_column_info['valueType'])} as '{item_column_info['hump_name']}'")
        field_sql_list.append(','.join(field_strings))

    # print("field_sql_list ==>>", field_sql_list)
    # print("field_sql_values ==>>", field_sql_values)

    # /*---------------------------------------from sql-------------------------------------------*/

    from_sql_list = ['from']
    from_sql_values = []

    from_sql_list.append(f"{module_config['tableName']} t1")

    join_config = get_value(module_config, 'joinConfig', [])
    if len(join_config):
        for item_join_config in join_config:
            item_join_config_type = get_value(item_join_config, 'type', '')
            if item_join_config_type != 'right join' and item_join_config_type != 'left join' and item_join_config_type != 'join':
                raise ValueError(f"Can't recognise join type:{item_join_config_type}")
            on_left, on_right = item_join_config['on'].split('=')
            left_table, left_field = on_left.strip().split('.')
            right_table, right_field = on_right.strip().split('.')
            from_sql_list.append(f"{item_join_config_type} {item_join_config['table']} {item_join_config['alia']} on {left_table}.{left_field} = {right_table}.{right_field}")

    # /*---------------------------------------filter sql-------------------------------------------*/

    filter_sql_list = []
    filter_sql_values = []

    query_config_filters = get_value(query_config, 'filters', [])

    if len(query_config_filters):
        for index, item_filter in enumerate(query_config_filters):
            # print(index, item_filter)
            if get_value(item_filter, 'id', None) is None:
                item_filter['id'] = f"_{index}"
        # print(query_config_filters)
        filter_expression = get_value(query_config, 'filterExpression', None) or ' and '.join(item['id'] for item in query_config_filters)
        filter_expression = re.sub(r'\s+(并且|&&)\s+', ' and ', filter_expression)
        filter_expression = re.sub(r'\s+(或者|\|\|)\s+', ' or ', filter_expression)

        id_2_filter = {item['id']: item for item in query_config_filters}

        def replace_func(match):

            full_match = match.group(0)
            filter_id = full_match

            if filter_id == 'and' or filter_id == 'or':
                return filter_id

            filter_info = get_value(id_2_filter, filter_id, None)

            if filter_info is None:
                return f"[NoMatchFilterForId:{filter_id}]"

            filter_field = filter_info['field']
            item_column = get_value(column_info['hump_to_columns'], filter_field, None)

            if item_column is None:
                return f"[NoMatchColumnForField:{filter_field}]"

            filter_type = get_value(filter_info, 'type', None) or get_value(item_column, 'valueType', None) or 'string'
            value = get_value(filter_info, 'value', None)
            filter_operator = filter_info['operator']
            query = item_column['query']

            if filter_type == "string":
                if filter_operator == '=' or filter_operator == '>' or filter_operator == '>=' or filter_operator == '<' or filter_operator == '<=':
                    filter_sql_values.append(value)
                    return f"{query} = ?"
                elif filter_operator == '!=':
                    filter_sql_values.append(value)
                    return f"{query} != ?"
                elif filter_operator == '~':
                    filter_sql_values.append(f"%{value}%")
                    return f"{query} like ?"
                elif filter_operator == 'in':
                    return format_in(value, query, False, filter_sql_values)
                elif filter_operator == 'not in':
                    return format_in(value, query, True, filter_sql_values)
                elif filter_operator == 'in like':
                    return format_in_like(value, query, False, filter_sql_values)
                elif filter_operator == 'not in like':
                    return format_in_like(value, query, True, filter_sql_values)
                elif filter_operator == 'is null':
                    return f"{query} is null"
                elif filter_operator == 'is not null':
                    return f"{query} is not null"
            elif filter_type == "number":
                if filter_operator == '=':
                    filter_sql_values.append(value)
                    return f"{query} = ?"
                elif filter_operator == '!=':
                    filter_sql_values.append(value)
                    return f"{query} != ?"
                elif filter_operator == '~':
                    filter_sql_values.append(f"%{value}%")
                    return f"{query} like ?"
                elif filter_operator == '>':
                    filter_sql_values.append(value)
                    return f"{query} > ?"
                elif filter_operator == '>=':
                    filter_sql_values.append(value)
                    return f"{query} >= ?"
                elif filter_operator == '<':
                    filter_sql_values.append(value)
                    return f"{query} < ?"
                elif filter_operator == '<=':
                    filter_sql_values.append(value)
                    return f"{query} <= ?"
                elif filter_operator == 'in':
                    return format_in(value, query, False, filter_sql_values)
                elif filter_operator == 'not in':
                    return format_in(value, query, True, filter_sql_values)
                elif filter_operator == 'in like':
                    return format_in_like(value, query, False, filter_sql_values)
                elif filter_operator == 'not in like':
                    return format_in_like(value, query, True, filter_sql_values)
                elif filter_operator == 'is null':
                    return f"{query} is null"
                elif filter_operator == 'is not null':
                    return f"{query} is not null"
            elif filter_type == "date":
                if filter_operator == '=' or filter_operator == '~':
                    filter_sql_values.append(value)
                    return f"{date_format_sql(query)} = ?"
                elif filter_operator == '!=':
                    filter_sql_values.append(value)
                    return f"{date_format_sql(query)} != ?"
                elif filter_operator == '>':
                    filter_sql_values.append(value)
                    return f"{query} > ?"
                elif filter_operator == '>=':
                    filter_sql_values.append(value)
                    return f"{query} >= ?"
                elif filter_operator == '<':
                    filter_sql_values.append(value)
                    return f"{query} < ?"
                elif filter_operator == '<=':
                    filter_sql_values.append(value)
                    return f"{query} <= ?"
                elif filter_operator == 'in' or filter_operator == 'in like':
                    v_list = format_string2array(value)
                    filter_sql_values.extend(v_list)
                    return f"{date_format_sql(query)} in ({','.join('?' for _ in v_list)})"
                elif filter_operator == 'not in' or filter_operator == 'not in like':
                    v_list = format_string2array(value)
                    filter_sql_values.extend(v_list)
                    return f"{date_format_sql(query)} not in ({','.join('?' for _ in v_list)})"
                elif filter_operator == 'is null':
                    return f"{query} is null"
                elif filter_operator == 'is not null':
                    return f"{query} is not null"
            elif filter_type == "time":
                if filter_operator == '=' or filter_operator == '~':
                    filter_sql_values.append(value)
                    return f"{time_format_sql(query)} = ?"
                elif filter_operator == '!=':
                    filter_sql_values.append(value)
                    return f"{time_format_sql(query)} != ?"
                elif filter_operator == '>':
                    filter_sql_values.append(value)
                    return f"{query} > ?"
                elif filter_operator == '>=':
                    filter_sql_values.append(value)
                    return f"{query} >= ?"
                elif filter_operator == '<':
                    filter_sql_values.append(value)
                    return f"{query} < ?"
                elif filter_operator == '<=':
                    filter_sql_values.append(value)
                    return f"{query} <= ?"
                elif filter_operator == 'in' or filter_operator == 'in like':
                    v_list = format_string2array(value)
                    filter_sql_values.extend(v_list)
                    return f"{time_format_sql(query)} in ({','.join('?' for _ in v_list)})"
                elif filter_operator == 'not in' or filter_operator == 'not in like':
                    v_list = format_string2array(value)
                    filter_sql_values.extend(v_list)
                    return f"{time_format_sql(query)} not in ({','.join('?' for _ in v_list)})"
                elif filter_operator == 'is null':
                    return f"{query} is null"
                elif filter_operator == 'is not null':
                    return f"{query} is not null"
                return
            elif filter_type == "datetime":
                if filter_operator == '=' or filter_operator == '~':
                    filter_sql_values.append(value)
                    return f"{datetime_format_sql(query)} = ?"
                elif filter_operator == '!=':
                    filter_sql_values.append(value)
                    return f"{datetime_format_sql(query)} != ?"
                elif filter_operator == '>':
                    filter_sql_values.append(value)
                    return f"{query} > ?"
                elif filter_operator == '>=':
                    filter_sql_values.append(value)
                    return f"{query} >= ?"
                elif filter_operator == '<':
                    filter_sql_values.append(value)
                    return f"{query} < ?"
                elif filter_operator == '<=':
                    filter_sql_values.append(value)
                    return f"{query} <= ?"
                elif filter_operator == 'not in' or filter_operator == 'not in like':
                    v_list = format_string2array(value)
                    filter_sql_values.extend(v_list)
                    return f"{datetime_format_sql(query)} in ({','.join('?' for _ in v_list)})"
                elif filter_operator == 'in' or filter_operator == 'in like':
                    v_list = format_string2array(value)
                    filter_sql_values.extend(v_list)
                    return f"{datetime_format_sql(query)} not in ({','.join('?' for _ in v_list)})"
                elif filter_operator == 'is null':
                    return f"{query} is null"
                elif filter_operator == 'is not null':
                    return f"{query} is not null"
                return
            else:
                return f"NoMatchFilterType:{filter_type}"

            return f"filter type {filter_type} no match operator: ${filter_operator}"

        new_filter_expression = re.sub(r'[a-zA-Z0-9_-]+', replace_func, filter_expression)

        filter_sql_list.extend(['where', new_filter_expression])

    # /*---------------------------------------only count-------------------------------------------*/

    sqls = []
    values = []

    query_config_only_count = get_value(query_config, 'onlyCount', False)

    if query_config_only_count:
        if not has_distinct:
            sqls.append("select count(0) as total")
        else:
            sqls.append(f"select count( {' '.join(field_sql_list)} ) as total")
            values.extend(field_sql_values)

        sqls.extend(from_sql_list)
        values.extend(from_sql_values)

        sqls.extend(filter_sql_list)
        values.extend(filter_sql_values)
    else:
        sqls.append('select')

        sqls.extend(field_sql_list)
        values.extend(field_sql_values)

        sqls.extend(from_sql_list)
        values.extend(from_sql_values)

        sqls.extend(filter_sql_list)
        values.extend(filter_sql_values)

        def get_sort_sql_value():
            sort_sql_list = []
            sort_sql_values = []

            query_config_orders = get_value(query_config, 'orders', [])
            query_config_orders = query_config_orders if isinstance(query_config_orders, list) else [query_config_orders]

            if len(query_config_orders) > 0:
                sort_sql_list.append("order by")
                temp_list = []

                for sort_item in query_config_orders:
                    sn = ''
                    sc = ''

                    if isinstance(sort_item, str):
                        sn = sort_item
                        sc = 'desc'
                    else:
                        sn = sort_item['field']
                        sc = 'desc' if sort_item['desc'] else 'asc'

                    column_item = get_value(column_info['hump_to_columns'], sn, None)

                    if column_item is None:
                        temp_list.append(f"[NoMatchSortField:{sn}]")
                    else:
                        temp_list.append(f"{column_item['query']} {sc}")

                sort_sql_list.append(', '.join(temp_list))
            return (sort_sql_list, sort_sql_values)

        sort_sql_list, sort_sql_values = get_sort_sql_value()

        sqls.extend(sort_sql_list)
        values.extend(sort_sql_values)

    query_config_all = get_value(query_config, 'all', False)

    if not query_config_all:
        sqls.append("limit ?,?")
        values.extend([
            get_value(query_config, 'offset', 0),
            get_value(query_config, 'size', 10)
        ])
    # /*---------------------------------------end-------------------------------------------*/

    sql = ' '.join(sqls)
    log_sql(sql, values)
    sql = sql.replace("?", "%s")

    return (sql, values)

# sql, values = build_query_sql(DEMO_MODULE_CONFIG, {
#     "page": 0,
#     "size": 10,
#     "filters": [
#         {
#             "field": "count",
#             "operator": "is null",
#             "id": "query_meta_1"
#         }
#     ]
# })
# log_sql(sql, values)
