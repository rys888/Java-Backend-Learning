
Redis 脑裂（Split-Brain）是指：**由于网络分区等原因，Redis 集群中同时出现两个 Master，导致数据不一致，甚至数据丢失。**

这是 Redis Sentinel（哨兵机制）中的一个高频面试问题。

## **一、Redis 脑裂是怎么产生的？⭐⭐⭐⭐⭐**

假设 Redis 采用一主两从、三个哨兵的架构：

```text
                  Sentinel 集群
                        │
                        ▼
                   Master A
                   /      \
                  ▼        ▼
              Replica B  Replica C
```

正常情况下：

- Master A 负责处理写请求。
- Replica B、C 负责复制 Master A 的数据。
- Sentinel 负责监控 Master A。

### **① Master A 发生网络故障**

假设 Master A 与 Sentinel、Replica 之间发生网络分区。

但是，**Master A 仍然可以与部分客户端通信**。

```text
客户端1 ─────→ Master A
                  ❌
               网络隔离
                  ❌
            Sentinel 集群
               /      \
              B        C
```

此时：

- 客户端 1 仍然认为 A 是 Master。
- Sentinel 无法连接 A。
- B、C 也无法正常从 A 接收数据。

### **② Sentinel 进行故障转移**

Sentinel 认为 Master A 已经宕机。

经过主观下线、客观下线和领导者选举后，将 Replica B 提升为新的 Master。

```text
客户端1 ─────→ Master A（旧主）
                  ❌
               网络隔离
                  ❌
客户端2 ─────→ Master B（新主）
                  │
                  ▼
               Replica C
```

此时出现了什么情况？

**Master A 和 Master B 同时存在，并且都可能接收写请求。**

这就是 Redis 脑裂。

---

## **二、Redis 脑裂为什么会造成数据丢失？**

假设脑裂期间：

客户端 1 向旧 Master A 写入：

```redis
SET name "Eason"
```

客户端 2 向新 Master B 写入：

```redis
SET age 20
```

此时：

```text
Master A（旧主）       Master B（新主）

name = Eason           age = 20
```

两个 Master 的数据已经不一致。

随后，网络恢复。

Sentinel 发现旧 Master A 恢复连接，就会让 A 变成 B 的从节点。

```text
        Master B
           │
           ▼
        Replica A
```

**关键问题来了：**

旧 Master A 需要按照新 Master B 的数据重新同步。

由于 A 上的 `name = Eason` 没有同步到 B，这部分数据就可能被覆盖或丢失。

即使客户端 1 之前收到了写入成功的响应，这条数据仍然可能丢失。

因此：

**脑裂最严重的问题，是旧 Master 在网络隔离期间接收的写入，可能在故障恢复后丢失。**

---

## **三、如何降低 Redis 脑裂的影响？⭐⭐⭐⭐⭐**

Redis 提供了两个非常重要的配置：

```conf
min-replicas-to-write 1
min-replicas-max-lag 10
```

### **① min-replicas-to-write**

表示：

**Master 至少需要有多少个符合条件的 Replica，才允许继续处理写请求。**

例如：

```conf
min-replicas-to-write 1
```

表示 Master 至少需要有 1 个复制延迟符合要求的从节点。

如果没有符合条件的 Replica，Master 就会拒绝写请求。

### **② min-replicas-max-lag**

表示：

**Replica 最近一次向 Master 报告复制进度的时间，距离现在不能超过多少秒。**

例如：

```conf
min-replicas-max-lag 10
```

表示只有最近 10 秒内向 Master 报告过复制进度的 Replica，才被认为符合条件。

注意，这里的 `10` 不是复制数据最多落后 10 秒，而是 **Replica 上报复制进度的时间间隔限制**。

### **③ 两个配置如何配合防止脑裂？**

假设旧 Master A 发生网络隔离：

```text
客户端1 ─────→ Master A（旧主）
                   │
                   ❌
              无法连接 Replica
                   │
                   ▼
          超过 10 秒没有收到
          Replica 的复制进度报告
                   │
                   ▼
              拒绝写请求
```

这样，即使客户端仍然连接旧 Master A，也无法一直向它写入数据。

从而减少脑裂期间产生的无效写入。

**但是需要注意：这两个配置只能降低脑裂导致的数据丢失风险，不能完全避免脑裂。**

原因是：

- 旧 Master 在超时之前，仍然可能接受写请求。
- 这些配置不保证每次写入都已经成功复制到从节点。
- 即使没有脑裂，异步复制也可能造成数据丢失。

因此，Redis Sentinel 并不提供强一致性保证。

---

## **四、面试怎么回答？**

Redis 脑裂是指由于网络分区等原因，集群中同时存在两个 Master。

例如，旧 Master 与 Sentinel 失去联系，但仍然可以处理部分客户端请求。Sentinel 判断旧 Master 下线后，会将某个 Replica 提升为新 Master。

此时新旧两个 Master 可能同时接收写请求，导致数据不一致。

当网络恢复后，旧 Master 会被降级为新 Master 的从节点，并重新同步数据，因此旧 Master 在脑裂期间接收的写入可能丢失。

为了降低脑裂的影响，可以配置 `min-replicas-to-write` 和 `min-replicas-max-lag`。

前者限制 Master 至少需要多少个符合条件的从节点，后者限制从节点上报复制进度的时间间隔。

当旧 Master 与从节点失去联系超过指定时间后，就会拒绝写请求，从而减少脑裂期间的数据丢失风险。

但这两个配置不能彻底避免脑裂，也不能保证 Redis 数据零丢失。

### **五、最后记住这张图**

```text
             网络分区
                │
                ▼
        旧 Master 被隔离
                │
                ▼
       Sentinel 选出新 Master
                │
                ▼
          出现两个 Master
                │
                ▼
       两边可能同时接收写请求
                │
                ▼
             数据不一致
                │
                ▼
             网络恢复
                │
                ▼
        旧 Master 变成从节点
                │
                ▼
       旧 Master 部分数据丢失
```

**一句话记忆：Redis 脑裂就是网络分区导致两个 Master 同时存在，解决思路是通过** ** `min-replicas-to-write` ** **和** ** `min-replicas-max-lag` ** **限制旧 Master 的写入，降低数据丢失风险。**