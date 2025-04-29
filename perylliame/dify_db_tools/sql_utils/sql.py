from sql_utils.build_delete_sql import build_delete_sql
from sql_utils.build_insert_sql import build_insert_sql
from sql_utils.build_query_sql import build_query_sql
from sql_utils.build_update_sql import build_update_sql
from sql_utils.utils import get_value, log_sql, create_convertor
import mysql.connector


def get_sql_connection(connect_config):
    connect_config_host = get_value(connect_config, 'host', None)
    connect_config_user = get_value(connect_config, 'user', None)
    connect_config_password = get_value(connect_config, 'password', None)
    connect_config_database = get_value(connect_config, 'database', None)
    connect_config_port = get_value(connect_config, 'port', 3306)

    if connect_config_host is None:
        raise Exception('sql connection: host parameter is missing')
    if connect_config_user is None:
        raise Exception('sql connection: user parameter is missing')
    if connect_config_password is None:
        raise Exception('sql connection: password parameter is missing')
    if connect_config_database is None:
        raise Exception('sql connection: database parameter is missing')

    conn = mysql.connector.connect(
        host=connect_config_host,
        user=connect_config_user,
        password=connect_config_password,
        database=connect_config_database,
        port=connect_config_port,
    )
    cursor = conn.cursor()

    def close():
        cursor.close()
        conn.close()

    return (conn, cursor, close)


def get_default_orders(query_config, module_config):
    orders = get_value(query_config, 'orders', None)
    if orders is not None:
        return orders
    module_config_default_orders = get_value(
        get_value(module_config, 'default', {}),
        'orders',
        None
    )
    if module_config_default_orders is not None:
        return module_config_default_orders
    return {"field": "createdAt", "desc": True}


def get_id(cursor, len):
    if len is None:
        len = 1
    sql = f"select {','.join([f'uuid() as _{idx}' for idx in range(len)])}"
    cursor.execute(sql)
    rows = cursor.fetchall()

    columns = [column[0] for column in cursor.description]
    result = [dict(zip(columns, row)) for row in rows]

    return [val for key, val in result[0].items()]


def select(connect_config, query_config, module_config, debug_data=[]):
    conn, cursor, close = get_sql_connection(connect_config)

    n_page = get_value(query_config, 'page', 0)
    n_size = get_value(query_config, 'size', 5)
    n_only_count = get_value(query_config, 'onlyCount', False)

    offset = n_page * n_size
    # 多查一条数据，方便判断是否有下一页数据
    size = n_size + 1

    target_query_config = {
        **query_config,
        "offset": offset,
        "size": size,
        "orders": get_default_orders(query_config, module_config)
    }

    sql, values = build_query_sql(target_query_config, module_config)

    try:

        debug_data.append({"sql": sql, "values": values})
        cursor.execute(sql, values)
        rows = cursor.fetchall()

        # 将查询结果转换为字典列表
        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        create_convertor(module_config)['decode_list'](result)

        if n_only_count:
            return {
                "total": result[0]['total']
            }
        else:
            has_next = False if get_value(query_config, 'all', False) else len(result) == n_size + 1
            if has_next:
                result.pop()
            return {
                "hasNext": has_next,
                "list": result,
            }
    except mysql.connector.Error as err:
        return {
            "error": f"Error: {err}",
        }
    finally:
        close()


def select_one(connect_config, query_config, module_config, debug_data=[]):
    target_query_config = {
        "offset": 0,
        "size": 1,
        "filters": [],
        "orders": {"field": "createdAt", "desc": True},
    }
    for humpName, value in query_config.items():
        target_query_config['filters'].append({
            "field": humpName,
            "value": value,
            "operator": "="
        })

    result = select(connect_config=connect_config, query_config=target_query_config, module_config=module_config, debug_data=debug_data)

    if "error" in result:
        return result

    return {"result": None if "list" not in result or len(result['list']) == 0 else result['list'][0]}


def insert(connect_config, query_config, module_config, debug_data=[]):
    conn, cursor, close = get_sql_connection(connect_config)

    row = get_value(query_config, 'row', None)
    if row is None:
        return {
            "error": "row parameter is missing",
        }
    create_convertor(module_config)['encode_list']([row])

    row_id = get_value(row, 'id', None)

    if row_id is None:
        row_id = get_id(cursor, 1)[0]
        row['id'] = row_id

    try:
        sql, values = build_insert_sql(module_config, row)

        debug_data.append({"sql": sql, "values": values})
        cursor.execute(sql, values)
        conn.commit()

        sql, values = build_query_sql({"page": 0, "size": 1, "filters": [{"field": "id", "operator": "=", "value": row_id}]}, module_config)
        debug_data.append({"sql": sql, "values": values})
        cursor.execute(sql, values)
        rows = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        create_convertor(module_config)['decode_list'](result)

        if len(result) > 0:
            return {
                "result": result[0]
            }
        else:
            return {
                "error": "insert failed, query result is empty",
            }

    except mysql.connector.Error as err:
        return {
            "error": f"Error: {err}",
        }
    finally:
        close()


def batch_insert(connect_config, query_config, module_config, debug_data=[]):
    conn, cursor, close = get_sql_connection(connect_config)

    rows = get_value(query_config, 'rows', None)
    if rows is None or len(rows) == 0:
        return {
            "error": "rows parameter is missing",
        }
    create_convertor(module_config)['encode_list'](rows)

    row_id_list = []
    for row in rows:
        row_id = get_value(row, 'id', None)
        if row_id is None:
            row_id = get_id(cursor, 1)[0]
            row['id'] = row_id
        row_id_list.append(row_id)

    try:
        for row in rows:
            sql, values = build_insert_sql(module_config, row)
            debug_data.append({"sql": sql, "values": values})
            cursor.execute(sql, values)

        conn.commit()

        sql, values = build_query_sql({"all": True, "filters": [{"field": "id", "operator": "in", "value": row_id_list}]}, module_config)
        debug_data.append({"sql": sql, "values": values})
        cursor.execute(sql, values)
        rows = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        create_convertor(module_config)['decode_list'](result)

        if len(result) > 0:
            return {
                "result": result
            }
        else:
            return {
                "error": "insert failed, query result is empty",
            }

    except mysql.connector.Error as err:
        return {
            "error": f"Error: {err}",
        }
    finally:
        close()


def update(connect_config, query_config, module_config, debug_data=[]):
    conn, cursor, close = get_sql_connection(connect_config)

    row = get_value(query_config, 'row', None)
    update_fields = get_value(query_config, 'updateFields', None)

    if row is None:
        return {
            "error": "row parameter is missing",
        }

    row_id = get_value(row, 'id', None)

    if row_id is None:
        return {
            "error": "row is missing field: id",
        }

    create_convertor(module_config)['encode_list']([row])

    try:
        sql, values = build_update_sql(module_config, row, update_fields)

        debug_data.append({"sql": sql, "values": values})
        cursor.execute(sql, values)
        conn.commit()

        sql, values = build_query_sql({"page": 0, "size": 1, "filters": [{"field": "id", "operator": "=", "value": row_id}]}, module_config)
        debug_data.append({"sql": sql, "values": values})
        cursor.execute(sql, values)
        rows = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        create_convertor(module_config)['decode_list'](result)

        if len(result) > 0:
            return {
                "result": result[0]
            }
        else:
            return {
                "error": "update failed, query result is empty",
            }

    except mysql.connector.Error as err:
        return {
            "error": f"Error: {err}",
        }
    finally:
        close()


def batch_update(connect_config, query_config, module_config, debug_data=[]):
    conn, cursor, close = get_sql_connection(connect_config)

    rows = get_value(query_config, 'rows', None)
    update_fields = get_value(query_config, 'updateFields', None)

    if rows is None or len(rows) == 0:
        return {
            "error": "rows parameter is missing",
        }
    create_convertor(module_config)['encode_list'](rows)

    row_id_list = []
    for row in rows:
        row_id = get_value(row, 'id', None)
        if row_id is None:
            return {
                "error": "row is missing field: id",
                "row": row,
            }
        row_id_list.append(row_id)

    try:
        for row in rows:
            sql, values = build_update_sql(module_config, row, update_fields)
            debug_data.append({"sql": sql, "values": values})
            cursor.execute(sql, values)

        conn.commit()

        sql, values = build_query_sql({"all": True, "filters": [{"field": "id", "operator": "in", "value": row_id_list}]}, module_config)
        debug_data.append({"sql": sql, "values": values})
        cursor.execute(sql, values)
        rows = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        create_convertor(module_config)['decode_list'](result)

        if len(result) > 0:
            return {
                "result": result
            }
        else:
            return {
                "error": "update failed, query result is empty",
            }

    except mysql.connector.Error as err:
        return {
            "error": f"Error: {err}",
        }
    finally:
        close()


def delete(connect_config, query_config, module_config, debug_data=[]):
    conn, cursor, close = get_sql_connection(connect_config)
    id = get_value(query_config, 'id', None)
    if id is None:
        return {
            "error": "id parameter is missing",
        }

    try:
        sql, values = build_delete_sql(module_config, id)
        debug_data.append({"sql": sql, "values": values})
        cursor.execute(sql, values)
        conn.commit()

        deleted_rows = cursor.rowcount

        if deleted_rows >= 1:
            return {"deletedRows": deleted_rows}
        else:
            return {"error": f"delete failed, delete rows is {deleted_rows}", }
    except mysql.connector.Error as err:
        return {
            "error": f"Error: {err}",
        }
    finally:
        close()


sql_service = {
    "select": select,
    "select_one": select_one,
    "insert": insert,
    "batch_insert": batch_insert,
    "update": update,
    "batch_update": batch_update,
    "delete": delete,
}
