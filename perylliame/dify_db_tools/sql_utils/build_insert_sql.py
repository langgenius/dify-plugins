from sql_utils.utils import format_columns, get_value, get_value_sql, log_sql


def build_insert_sql(module_config, row):
    column_info = format_columns(module_config["columns"])
    sqls = [f"insert into {get_value(module_config, 'tableName')}"]
    values = []

    field_sql_left_list = []
    field_sql_right_list = []
    field_sql_right_values = []

    for hump_name, column in column_info['hump_to_columns'].items():
        value = get_value(row, hump_name)

        # if (value === undefined) {return;}

        if value is None:
            continue;

        if 't1.' not in column['query']:
            continue

        field_sql_left_list.append(column['col_name'])
        field_sql_right_list.append(get_value_sql(
            value=value,
            value_type=column['valueType'],
            sql_values=field_sql_right_values,
        ))

    sqls.append(f"( {', '.join(field_sql_left_list)} ) ")
    sqls.append("values")
    sqls.append(f"( {', '.join(field_sql_right_list)} )")
    values.extend(field_sql_right_values)
    sql = ' '.join(sqls)
    log_sql(sql, values)
    sql = sql.replace("?", "%s")
    return (sql, values)

# build_insert_sql(DEMO_MODULE_CONFIG, {"normalText": "123", "numberVal": 213})
