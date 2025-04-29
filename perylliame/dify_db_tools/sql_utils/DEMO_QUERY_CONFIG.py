DEMO_QUERY_ROWS = [
    {
        "id": "8570453e-0c88-11ef-9e34-5254001d6dcd",
        "createdAt": "2024-05-07 23:43:16",
        "createdBy": None,
        "updatedAt": "2024-10-31 14:41:28",
        "updatedBy": None,
        "count": 409,
        "normalText": "hello",
        "longText": None,
        "numberVal": 602,
        "flag": None,
        "selectVal": "consumer",
        "colorVal": None,
        "dateVal": "2024-05-14",
        "timeVal": None,
        "parentId": "9075e7c9-a9db-11ed-8add-525400138871",
        "imageId": None,
        "parentName": "Michael",
        "provinceVal": "310000",
        "cityVal": "310100",
        "districtVal": "310101",
        "ovVal": "member_discount",
        "arrayJson": [
            "consumer",
            "potential"
        ],
        "arrayString": [
            "consumer",
            "store"
        ],
        "arrayJsonStr": "[\"consumer\",\"potential\"]",
        "arrayStringStr": "consumer,potential"
    },
    {
        "id": "134437d3-fed2-11ee-9e34-5254001d6dcd",
        "createdAt": "2024-04-20 12:54:31",
        "createdBy": None,
        "updatedAt": "2024-10-31 14:10:46",
        "updatedBy": None,
        "count": 347,
        "normalText": "session",
        "longText": None,
        "numberVal": 456,
        "flag": None,
        "selectVal": "potential",
        "colorVal": None,
        "dateVal": "2024-04-03",
        "timeVal": None,
        "parentId": "90bf805f-a9db-11ed-8add-525400138871",
        "imageId": None,
        "parentName": "Michael3",
        "provinceVal": "150000",
        "cityVal": "150500",
        "districtVal": "150523",
        "ovVal": "member_discount",
        "arrayJson": [
            "consumer"
        ],
        "arrayString": [
            "consumer"
        ],
        "arrayJsonStr": "[\"consumer\",\"store\"]",
        "arrayStringStr": "consumer,store"
    }
]

DEMO_QUERY_CONFIG = {
    "offset": 0,
    "size": 8,
    "filters": [
        {
            "field": "normalText",
            "value": "ro",
            "operator": "~",
            "id": "query_meta_1"
        },
        {
            "field": "numberVal",
            "value": 100,
            "operator": ">",
        }
    ],
    "orders": [
        {
            "field": "createdAt",
            "desc": True
        },
        {
            "field": "updatedAt",
            "desc": False
        }
    ]
}
