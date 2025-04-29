from sql_utils.DEMO_MODULE_CONFIG import DEMO_MODULE_CONFIG
from sql_utils.utils import log_sql


def build_delete_sql(module_config, id):
    if isinstance(id, list):
        sql = f"delete from {module_config['tableName']} where id in ({','.join(['?'] * len(id))})"
        values = id

    else:
        sql = f"delete from {module_config['tableName']} where id = ?"
        values = [id]

    log_sql(sql, values)
    sql = sql.replace("?", "%s")
    return (sql, values)

# sql, values = build_delete_sql(DEMO_MODULE_CONFIG, ['111','2222'])
# log_sql(sql, values)
