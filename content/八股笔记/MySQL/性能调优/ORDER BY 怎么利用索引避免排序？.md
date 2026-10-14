 `ORDER BY` 能利用索引避免排序，是因为 B+ 树索引中的数据本身就是有序的。

如果 `ORDER BY` 的排序顺序与索引顺序一致，MySQL 就可以直接按照索引顺序读取数据，而不需要额外排序。

### **① 没有索引的情况**

假设有一张订单表：

|**id**|**created_at**|
|---|---|
|1|2026-10-10|
|2|2026-10-13|
|3|2026-10-11|

执行：

```sql
SELECT * FROM orders
ORDER BY created_at DESC;
```

如果 `created_at` 没有索引，MySQL 可能需要：

1. 扫描数据。
2. 根据 `created_at` 排序。
3. 返回排序后的结果。

这种额外排序通常称为 **Filesort**。

### **② 有索引的情况**

假设建立联合索引：

```sql
CREATE INDEX idx_created_id
ON orders(created_at DESC, id DESC);
```

那么 B+ 树索引中的记录就是按照以下顺序排列的：

```text
created_at DESC       id DESC

2026-10-13             2
2026-10-11             3
2026-10-10             1
```

此时执行：

```sql
SELECT * FROM orders
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

MySQL 可以直接按照索引顺序读取前 20 条记录。

**因为索引已经排好序了，所以不需要再额外排序。**

### **③ 为什么联合索引很重要？**

假设有联合索引：

```sql
INDEX idx_created_id(created_at DESC, id DESC)
```

那么：

|**ORDER BY**|**能否利用索引排序**|
|---|---|
| `ORDER BY created_at DESC` |✅ 可以|
| `ORDER BY created_at DESC, id DESC` |✅ 可以|
| `ORDER BY created_at ASC, id ASC` |✅ 可以，反向扫描|
| `ORDER BY id DESC` |❌ 通常不能直接利用该联合索引排序|
| `ORDER BY created_at DESC, id ASC` |❌ 不能直接利用该索引的顺序完成排序|

注意：这里讨论的是没有额外 `WHERE` 条件的情况。实际是否选择索引，还取决于查询成本和执行计划。

### **④ 怎么判断是否避免了排序？**

使用：

```sql
EXPLAIN
SELECT * FROM orders
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

重点看 `Extra`：

- 出现 `Using filesort`：说明需要额外排序。
- 没有 `Using filesort`：说明没有使用这种额外排序方式，可能直接利用了索引顺序。

---

### Q：

MySQL 可以利用 B+ 树索引本身有序的特性来优化 ORDER BY。

如果 ORDER BY 的字段及排序方向与索引顺序匹配，MySQL 就可以直接按照索引顺序读取数据，避免额外的 Filesort。

例如建立 `(created_at DESC, id DESC)` 联合索引后，执行 `ORDER BY created_at DESC, id DESC`，就可以利用索引顺序完成排序。

如果再配合 LIMIT，还可以只读取需要的记录，进一步提高查询效率。

**一句话记忆：B+ 树索引本身有序，ORDER BY 顺序与索引匹配，就可以直接按索引读取，避免额外排序。**