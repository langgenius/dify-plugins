import mysql
from flask import Flask, jsonify, request
from flask_cors import CORS

from sql_utils.DEMO_CONNECT_CONFIG import DEMO_CONNECT_CONFIG
from sql_utils.DEMO_MODULE_CONFIG import DEMO_MODULE_CONFIG, DEMO_LLM_USER_CONFIG
from sql_utils.sql import sql_service, get_sql_connection, get_id
from sql_utils.utils import get_value

app = Flask(__name__)
CORS(app)


@app.route('/demo/list', methods=['POST'])
def demo_list():
    # 获取 POST 请求中的 JSON 数据
    query_config = request.get_json()

    # 构建查询语句，这里简单使用条件拼接，实际应用中要防止 SQL 注入
    print('query_config', query_config)

    result = sql_service['select'](
        connect_config=DEMO_CONNECT_CONFIG,
        query_config=query_config,
        module_config=DEMO_MODULE_CONFIG,
    )
    if get_value(result, 'error', None) is not None:
        return jsonify(result), 500
    else:
        return jsonify(result), 200


@app.route('/demo/item', methods=['POST'])
def demo_item():
    # 获取 POST 请求中的 JSON 数据
    query_config = request.get_json()

    # 构建查询语句，这里简单使用条件拼接，实际应用中要防止 SQL 注入
    print('query_config', query_config)

    result = sql_service['select_one'](
        connect_config=DEMO_CONNECT_CONFIG,
        query_config=query_config,
        module_config=DEMO_MODULE_CONFIG,
    )
    if get_value(result, 'error', None) is not None:
        return jsonify(result), 500
    else:
        return jsonify(result), 200


@app.route('/createIds', methods=['POST'])
def demo_create_id():
    # 获取 POST 请求中的 JSON 数据
    query_config = {}
    try:
        query_config = request.get_json()
    except Exception as e:
        print("createIds missing request param, use default config.")

    conn, cursor, close = get_sql_connection(DEMO_CONNECT_CONFIG)

    ids = get_id(cursor, get_value(query_config, 'num', 1))

    try:
        return jsonify({'ids': ids}), 200
    except mysql.connector.Error as err:
        return jsonify({
            "error": f"Error: {err}",
        }), 500
    finally:
        close()


@app.route('/demo/insert', methods=['POST'])
def demo_insert():
    # 获取 POST 请求中的 JSON 数据
    query_config = request.get_json()

    # 构建查询语句，这里简单使用条件拼接，实际应用中要防止 SQL 注入
    print('query_config', query_config)

    result = sql_service['insert'](
        connect_config=DEMO_CONNECT_CONFIG,
        query_config=query_config,
        module_config=DEMO_MODULE_CONFIG,
    )
    if get_value(result, 'error', None) is not None:
        return jsonify(result), 500
    else:
        return jsonify(result), 200


@app.route('/llm_user/batchInsert', methods=['POST'])
def batchInsert():
    # 获取 POST 请求中的 JSON 数据
    query_config = request.get_json()

    # 构建查询语句，这里简单使用条件拼接，实际应用中要防止 SQL 注入
    print('query_config', query_config)

    result = sql_service['batch_insert'](
        connect_config=DEMO_CONNECT_CONFIG,
        query_config=query_config,
        module_config=DEMO_LLM_USER_CONFIG,
    )
    if get_value(result, 'error', None) is not None:
        return jsonify(result), 500
    else:
        return jsonify(result), 200


@app.route('/llm_user/batchUpdate', methods=['POST'])
def batchUpdate():
    # 获取 POST 请求中的 JSON 数据
    query_config = request.get_json()

    # 构建查询语句，这里简单使用条件拼接，实际应用中要防止 SQL 注入
    print('query_config', query_config)

    result = sql_service['batch_update'](
        connect_config=DEMO_CONNECT_CONFIG,
        query_config=query_config,
        module_config=DEMO_LLM_USER_CONFIG,
    )
    if get_value(result, 'error', None) is not None:
        return jsonify(result), 500
    else:
        return jsonify(result), 200


@app.route('/demo/update', methods=['POST', 'PUT'])
def demo_update():
    # 获取 POST 请求中的 JSON 数据
    query_config = request.get_json()

    # 构建查询语句，这里简单使用条件拼接，实际应用中要防止 SQL 注入
    print('query_config', query_config)

    result = sql_service['update'](
        connect_config=DEMO_CONNECT_CONFIG,
        query_config=query_config,
        module_config=DEMO_MODULE_CONFIG,
    )
    if get_value(result, 'error', None) is not None:
        return jsonify(result), 500
    else:
        return jsonify(result), 200


@app.route('/demo/delete', methods=['POST', 'DELETE'])
def demo_delete():
    # 获取 POST 请求中的 JSON 数据
    query_config = request.get_json()

    # 构建查询语句，这里简单使用条件拼接，实际应用中要防止 SQL 注入
    print('query_config', query_config)

    result = sql_service['delete'](
        connect_config=DEMO_CONNECT_CONFIG,
        query_config=query_config,
        module_config=DEMO_MODULE_CONFIG,
    )
    if get_value(result, 'error', None) is not None:
        return jsonify(result), 500
    else:
        return jsonify(result), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7733, debug=True)
