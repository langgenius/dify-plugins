DEMO_MODULE_CONFIG = {
    "tableName": "pl_demo",
    "base": "demo",
    "columns": {
        "id": {"valueType": "string"},
        "createdAt": {"valueType": "datetime"},
        "createdBy": {"valueType": "string"},
        "updatedAt": {"valueType": "datetime"},
        "updatedBy": {"valueType": "string"},
        "count": {"valueType": "number"},
        "normalText": {"valueType": "string"},
        "longText": {"valueType": "string"},
        "numberVal": {"valueType": "number"},
        "flag": {"valueType": "string"},
        "selectVal": {"valueType": "string"},
        "colorVal": {"valueType": "string"},
        "dateVal": {"valueType": "date"},
        "timeVal": {"valueType": "time"},
        "parentId": {"valueType": "string"},
        "imageId": {"valueType": "string"},
        "parentName": {"valueType": "string", "query": "t2.normal_text"},
        "provinceVal": {"valueType": "string"},
        "cityVal": {"valueType": "string"},
        "districtVal": {"valueType": "string"},
        "ovVal": {"valueType": "string"},
        "arrayJson": {"valueType": "string", "convert": "arrayjson"},
        "arrayString": {"valueType": "string", "convert": "arraystring"},
        "arrayJsonStr": {"valueType": "string"},
        "arrayStringStr": {"valueType": "string"}
    },
    "joinConfig": [
        {
            "type": "left join",
            "table": "pl_demo",
            "alia": "t2",
            "on": "t1.parent_id = t2.id"
        }
    ]
}

DEMO_LLM_USER_CONFIG = {
    "tableName": 'llm_user',
    "base": '/llm_user',
    "columns": {
        "id": {"valueType": "string"},
        "createdAt": {"valueType": "datetime"},
        "createdBy": {"valueType": "string"},
        "updatedAt": {"valueType": "datetime"},
        "updatedBy": {"valueType": "string"},
        "fullName": {"valueType": "string"},
        "username": {"valueType": "string"},
        "password": {"valueType": "number"},
        "memberStart": {"valueType": "string"},
        "memberEnd": {"valueType": "string"},
    },
}
