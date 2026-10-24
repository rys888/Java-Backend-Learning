
Redis 集群模式（Redis Cluster）是 Redis 提供的一种**分布式部署方案**，主要解决两个问题：

1. **数据容量问题**：单台 Redis 内存有限，无法存储海量数据。
2. **高可用问题**：某个 Redis 主节点宕机后，可以自动进行故障转移。

你前面学习的主从复制和 Sentinel，主要解决的是**高可用问题**，而 Redis Cluster 在此基础上还实现了**数据分片**。

## **一、Redis Cluster 的基本架构**

假设我们部署 6 个 Redis 节点，采用 **3 主 3 从**架构：

```text
               Redis Cluster
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
    Master A      Master B      Master C
       │             │             │
       ▼             ▼             ▼
    Replica A     Replica B     Replica C
```

其中：

- **Master**：负责存储和处理对应分片的数据。
- **Replica**：复制对应 Master 的数据，提供故障恢复能力。

与普通主从架构不同：

**Redis Cluster 中的多个 Master 并不是保存相同的数据，而是各自负责不同的数据。**

例如：

```text
Master A：user:1、user:2

Master B：product:1、product:2

Master C：order:1、order:2
```

这样，数据就可以分散到不同 Redis 节点中。

但 Redis 怎么知道一个 Key 应该存在哪个 Master 上？

这就涉及 Redis Cluster 最重要的概念：**哈希槽（Hash Slot）**。

---

## **二、哈希槽是什么？**

Redis Cluster 将整个 Key 空间划分为 **16384 个哈希槽（0～16383）**。

每个 Master 负责其中一部分哈希槽。

例如：

```text
Redis Cluster：16384 个哈希槽

Master A：0 ～ 5460

Master B：5461 ～ 10922

Master C：10923 ～ 16383
```

假设客户端执行：

```redis
SET name "Eason"
```

Redis 会根据 Key 计算它属于哪个哈希槽：

```text
hash_slot = CRC16(key) % 16384
```

例如，假设：

```text
CRC16("name") % 16384 = 3000
```

那么：

```text
name
  │
  ▼
计算哈希槽
  │
  ▼
Slot 3000
  │
  ▼
Master A
```

因此，`name` 会存储在 Master A 中。

注意，这里的 3000 只是示例。

### **这里容易和前面学的 HashTable 混淆**

你之前学过：

**Redis 通过 HashTable 定位 Key。**

现在又出现了哈希槽，它们有什么区别？

实际上是两个不同层次的定位过程：

```text
客户端：GET name
       │
       ▼
① 计算哈希槽
       │
       ▼
找到负责该槽的 Master A
       │
       ▼
② Master A 内部的 HashTable
       │
       ▼
找到 name 对应的 Value
       │
       ▼
返回 "Eason"
```

所以：

- **哈希槽**：决定 Key 存储在哪个 Redis 节点。
- **HashTable**：决定在这个 Redis 节点内部如何查找 Key。

**一句话：先通过哈希槽找节点，再通过 HashTable 找 Key。**

---

## **三、Redis Cluster 如何实现高可用？**

假设 Master A 突然宕机：

```text
Master A ❌      Master B      Master C
    │               │             │
    ▼               ▼             ▼
Replica A        Replica B     Replica C
```

Redis Cluster 会通过节点之间的通信发现故障。

当满足故障确认和选举条件后，Replica A 可以被提升为新的 Master。

```text
Master A ❌

Replica A
    │
    ▼
新 Master A
    │
    ▼
接管原 Master A 的哈希槽
```

这样，原本属于 Master A 的哈希槽仍然可以继续提供服务。

### **和 Sentinel 有什么区别？**

**Sentinel 需要独立部署哨兵节点，而 Redis Cluster 内部就具备故障检测和故障转移能力。**

Cluster 节点之间通过 Gossip 等机制交换集群状态信息，不需要额外部署 Sentinel。

不过，故障转移期间仍可能出现短暂不可用，而且 Redis Cluster 同样不能保证异步复制下的数据零丢失。

---

## **四、Redis Cluster 如何扩容？⭐⭐⭐⭐⭐**

假设最初只有三个 Master：

```text
Master A：0 ～ 5460

Master B：5461 ～ 10922

Master C：10923 ～ 16383
```

随着业务增长，三个 Master 的内存不够用了。

这时可以增加一个 Master D。

但是要注意：

**Redis Cluster 的哈希槽总数始终是 16384，不会因为增加节点而增加。**

我们只需要把原来三个 Master 的部分哈希槽迁移给 Master D。

例如：

```text
扩容前：

Master A：5461 个槽
Master B：5462 个槽
Master C：5461 个槽


扩容后：

Master A：4096 个槽
Master B：4096 个槽
Master C：4096 个槽
Master D：4096 个槽
```

Redis 会在迁移哈希槽的过程中迁移对应的 Key。

这样就实现了水平扩容。

**核心：Redis Cluster 扩容不是增加哈希槽，而是重新分配哈希槽。**

---

## **五、Redis Cluster 有什么缺点？**

虽然 Redis Cluster 解决了数据分片和高可用问题，但也有一定限制。

**① 多 Key 操作受到限制**

例如：

```redis
MGET user:1 user:2
```

如果 `user:1` 和 `user:2` 属于不同哈希槽，那么在 Cluster 模式下，这种跨槽操作通常无法直接执行。

可以使用 Hash Tag，让相关 Key 落到同一个哈希槽：

```redis
SET user:{1001}:name "Eason"
SET user:{1001}:age 20
```

这两个 Key 都会根据 `{1001}` 计算哈希槽，因此会被分配到同一个槽。

**② 运维复杂度更高**

需要管理多个 Master、Replica，以及哈希槽的迁移和重新分配。

**③ 无法保证强一致性**

Redis Cluster 的主从复制默认也是异步的，因此主节点故障时仍然可能丢失尚未同步的数据。

---

## **六、主从复制、Sentinel、Cluster 有什么区别？**

这是面试中非常容易连着问的问题。

|**对比**|**主从复制**|**Sentinel**|**Redis Cluster**|
|---|---|---|---|
|主要目的|数据复制|高可用|数据分片 + 高可用|
|多个 Master|❌|❌|✅|
|数据分片|❌|❌|✅|
|自动故障转移|❌|✅|✅|
|是否需要独立哨兵|❌|✅|❌|
|水平扩展数据容量|❌|❌|✅|

这里的 Sentinel 指的是常见的**单主多从 + Sentinel** 架构。

可以这样理解：

- **主从复制**：一个 Master，多个 Replica，解决数据冗余问题。
- **Sentinel**：在主从复制基础上，实现自动故障转移。
- **Cluster**：多个 Master 分别存储不同的数据，同时通过主从复制实现高可用。

---

## Q：

Redis Cluster 是 Redis 提供的一种分布式集群方案，主要解决单机 Redis 的数据容量限制和高可用问题。

Redis Cluster 采用哈希槽机制，将整个 Key 空间划分为 16384 个哈希槽，每个 Master 负责其中一部分。

当客户端访问某个 Key 时，会通过 CRC 16 算法计算哈希槽，从而定位到对应的 Master，再由 Master 在内部查找数据。

Redis Cluster 支持多个 Master，每个 Master 可以配置 Replica。当某个 Master 宕机时，集群可以通过故障检测和选举机制，将对应的 Replica 提升为新的 Master。

此外，Redis Cluster 支持通过迁移哈希槽实现水平扩容。

不过，Cluster 存在跨槽多 Key 操作限制，并且由于主从复制默认是异步的，因此不能保证数据完全不丢失。

### **最后记住这张图**

```text
               Redis Cluster
                     │
              CRC16(Key) % 16384
                     │
                     ▼
                  哈希槽
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
       Master A   Master B   Master C
          │          │          │
          ▼          ▼          ▼
       Replica A  Replica B  Replica C
```

**一句话记忆：Redis Cluster 通过 16384 个哈希槽实现数据分片，通过主从复制和自动故障转移实现高可用。**

你可以把 Redis Cluster 理解成：**在原来主从架构的基础上，把一个 Master 变成多个 Master，每个 Master 管理不同的数据。**