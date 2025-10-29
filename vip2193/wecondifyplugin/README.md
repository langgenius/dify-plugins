## wecondifyplugin

**Author:** neo
**Version:** 0.0.1
**Type:** tool

### Description

企业微信智能表格插件,支持创建、添加、更新记录。

### 功能

- ✅ **创建表格** (create_sheet): 创建新的智能表格,返回docid
- ✅ **查询子表** (get_sheets): 查询智能表格中的所有子表信息
- ✅ **添加记录** (add_rows): 向智能表格添加一条或多条记录
- ✅ **获取表格信息** (get_rows): 获取表格属性(工作表名称、行数、列数)
- ✅ **更新记录** (update_rows): 更新智能表格中指定记录
- 🔒 **安全凭证管理**: 企业ID和Secret加密存储在Provider中
- 🔄 **自动Token管理**: 自动获取和刷新access_token

### 快速开始

#### 1. 在企业微信后台配置

**创建自建应用:**
1. 登录企业微信管理后台: https://work.weixin.qq.com/
2. 进入 "应用管理" → "应用" → "创建应用"
3. 记录 **AgentId** 和 **Secret**

**开启API权限:**
1. 进入应用详情页
2. 点击 "企业可信IP" 配置(如需要)
3. 进入 "协作" → "文档" → "API" 
4. 开启 **"文档/智能表格"** 相关接口权限

**获取企业ID:**
1. 进入 "我的企业"
2. 复制 **企业ID (CorpID)**

#### 2. 在Dify中安装插件

安装插件后,配置Provider凭证:
- **企业ID**: 从"我的企业"获取
- **应用Secret**: 从"应用管理"获取

#### 3. 获取表格ID和子表ID

打开企业微信智能表格:
- **docid**: 从URL获取 `https://doc.weixin.qq.com/smartsheet/xxxxx`
- **sheet_id**: 子表ID,可通过API获取或在表格中查看

### 工具说明

#### 0. 创建表格 (create_sheet)

创建新的智能表格,返回docid用于后续操作。

**参数:**
- `sheet_name`: 表格名称
- `admin_users`: 管理员用户ID,逗号分隔 (可选)

**示例:**
```json
{
  "sheet_name": "销售数据表"
}
```

#### 1. 添加记录 (add_rows)

向智能表格添加新记录。

**参数:**
- `sheet_id`: 表格文档ID (docid)
- `sheet_name`: 子表ID
- `rows_data`: JSON数组格式,使用字段名作为key

**示例:**
```json
{
  "sheet_id": "your_docid",
  "sheet_name": "your_sheet_id",
  "rows_data": "[{\"姓名\": \"张三\", \"年龄\": \"25\", \"职位\": \"工程师\"}]"
}
```

#### 1.5. 查询子表 (get_sheets)

查询智能表格中的所有子表信息。

**参数:**
- `sheet_id`: 表格文档ID (docid)
- `sub_sheet_id`: 指定子表ID (可选)
- `need_all_type_sheet`: 是否包含仪表盘和说明页 (可选,默认false)

**示例:**
```json
{
  "sheet_id": "your_docid",
  "need_all_type_sheet": true
}
```

**返回:**
```json
{
  "success": true,
  "sheet_count": 2,
  "sheet_list": [
    {
      "sheet_id": "123Abc",
      "title": "工作表1",
      "is_visible": true,
      "type": "smartsheet"
    }
  ]
}
```

#### 2. 获取表格信息 (get_rows)

获取智能表格的属性信息。

**参数:**
- `sheet_id`: 表格文档ID (docid)

**示例:**
```json
{
  "sheet_id": "your_docid"
}
```

#### 3. 更新记录 (update_rows)

更新智能表格中的指定记录。

**参数:**
- `sheet_id`: 表格文档ID (docid)
- `sheet_name`: 子表ID
- `record_id`: 要更新的记录ID
- `row_data`: JSON对象格式,使用字段名作为key

**示例:**
```json
{
  "sheet_id": "your_docid",
  "sheet_name": "your_sheet_id",
  "record_id": "record_id_from_add",
  "row_data": "{\"姓名\": \"王五\", \"年龄\": \"35\"}"
}
```

### 安全特性

✓ 敏感凭证(企业ID、Secret)加密存储在Provider中  
✓ 工作流中不会暴露敏感信息  
✓ 自动管理access_token,无需手动刷新  
✓ 符合企业安全最佳实践

### 本地测试

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test_local.py
```

### 权限配置检查清单

- [ ] 已创建企业微信自建应用
- [ ] 已获取企业ID和应用Secret
- [ ] 已在应用中开启"文档/智能表格"API权限
- [ ] 已配置企业可信IP(如需要)
- [ ] 已在Dify中配置Provider凭证

### API参考

- [企业微信智能表格API文档](https://developer.work.weixin.qq.com/document/path/97392)
- [获取access_token](https://developer.work.weixin.qq.com/document/path/91039)



