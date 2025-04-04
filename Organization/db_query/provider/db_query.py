from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import logging
from tools.db_util import DbUtil

class DbQueryProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        db_type = credentials.get("db_type", "")
        if not db_type:
            raise ValueError("Please select the database type")
        db_host = credentials.get("db_host", "")
        if not db_host:
            raise ValueError("Please fill in the database host")
        db_username = credentials.get("db_username", "")
        if not db_username:
            raise ValueError("Please fill in the database username")
        db_password = credentials.get("db_password", "")
        if not db_password:
            raise ValueError("Please fill in the database password")
        db_port = credentials.get("db_port", "")
        if DbUtil.is_not_empty(db_port) and not db_port.isdigit():
            raise ValueError("Database port can be empty or fill with integer value")
        db_name = credentials.get("db_name", "")
        db_properties = credentials.get("db_properties", "")
        try:
            db = DbUtil(db_type=db_type,
                        username=db_username, password=db_password,
                        host=db_host, port=db_port,
                        database=db_name, properties=db_properties)
            db.run_query(db.test_sql())
            credentials.setdefault("db_uri", db.get_url())
        except Exception as e:
            message = "Database connection failure."
            logging.exception(message)
            raise Exception(message + " {}".format(e))

        # try:
        #     """
        #     IMPLEMENT YOUR VALIDATION HERE
        #     """
        # except Exception as e:
        #     raise ToolProviderCredentialValidationError(str(e))
