
Redis 的 **Big Key（大 Key）问题**是指：**某个 Key 对应的 Value 占用内存过大，或者集合类型的 Value 包含过多元素，导致 Redis 性能下降。**

例如：

```text
Redis
│
├── user:1 → "Eason"              正常 Key
├── user:2 → "Tom"                正常 Key
│
└── user:3 → 100万个用户信息       Big Key
```

大 Key 的问题不在于 Key 名字太长，而在于 **Value 太大**。

## **一、什么是 Big Key？**

Redis 不同数据类型的大 Key 表现不同。

|**数据类型**|**Big Key 示例**|
|---|---|
|String|一个 Value 占用 10 MB|
|Hash|一个 Hash 包含 100 万个 Field|
|List|一个 List 包含 100 万个元素|
|Set|一个 Set 包含 100 万个成员|
|ZSet|一个 ZSet 包含 100 万个成员|

例如：

```redis
SET user:1 "Eason"
```

这是正常 Key。

但如果：

```redis
HSET user:1001 name Eason age 20 ...
```

这个 Hash 不断增加 Field，最终包含 100 万个字段，就可能成为 Big Key。

**注意：Redis 没有统一的大 Key 判断标准，需要结合 Value 大小、元素数量和业务场景判断。**

---

## **二、Big Key 有什么危害？⭐⭐⭐⭐⭐**

主要有四个问题。

### **① 阻塞 Redis 主线程**

你前面学过：

**Redis 的核心命令执行采用单线程模型。**

假设 Redis 中有一个包含 100 万个元素的 List：

```text
orders → [order1, order2, ... order1000000]
```

如果执行：

```redis
LRANGE orders 0 -1
```

Redis 需要读取并返回大量元素。

```text
客户端 A → LRANGE orders 0 -1
                    │
                    ▼
              Redis 主线程
                    │
              处理大量数据
                    │
                    ▼
客户端 B → GET name → 等待
```

由于 Redis 的命令执行主要由单线程完成，处理大 Key 的耗时操作可能阻塞其他请求。

**注意：不是所有大 Key 操作都会阻塞。**

例如 `LLEN` 获取 List 长度通常是 O(1)，即使 List 很大，也不需要遍历所有元素。

关键要看命令的时间复杂度。

### **② 网络带宽消耗大**

假设：

```text
普通 Key：1KB
Big Key：10MB
```

客户端读取普通 Key，只需要传输 1 KB。

但读取 Big Key，需要传输 10 MB。

如果有 100 个客户端同时读取：

10 MB \times 100 = 1000 MB

这会带来较大的网络开销。

可能导致：

- 网络带宽被占满。
- 请求响应时间增加。
- 客户端接收和反序列化数据的开销增加。

### **③ 内存分布不均匀**

假设使用 Redis Cluster：

```text
Master A：1GB
Master B：1GB
Master C：8GB
```

如果 Master C 存储了大量 Big Key，就可能出现内存倾斜。

即使整个集群还有剩余内存，Master C 也可能先达到内存上限，触发内存淘汰或拒绝写入。

### **④ 删除 Big Key 可能导致阻塞**

假设：

```redis
DEL big:hash
```

其中 `big:hash` 包含 100 万个 Field。

Redis 删除这个 Hash 时，需要释放大量内存。

如果使用同步删除，可能长时间占用主线程，导致其他请求延迟增加。

因此，**删除大 Key 时通常优先考虑 UNLINK，而不是 DEL。**

---

## **三、如何发现 Big Key？⭐⭐⭐⭐⭐**

### **① redis-cli –bigkeys**

Redis 提供了一个很方便的工具：

```bash
redis-cli --bigkeys
```

它会扫描数据库，统计不同数据类型中较大的 Key。

例如：

```text
Biggest string: user:profile
Biggest hash: user:1001
Biggest list: orders
```

但要注意：

`--bigkeys` 对集合类型主要根据元素数量判断大小，并不等于精确统计内存占用。

### **② MEMORY USAGE**

可以查看某个 Key 实际占用的内存估计值：

```redis
MEMORY USAGE user:1001
```

例如返回：

```text
10485760
```

表示这个 Key 估计占用了约 10 MB 内存。

对于大型集合，`MEMORY USAGE` 默认可能采用抽样估算；需要更精确时可以指定 `SAMPLES 0`，但这样也会增加遍历开销。

### **③ 使用 SCAN 扫描**

如果需要检查大量 Key，可以使用：

```redis
SCAN 0 COUNT 100
```

通过游标逐步扫描，避免一次性遍历所有 Key。

**不建议在生产环境中直接使用** ** `KEYS *` ** **扫描大量数据**，因为它会同步遍历整个 Key 空间，可能阻塞 Redis 主线程。

---

## **四、如何解决 Big Key？⭐⭐⭐⭐⭐**

### **① 拆分 Big Key**

这是最常用的方法。

假设一个 Hash 保存了 100 万个用户的信息：

```text
原来：

users
  ├── user1
  ├── user2
  ├── ...
  └── user1000000
```

可以拆分为多个 Key：

```text
拆分后：

users:0 → 部分用户
users:1 → 部分用户
users:2 → 部分用户
...
users:99 → 部分用户
```

这样每个 Key 只存储一部分数据。

**核心：将一个大 Key 拆分为多个小 Key，降低单次操作的资源消耗。**

但需要注意：拆分后可能增加 Key 数量和管理开销，Redis Cluster 中还需要考虑数据如何分布到不同哈希槽。

### **② 分批读取数据**

假设 List 中有 100 万个元素。

不建议：

```redis
LRANGE orders 0 -1
```

因为这会一次性读取所有元素。

可以改成：

```redis
LRANGE orders 0 99
LRANGE orders 100 199
LRANGE orders 200 299
```

每次只读取 100 个元素。

对于 Hash、Set、ZSet，也可以考虑：

```redis
HSCAN
SSCAN
ZSCAN
```

通过游标逐步获取元素。

不过，**分批读取只能降低单次操作的压力，并不能从根本上消除 Big Key**。

### **③ 使用 UNLINK 异步删除**

Redis 提供了：

```redis
UNLINK big:hash
```

与 `DEL` 不同：

- `DEL`：通常同步释放内存，删除大集合时可能阻塞主线程。
- `UNLINK`：先将 Key 从数据库中移除，再由后台线程异步回收内存。

例如：

```text
DEL：
Redis 主线程 → 删除 Key + 释放大量内存

UNLINK：
Redis 主线程 → 移除 Key
                     │
                     ▼
               后台释放内存
```

因此，**对于需要整体删除的大 Key，通常推荐使用 UNLINK。**

但 `UNLINK` 只是降低内存释放造成的阻塞，并不能解决大 Key 本身的存储和读取问题。

### **④ 优化数据结构和业务设计**

例如：

原本将一个用户的全部历史订单放入一个 List：

```text
user:1001:orders → 100 万个订单
```

可以考虑：

- 只缓存最近 100 条订单。
- 历史订单存储在 MySQL。
- 根据时间或业务维度拆分缓存。
- 给不再需要的数据设置合理的过期时间。

**Redis 是缓存，不一定需要保存所有历史数据。**

---

## **五、面试怎么回答？**

Redis Big Key 是指某个 Key 对应的 Value 占用内存过大，或者集合类型包含过多元素。

Big Key 主要有四个危害。

第一，大 Key 的读取、遍历等操作可能长时间占用 Redis 主线程，影响其他请求。

第二，大 Key 会增加网络传输开销，导致响应时间变长。

第三，在 Redis Cluster 中，大 Key 可能导致节点之间的内存分布不均匀。

第四，使用 DEL 同步删除大型集合时，可能因为释放大量内存而阻塞主线程。

解决方法主要包括：通过 `redis-cli --bigkeys` 和 `MEMORY USAGE` 定位大 Key；将大 Key 拆分成多个小 Key；使用分页或 SCAN 系列命令分批读取；使用 UNLINK 异步删除；以及通过业务设计限制缓存数据量。

**一句话记忆：Big Key 就是 Value 太大，主要危害是阻塞、网络开销和内存倾斜；解决思路是拆分、分批读取、异步删除。**