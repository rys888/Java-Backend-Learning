### **① String（字符串）**

**一个 Key 对应一个 Value。**

```text
Key             Value
──────────────────────
name       →    "Eason"
age        →    "20"
token      →    "abc123"
```

对应 Redis 命令：

```redis
SET name "Eason"
SET age 20
```

可以理解成 Java 中的一个键值对。

---

### **② List（列表）**

**一个 Key 对应一个列表，元素有顺序，可以重复。**

例如保存用户最近浏览的商品：

```text
Key：history:1001

┌────────┬────────┬────────┬────────┐
│ 商品A  │ 商品B  │ 商品C  │ 商品A  │
└────────┴────────┴────────┴────────┘
   0        1        2        3
```

对应 Redis 命令：

```redis
RPUSH history:1001 "商品A" "商品B" "商品C" "商品A"
```

类似 Java 的 `ArrayList`。

---

### **③ Hash（哈希）**

**一个 Key 对应多个 Field-Value 键值对。**

例如保存用户信息：

```text
Key：user:1001
         │
         ▼
┌──────────┬────────────┐
│  Field   │   Value    │
├──────────┼────────────┤
│  name    │  Eason     │
│  age     │  20        │
│  city    │  Hangzhou  │
└──────────┴────────────┘
```

对应 Redis 命令：

```redis
HSET user:1001 name "Eason" age 20 city "Hangzhou"
```

类似 Java 的 `HashMap<String, String>`。

---

### **④ Set（集合）**

**一个 Key 对应一个集合，元素不能重复，没有固定顺序。**

例如保存点赞某篇文章的用户：

```text
Key：article:1:likes

      ┌───────────────┐
      │               │
      │  1001   1003  │
      │               │
      │  1002   1004  │
      │               │
      └───────────────┘
```

对应 Redis 命令：

```redis
SADD article:1:likes 1001 1002 1003 1004
```

如果再次添加 `1001`：

```redis
SADD article:1:likes 1001
```

不会出现两个 `1001`，因为 Set 自动去重。

类似 Java 的 `HashSet`。

---

### **⑤ ZSet（有序集合）**

**一个 Key 对应多个 Member-Score，元素不重复，按照 Score 排序。**

例如游戏排行榜：

```text
Key：game:ranking

┌──────────┬─────────┐
│  Member  │  Score  │
├──────────┼─────────┤
│  Tom     │   100   │
│  Eason   │   200   │
│  Jack    │   300   │
└──────────┴─────────┘
        ↑
   按 Score 从小到大排序
```

对应 Redis 命令：

```redis
ZADD game:ranking 100 Tom 200 Eason 300 Jack
```

如果想查看分数最高的用户：

```redis
ZREVRANGE game:ranking 0 0
```

返回：

```text
Jack
```

因为 Jack 的分数最高。

---

### **最后总结 ⭐⭐⭐⭐⭐**

```text
String：
name → "Eason"

List：
history → [A, B, C, A]

Hash：
user:1 → {
    name: "Eason",
    age: "20"
}

Set：
likes → {1001, 1002, 1003}

ZSet：
ranking → {
    Tom: 100,
    Eason: 200,
    Jack: 300
}
```

- **String**：一个值。
- **List**：一个有序列表，可以重复。
- **Hash**：一个对象，里面有多个字段。
- **Set**：一个无序集合，自动去重。
- **ZSet**：一个带分数的集合，按分数排序。

这五种是 Java 后端开发中最常接触的 Redis 数据类型。