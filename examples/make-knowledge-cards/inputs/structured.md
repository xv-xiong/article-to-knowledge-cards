# 某接口返回字段说明

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| name | string | 名称 |
| created_at | string | 创建时间（ISO 8601） |
| tags | string[] | 标签列表 |

示例响应：

```json
{
  "id": 1024,
  "name": "example",
  "created_at": "2026-01-01T00:00:00Z",
  "tags": ["a", "b"]
}
```

批量插入语句：

```sql
INSERT INTO t (id, name) VALUES (1, 'a'), (2, 'b');
```

导出脚本片段：

```bash
curl -s "$API_BASE/items?page=1" -H "Authorization: Bearer $TOKEN" > items.json
```
