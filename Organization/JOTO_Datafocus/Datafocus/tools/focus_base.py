# -*- coding: utf-8 -*-
# @Time    : 2025/1/21 13:57
# @Author  : joto
# @File    : focus_base.py
# @Remark  :
import hashlib
import json
import uuid
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.constants import Aggregation, DataType
from utils.logger import get_logger

logger = get_logger()


def md5(in_str: str) -> str:
    in_str = str(in_str).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(in_str)
    return md5.hexdigest()


class FocusAPIError(Exception):
    def __init__(self, response):
        self.message = response.get("exception")
        self.err_code = response.get("errCode")

    def __str__(self):
        return "Focus API Error：%s %s" % (self.err_code, self.message)


class FocusBaseTool(Tool):
    STORAGE_SIZE = 50
    STORAGE_KEY = "StorageKey"
    STORAGE_VALUE = "StorageValue"
    STORAGE_INDEX = 'StorageIndex'

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.headers = {
            "Authorization": None,
            "Content-Type": "application/json"
        }
        self.tool_parameters = None
        self.conversation_id = None
        self.chat_id = None
        self.conversation_ids = []
        self.storage_index = int(self.__get_storage(self.STORAGE_INDEX, 0))
        if not self.storage_index:
            self.storage_index = 0
        for i in range(self.STORAGE_SIZE):
            self.conversation_ids.append(self.__get_storage_key(i))

    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage]:
        self.tool_parameters = tool_parameters
        self.conversation_id = self.get_param("conversation_id", "")
        if self.__class__.__name__ == FocusBaseTool.__name__:
            return self.list_table()

    def need_reinit(self, **kwargs) -> bool:
        """判断是否需要重新初始化"""
        data = self.get_storage_info()
        for key, value in kwargs.items():
            if not value or value.lower() != data.get(key, ""):
                return True
        return False

    def __get_storage(self, key, default=None):
        try:
            return self.session.storage.get(key).decode()
        except Exception:
            return default

    def __set_storage(self, key, value):
        self.session.storage.set(key, value.encode())

    def __get_storage_key(self, idx):
        return self.__get_storage(self.STORAGE_KEY + str(idx))

    def __set_storage_key(self, idx, value: str):
        self.__set_storage(self.STORAGE_KEY + str(idx), value)

    def __get_storage_value(self, idx):
        return self.__get_storage(self.STORAGE_VALUE + str(idx))

    def __set_storage_value(self, idx, value: str):
        self.__set_storage(self.STORAGE_VALUE + str(idx), value)

    def next_index(self) -> int:
        return self.storage_index + 1 if self.storage_index + 1 < self.STORAGE_SIZE else 0

    def get_storage_info(self) -> dict:
        """从storage中恢复指定conversation_id保存的信息"""
        if self.conversation_id and self.conversation_id in self.conversation_ids:
            self.storage_index = self.conversation_ids.index(self.conversation_id)
            try:
                return json.loads(self.__get_storage_value(self.storage_index))
            except Exception as e:
                print(e)
                pass
        else:
            self.storage_index = self.next_index()
            self.__set_storage(self.STORAGE_INDEX, str(self.storage_index))  # 及时更新storage_index
            self.conversation_ids[self.storage_index] = self.conversation_id
            self.__set_storage_key(self.storage_index, self.conversation_id)
        return {}

    def set_storage_info(self, data):
        """向storage中保存conversation_id的数据"""
        self.__set_storage_key(self.storage_index, self.conversation_id)
        self.__set_storage_value(self.storage_index, json.dumps(data, ensure_ascii=False))

    def list_table(self) -> Generator[ToolInvokeMessage]:
        """获取表列表"""
        datasource = self.parse_datasource_config()
        tbl_name = self.get_param("tableName", "")
        if datasource:
            response = self.post("/df/rest/datasource/tables", params={"name": tbl_name}, body=datasource)["data"]
        else:
            response = self.get("/df/rest/table/list", params={"name": tbl_name})["data"]
        for tbl in response:
            yield self.create_json_message({"name": tbl["tblDisplayName"], "numColumns": len(tbl['columns'])})

    def get_param(self, key, default=None):
        param = self.tool_parameters.get(key)
        if param:
            return param
        else:
            return default

    @staticmethod
    def __check_datasource_param(tool_parameters, key):
        param = tool_parameters.get(key)
        if param:
            return param
        else:
            raise ValueError("%s is necessary, if you assigned datasource type." % key.capitalize())

    def parse_datasource_config(self) -> dict:
        db_type = self.get_param("type")
        if not db_type:
            return None
        name = self.get_param("name")
        if not name:
            name = "Dify-%s-%s" % (db_type, str(uuid.uuid4())[:8])
        host = self.__check_datasource_param(self.tool_parameters, "host")
        port = self.__check_datasource_param(self.tool_parameters, "port")
        user = self.__check_datasource_param(self.tool_parameters, "user")
        password = self.__check_datasource_param(self.tool_parameters, "password")
        db = self.__check_datasource_param(self.tool_parameters, "db")
        return {
            "type": db_type,
            "name": name,
            "description": self.get_param("description"),
            "schemaName": self.get_param("schema"),
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "db": db,
            "jdbcSuffix": self.get_param("jdbc")
        }

    def get(self, url, params: dict = None, verify=True):
        print("Get: %s" % url)
        logger.info("Get: %s" % url)
        self.headers["Authorization"] = "Bearer %s" % self.runtime.credentials["app_token"]
        logger.info("Authorization: %s" % self.headers["Authorization"])
        logger.info(f"Request URL: {self.__build_url(url)}")
        logger.info(f"Request Headers: {self.headers}")
        logger.info(f"Request Params: {params}")
        
        response = requests.get(self.__build_url(url), params=params, headers=self.headers, verify=False)
        
        logger.info(f"Response Status: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        response = response.json()
        if verify and response["errCode"] != 0:
            raise FocusAPIError(response)
        return response

    def post(self, url, body: dict = None, params: dict = None, verify=True) -> dict:
        logger.info(f"Posting to: {url}")
        logger.info(f"Request body: {body}")
        logger.info(f"Request params: {params}")
        
        self.headers["Authorization"] = "Bearer %s" % self.runtime.credentials["app_token"]
        logger.info(f"Request headers: {self.headers}")
        
        response = requests.post(self.__build_url(url), params=params, json=body, headers=self.headers, verify=False)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")
        
        response.raise_for_status()
        response = response.json()
        logger.info(f"Response body: {response}")
        
        if verify and response["errCode"] != 0:
            logger.error(f"API Error: errCode={response['errCode']}")
            raise FocusAPIError(response)
        return response

    def __build_url(self, path):
        return self.runtime.credentials["datafocus_host"] + path


class FocusGPTTool(FocusBaseTool):
    STORAGE_KEY = "StorageGPTKey"
    STORAGE_VALUE = "StorageGPTValue"
    STORAGE_INDEX = 'StorageGPTIndex'

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        logger.debug(f"Invoking FocusGPTTool with parameters: {tool_parameters}")
        super()._invoke(tool_parameters)
        action = self.get_param("action")
        logger.info(f"Action: {action}")
        if action == "listTables":
            return self.list_table()
        elif action == "chat":
            return self.chat()
        else:
            raise ValueError("Unexpected action type: %s" % action)

    def init(self) -> Generator[ToolInvokeMessage]:
        """初始化FocusGPT上下文"""
        logger.info("Initializing FocusGPT context")
        language = self.get_param("language", "chinese").lower()
        tbl_name = self.get_param("tableName", "")
        logger.debug(f"Language: {language}, Table Name: {tbl_name}")
        
        datasource = self.parse_datasource_config()
        logger.debug(f"Datasource config: {datasource}")
        
        body = {"language": language}
        if datasource:
            body["dataSource"] = datasource
        if tbl_name:
            body["names"] = [tbl_name]
        else:
            logger.error("TableName is empty")
            raise KeyError("TableName cannot be empty.")
            
        logger.debug(f"Init request body: {body}")
        response = self.post("/df/rest/gpt/init", body=body)
        logger.debug(f"Init response: {response}")

        data = {"tableName": tbl_name, "language": language}
        if response["errCode"] == 0:
            self.chat_id = response["data"]
            data["chatId"] = self.chat_id
            logger.info(f"Successfully initialized with chat_id: {self.chat_id}")
            self.set_storage_info(data)
            yield self.create_text_message("已选择数据表[%s]" % tbl_name)
        elif response["errCode"] == 1008:
            logger.warning(f"Table not found: {tbl_name}")
            self.set_storage_info(data)
            yield self.create_text_message("选择的表不存在")
        else:
            logger.error(f"Unexpected error code: {response['errCode']}")
            raise ValueError("Unexpected errCode: %s" % response["errCode"])

    def need_reinit(self) -> bool:
        storage_info = self.get_storage_info()
        logger.debug(f"Current storage info: {storage_info}")
        
        language = self.get_param("language", "chinese").lower()
        tbl_name = self.get_param("tableName", "")
        logger.debug(f"Checking reinit - Language: {language}, Table: {tbl_name}")
        
        if not tbl_name or tbl_name != storage_info.get("tableName"):
            logger.info("Reinit needed: table name changed")
            return True
        if not language or language != storage_info.get("language"):
            logger.info("Reinit needed: language changed")
            return True
        logger.info("No reinit needed")
        return False

    def chat(self) -> Generator[ToolInvokeMessage]:
        logger.info("Starting chat")
        if self.need_reinit():
            logger.info("Reinitializing before chat")
            for output in self.init():
                yield output
                
        query = self.get_param("query")
        data = self.get_storage_info()
        self.chat_id = data.get("chatId")
        logger.debug(f"Chat query: {query}, chat_id: {self.chat_id}")
        
        if self.chat_id and query:
            logger.debug(f"Sending chat request with chat_id: {self.chat_id}")
            response = self.post("/df/rest/gpt/data", body={"input": query, "chatId": self.chat_id})
            
            if response["errCode"] == 1001:
                logger.warning("Chat session expired, reinitializing...")
                for output in self.init():
                    yield output
                logger.debug("Retrying chat request after reinitialization")
                response = self.post("/df/rest/gpt/data", body={"input": query, "chatId": self.chat_id})
                
            logger.debug(f"Chat response: {response}")
            yield self.create_json_message(response["data"]["content"])


class FocusSQLTool(FocusBaseTool):
    STORAGE_KEY = "StorageSQLKey"
    STORAGE_VALUE = "StorageSQLValue"
    STORAGE_INDEX = 'StorageSQLIndex'

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        super()._invoke(tool_parameters)
        action = self.get_param("action")
        if action == "listTables":
            return self.list_table()
        elif action == "chat":
            return self.chat()
        else:
            raise ValueError("Unexpected action type: %s" % action)

    def init(self) -> Generator[ToolInvokeMessage]:
        """初始化FocusGPT上下文"""
        language = self.get_param("language", "chinese").lower()
        tbl_name = self.get_param("tableName", "")
        output_sql_type = self.get_param("outputSqlType", "mysql").lower()
        model = self.get_param("model")
        datasource = self.parse_datasource_config()
        body = {"language": language}
        model_hash = ""
        if model:
            model_hash = md5(model)
            model = json.loads(model)
        else:
            model = {
                "type": output_sql_type,
                "version": "8.0",
                "tables": [self.get_table_model(tbl_name, datasource)],
                "relations": []
            }
        body["model"] = model
        response = self.post("/df/rest/gpt/start", body=body)
        data = {
            "tableName": tbl_name,
            "model": model_hash,
            "language": language,
            "outputSqlType": output_sql_type
        }
        if response["errCode"] == 0:
            self.chat_id = response["data"]
            data["chatId"] = self.chat_id
            self.set_storage_info(data)
            yield self.create_text_message("已初始化表[%s]" % tbl_name)
        else:
            raise ValueError(
                "Unexpected errCode: %s, with %s" % (response["errCode"], json.dumps(response, ensure_ascii=False)))

    def need_reinit(self) -> bool:
        storage_info = self.get_storage_info()
        tbl_name = self.get_param("tableName", "")
        if tbl_name or tbl_name != storage_info.get("tableName"):
            return True
        language = self.get_param("language", "chinese").lower()
        if language != storage_info.get("language"):
            return True
        outputSqlType = self.get_param("outputSqlType", "mysql").lower()
        if outputSqlType != storage_info.get("outputSqlType"):
            return True
        model = self.get_param("model", "")
        if model and md5(model) != storage_info.get("model"):
            return True
        return False

    def chat(self) -> Generator[ToolInvokeMessage]:
        if self.need_reinit():
            for output in self.init():
                yield output
        query = self.get_param("query")
        data = self.get_storage_info()
        self.chat_id = data.get("chatId")
        if self.chat_id and query:
            response = self.post("/df/rest/gpt/chat", body={"input": query, "chatId": self.chat_id})
            if response["errCode"] == 1001:
                for output in self.init():
                    yield output
                response = self.post("/df/rest/gpt/chat", body={"input": query, "chatId": self.chat_id})
            yield self.create_json_message(response["data"])

    def get_table_model(self, tbl_name, datasource=None):
        """获取并构建表的数据模型"""
        logger.debug(f"Getting table model for: {tbl_name}")
        logger.debug(f"Using datasource: {datasource}")
        
        if datasource:
            response = self.post("/df/rest/datasource/tables", params={"name": tbl_name}, body=datasource)["data"]
            logger.debug(f"Datasource tables response: {response}")
            for table in response:
                if table["tblDisplayName"] == tbl_name:
                    return self.build_table_model(table, is_external=True)
        else:
            response = self.get("/df/rest/table/list", params={"name": tbl_name})["data"]
            logger.debug(f"Table list response: {response}")
            for table in response:
                if table["tblDisplayName"] == tbl_name:
                    return self.build_table_model(table)
        
        logger.warning(f"Table model not found for: {tbl_name}")
        return None

    @staticmethod
    def build_table_model(table_info: dict, is_external=False) -> dict:
        columns = []
        table_model = {
            "tableDisplayName": table_info["tblDisplayName"],
            "tableName": table_info["tblName"],
            "columns": columns
        }
        for col_info in table_info["columns"]:
            columns.append({
                "columnDisplayName": col_info["colDisplayName"],
                "columnName": col_info["colName"],
                "dataType": DataType.map_data_type(col_info["dataType"]) if is_external else col_info["dataType"],
                "aggregation": Aggregation.get_default_aggregation(col_info["dataType"])
            })
        return table_model
