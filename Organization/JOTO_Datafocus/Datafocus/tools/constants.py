# -*- coding: utf-8 -*-
# @Time    : 2025/1/21 16:30
# @Author  : joto
# @File    : constants.py.py
# @Remark  :


class TrinoDataType(object):
    BOOLEAN = "boolean"
    TINYINT = "tinyint"
    SMALLINT = "smallint"
    INT = "integer"
    BIGINT = "bigint"
    REAL = "real"
    DOUBLE = "double"
    DECIMAL = "decimal"
    VARCHAR = "varchar"
    CHAR = "char"
    VARBINARY = "varbinary"
    JSON = "json"
    # row,array类型都需要转成json类型才能进行分析处理
    ROW = "row"
    ARRAY = "array"
    MAP = "map"
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"
    TIMESTAMP_TZ = "timestamp with time zone"

    TO_JSON_TYPES = [ROW, ARRAY, MAP]


# 数据类型常量
class DataType(object):
    BOOLEAN = "boolean"
    INT = "int"
    BIGINT = "bigint"
    DOUBLE = "double"
    STRING = "string"
    TIMESTAMP = "timestamp"
    DATE = "date"
    TIME = "time"
    NUMBER_TYPE = [INT, DOUBLE, BIGINT]

    @staticmethod
    def get_primary_base_type(base_type):
        idx = base_type.find('(')
        if idx > 0:
            return base_type[:idx]
        return base_type

    @staticmethod
    def map_data_type(base_type):
        primary_base_type = DataType.get_primary_base_type(base_type)
        if primary_base_type == TrinoDataType.BOOLEAN:
            return DataType.BOOLEAN
        elif primary_base_type in [TrinoDataType.TINYINT, TrinoDataType.SMALLINT, TrinoDataType.INT]:
            return DataType.INT
        elif primary_base_type == TrinoDataType.BIGINT:
            return DataType.BIGINT
        elif primary_base_type in [TrinoDataType.REAL, TrinoDataType.DECIMAL, TrinoDataType.DOUBLE]:
            return DataType.DOUBLE
        elif primary_base_type in [TrinoDataType.VARCHAR, TrinoDataType.VARBINARY, TrinoDataType.CHAR]:
            return DataType.STRING
        elif primary_base_type in [TrinoDataType.DATE, TrinoDataType.TIMESTAMP, TrinoDataType.TIMESTAMP_TZ]:
            return DataType.DATE
        elif primary_base_type == TrinoDataType.TIME:
            return DataType.STRING
        else:
            return DataType.STRING


class Aggregation(object):
    """
    聚合类型
    """
    SUM = 'SUM'
    AVERAGE = 'AVERAGE'
    MIN = 'MIN'
    MAX = 'MAX'
    COUNT = 'COUNT'
    COUNT_DISTINCT = 'COUNT_DISTINCT'
    VARIANCE = 'VARIANCE'
    STD_DEVIATION = 'STD_DEVIATION'
    NONE = 'NONE'

    @staticmethod
    def get_default_aggregation(data_type):
        if data_type == DataType.STRING or data_type == DataType.DATE or data_type == DataType.BOOLEAN:
            return Aggregation.NONE

        if data_type in DataType.NUMBER_TYPE:
            return Aggregation.SUM

        return Aggregation.NONE
