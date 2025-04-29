from datetime import datetime

from sql_utils.utils import format_columns, get_value, get_value_sql, log_sql

UPDATE_EXCLUDE_FIELDS = ['id', 'createAt', 'createdBy']


def build_update_sql(module_config, row, param_update_fields=None):
    row_id = get_value(row, 'id', None)

    if row_id is None:
        raise Exception("row_id is None")

    column_info = format_columns(module_config["columns"])
    sqls = [f"update {module_config['tableName']} set"]
    values = []

    field_sql_list = []
    for hump_name, column in column_info['hump_to_columns'].items():
        value = get_value(row, hump_name, None)
        if hump_name in UPDATE_EXCLUDE_FIELDS:
            continue
        if 't1.' not in column['query']:
            continue
        if param_update_fields is not None and hump_name not in param_update_fields:
            # 如果有指定更新的字段，并且humpName不在这个字段列表中，则不更新这个字段
            continue
        if hump_name == 'updateAt':
            value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        field_sql_list.append(f"{column['col_name']} = {get_value_sql(
            value=value,
            value_type=column['valueType'],
            sql_values=values,
        )}")
    sqls.append(', '.join(field_sql_list))
    sqls.append("where id = ?")
    values.append(row_id)

    sql = ' '.join(sqls)
    log_sql(sql, values)
    sql = sql.replace("?", "%s")
    return (sql, values)


# build_update_sql(DEMO_MODULE_CONFIG, DEMO_QUERY_ROWS[0],['normalText','numberVal'])
