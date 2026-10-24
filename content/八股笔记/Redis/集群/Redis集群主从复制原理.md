
[[#Q：]]

**Redis Cluster 的主从复制，本质上与普通 Redis 主从复制相同，都是通过 PSYNC 命令实现数据同步。**

区别在于：**Redis Cluster 通过哈希槽（16384 个 Slot）将数据分散到多个 Master，每个 Master 可以拥有自己的 Replica（从节点）。**

理解它需要掌握三个问题：

1. Redis Cluster 的主从关系是什么？
2. 主从之间如何进行数据同步？
3. Master 宕机后，Cluster 如何实现故障转移？

## **一、Redis Cluster 的主从架构**

假设 Redis Cluster 采用经典的 **3 主 3 从**架构：

```text
                Redis Cluster
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
     Master A      Master B      Master C
   Slot 0~5460  Slot 5461~10922  Slot 10923~16383
        │             │             │
        │ 复制数据     │ 复制数据      │ 复制数据
        ▼             ▼             ▼
     Replica A     Replica B     Replica C
```

这里有两个非常重要的概念。

**① 分片（Sharding）**

Redis Cluster 将 16384 个哈希槽分配给不同的 Master。

例如：

```redis
SET user:1 "Eason"
```

Redis 会根据 Key 计算哈希槽：

```text
Slot = CRC16(key) % 16384
```

假设 `user:1` 对应 Slot 3000，那么这条数据就会写入 Master A。

**② 主从复制（Replication）**

Master A 的数据会同步到 Replica A。

Master B 的数据会同步到 Replica B。

Master C 的数据会同步到 Replica C。

因此：

- **分片解决数据分布和横向扩容问题。**
- **主从复制解决数据冗余问题，为高可用提供基础。**

注意：Replica A 不会复制整个 Cluster 的数据，而是复制其所属 Master 的数据。

---

## 二、Redis 主从复制的原理 

Redis 主从复制主要分为两个阶段：

**全量复制和增量复制。**

### **1. 全量复制：第一次建立主从关系**

假设 Replica A 第一次连接 Master A。

整个流程如下：

```text
        Replica A                         Master A
            │                                │
            │────── PSYNC ? -1 ────────────► │
            │                                │
            │◄──── FULLRESYNC ────────────── │
            │                                │
            │                         生成 RDB 快照
            │                                │
            │◄──── 发送 RDB 文件 ───────────  │
            │                                │
        加载 RDB 数据                         │
            │                                │
            │◄──── 发送缓冲的写命令 ────────    │
            │                                │
        执行写命令                             │
            │                                │
            ▼                                ▼
                  主从数据基本同步
```

具体分为四步。

**第一步：Replica 发送 PSYNC 命令**

```redis
PSYNC ? -1
```

`?` 表示不知道 Master 的复制 ID。

`-1` 表示没有可用于续传的复制偏移量。

Master 判断无法进行增量复制，于是返回：

```text
FULLRESYNC <replid> <offset>
```

其中：

- `replid`：Master 的复制 ID。
- `offset`：当前复制偏移量。

**第二步：Master 生成 RDB 快照**

Master 通常通过后台子进程生成 RDB 快照。

与此同时，Master 仍然可以处理客户端写请求。

那么问题来了：

**生成 RDB 期间产生的新数据怎么办？**

Redis 会将需要复制的写命令保存在复制输出缓冲区中，等待后续发送给 Replica。

**第三步：Replica 加载 RDB**

Master 将 RDB 快照发送给 Replica。

Replica 接收并加载 RDB，从而获得快照时刻的数据。

**第四步：同步后续写命令**

RDB 只是某一时刻的数据快照。

因此，Master 还需要将快照生成期间积累的写命令发送给 Replica。

Replica 执行这些命令后，就能追赶 Master 的数据状态。

之后进入持续的命令复制阶段。

---

### **2. 增量复制：主从断线后重新连接**

假设 Master 和 Replica 已经完成同步。

```text
Master A                  Replica A
   │                          │
   │──── SET a 1 ────────────►│
   │──── SET b 2 ────────────►│
   │──── SET c 3 ────────────►│
   │                          │
   X       网络断开           X
   │                          │
   │   Master 继续执行写操作    │
   │                          │
   │──── SET d 4              │
   │──── SET e 5              │
   │                          │
   │       网络恢复            │
   │◄──── PSYNC ──────────────│
   │                          │
   │──── SET d 4 ────────────►│
   │──── SET e 5 ────────────►│
```

网络恢复后，Replica 不一定需要重新复制全部数据。

因为 Redis 有一个重要机制：

**Replication Backlog（复制积压缓冲区）。**

它是 Master 用于保存最近复制数据流的环形缓冲区。

例如：

```text
Master 复制积压缓冲区

┌─────────────────────────────────────┐
│ ... │ SET c 3  │ SET d 4  │ SET e 5 │
└─────────────────────────────────────┘
```

Replica 会记录自己已经接收到的复制偏移量。

重新连接时，Replica 发送：

```text
PSYNC <replid> <offset>
```

Master 判断：

1. 复制 ID 是否匹配。
2. Replica 缺失的数据是否仍在复制积压缓冲区中。

如果满足条件：

```text
CONTINUE
```

Master 只需要发送 Replica 缺失的数据。

这就是**增量复制，也称部分重同步（Partial Resynchronization）**。

如果缺失的数据已经被环形缓冲区覆盖，或者复制历史无法衔接，就可能退化为全量复制。

### **3. 为什么需要复制偏移量？**

可以把复制偏移量理解为：

**主从节点分别记录自己处理到复制数据流的哪个位置。**

例如：

```text
Master offset  = 10000
Replica offset = 8000
```

说明 Replica 落后 Master。

如果 Master 还能提供偏移量 8000 之后的数据，就可以进行增量复制。

注意，偏移量记录的是**复制数据流的字节位置**，不是 Redis 命令的条数。

---

## **三、主从复制是同步还是异步？**

**Redis 主从复制默认是异步复制。**

例如：

```text
客户端              Master              Replica
   │                   │                    │
   │── SET key value ─►│                    │
   │                   │                    │
   │◄──── OK ──────────│                    │
   │                   │                    │
   │                   │── 复制写命令 ──────► │
   │                   │                    │
```

Master 执行写命令后，通常不需要等待 Replica 完成复制，就可以向客户端返回成功。

这样做的好处是：

**写入延迟较低，吞吐量较高。**

但也带来一个问题：

如果 Master 刚执行完写操作，还没来得及同步给 Replica 就宕机了，那么这部分数据可能丢失。

这也是 Redis Cluster **不能保证强一致性**的原因之一。

Redis 提供 `WAIT` 命令，可以等待指定数量的 Replica 确认接收复制数据，但它并不能让 Redis Cluster 变成严格的强一致性系统。

---

## **四、Redis Cluster 的 Master 宕机后怎么办？（了解）**

这部分是 Redis Cluster 和普通主从复制的重要区别。

普通主从复制本身不负责自动选主，而 Redis Cluster 内置了故障检测和故障转移机制。

假设：

```text
Master A
   │
   ▼
Replica A
```

Master A 突然宕机。

### **第一步：故障检测**

Cluster 节点通过 Gossip 协议交换集群状态信息。

当某个节点发现 Master A 无法正常响应时，会将其标记为：

```text
PFAIL（疑似下线）
```

如果负责投票的其他 Master 中有足够多的节点认为 Master A 已经不可达，就可以将其判定为：

```text
FAIL（客观下线）
```

### **第二步：从节点发起故障转移**

Master A 的 Replica 会尝试发起选举。

Replica 需要获得足够数量的 Master 投票，才能成为新的 Master。

如果 Master A 有多个 Replica，还需要根据复制进度等因素决定哪个从节点更适合发起故障转移。

### **第三步：Replica 晋升为 Master**

```text
故障前：

Master A
   │
   ▼
Replica A


故障后：

Master A（宕机）

Replica A
   │
   ▼
晋升为 Master A'
```

新的 Master A’ 接管原来 Master A 负责的哈希槽。

其他 Cluster 节点会逐步更新集群拓扑信息。

客户端随后可以将请求发送给新的 Master。

**注意：自动故障转移不等于数据零丢失。**

因为 Redis 使用异步复制，新 Master 可能没有收到旧 Master 最后执行的部分写命令。

---

## Q：

Redis Cluster 采用多主多从架构，将 16384 个哈希槽分配给不同的 Master，每个 Master 可以配置 Replica，从而实现数据分片和高可用。

Cluster 的主从复制与普通 Redis 主从复制相同，主要基于 PSYNC 命令，分为全量复制和增量复制。

**全量复制**通常发生在 Replica 第一次连接 Master 时。Replica 发送 PSYNC 命令，Master 生成 RDB 快照并发送给 Replica，Replica 加载 RDB 后，再执行 Master 在快照期间缓存的写命令，最终完成数据同步。

**增量复制**通常发生在网络短暂断开后。Replica 通过在 PSYNC 中带着的复制 ID 和复制偏移量告诉 Master 自己的复制进度。如果缺失的数据仍然保存在 Master 的复制积压缓冲区中，就只需要同步缺失部分，否则可能重新进行全量复制。

Redis 默认采用异步复制，因此主从之间可能存在短暂的数据延迟。

### 关系图

```text
             Redis Cluster
                   │
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
    Master A    Master B    Master C
       │           │           │
       ▼           ▼           ▼
    Replica A   Replica B   Replica C
       │
       ├── 全量复制：PSYNC → RDB → 补发写命令
       │
       ├── 增量复制：PSYNC → offset → backlog
```
