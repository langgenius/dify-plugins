from collections.abc import Generator
from typing import Any

import records
from sqlalchemy import text
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.db_util import DbUtil

class SQLExecuteTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # db_uri = self.runtime.credentials.get("db_uri", '')
        inner_tool_val = tool_parameters.get("inner_tool","")
        db_uri = ''
        if inner_tool_val == "sql_execute":
            db_util = DbUtil(db_type=tool_parameters.get("db_type", ''),
                            username=tool_parameters.get("db_username", ''), 
                            password=tool_parameters.get("db_password", ''),
                            host=tool_parameters.get("db_host", ''), 
                            port=tool_parameters.get("db_port", ''),
                            database=tool_parameters.get("db_name", ''), 
                            properties=tool_parameters.get("db_properties", ''))
            db_uri = db_util.get_url()
        else:
            db_util = DbUtil(db_type=self.runtime.credentials.get("db_type", ''),
                            username=self.runtime.credentials.get("db_username", ''), 
                            password=self.runtime.credentials.get("db_password", ''),
                            host=self.runtime.credentials.get("db_host", ''), 
                            port=self.runtime.credentials.get("db_port", ''),
                            database=self.runtime.credentials.get("db_name", ''), 
                            properties=self.runtime.credentials.get("db_properties", ''))
            db_uri = db_util.get_url()
        
        db = records.Database(db_uri)
        query = tool_parameters.get("query").strip().lower()
        format = tool_parameters.get("format", "json")
        
        if query.startswith('select'):
            rows = db.query(query)
            if format == 'json':
                result = rows.as_dict()
                for r in result:
                    yield self.create_json_message(r)
            elif format == 'md':
                result = str(rows.dataset)
                yield self.create_text_message(result)
            elif format == 'csv':
                result = rows.export('csv').encode()
                yield self.create_blob_message(result, meta={'mime_type': 'text/csv', 'filename': 'result.csv'})
            elif format == 'yaml':
                result = rows.export('yaml').encode()
                yield self.create_blob_message(result, meta={'mime_type': 'text/yaml', 'filename': 'result.yaml'})
            elif format == 'xlsx':
                result = rows.export('xlsx')
                yield self.create_blob_message(result, meta={'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'filename': 'result.xlsx'})
            elif format == 'html':
                result = rows.export('html').encode()
                yield self.create_blob_message(result, meta={'mime_type': 'text/html', 'filename': 'result.html'})
            else:
                raise ValueError(f"Unsupported format: {format}")
        else:
             with db.get_connection() as conn: 
                trans = conn._conn.begin()
                try:
                    result = conn._conn.execute(text(query))
                    affected_rows = result.rowcount
                    trans.commit()
                    yield self.create_text_message(f"Query executed successfully. Affected rows: {affected_rows}")
                except Exception as e:
                    trans.rollback()
                    yield self.create_text_message(f"Error: {str(e)}")
