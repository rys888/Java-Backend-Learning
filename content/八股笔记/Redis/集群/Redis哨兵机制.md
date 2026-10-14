
Redis 的**哨兵机制（Sentinel）** 主要用于解决一个问题：

**当 Redis 主节点（Master）宕机时，自动从从节点（Replica）中选出新的主节点，保证 Redis 服务的高可用性。**

哨兵机制主要有三个功能：

1. **监控**：检查 Redis 主从节点是否正常运行。
2. **自动故障转移**：主节点宕机后，自动选出新的主节点。
3. **通知**：将新的主节点地址通知客户端。

## **一、Redis 哨兵架构**

假设有一主两从，以及三个 Sentinel：

```text
                 Sentinel 1
                 Sentinel 2
                 Sentinel 3
                      │
                      │ 监控
                      ▼
                   Master
                  /      \
                 /        \
                ▼          ▼
             Replica A   Replica B
```

其中：

- Master：负责处理写请求，也可以处理读请求。
- Replica：复制 Master 的数据。
- Sentinel：负责监控 Redis 节点，并在必要时进行故障转移。

为什么通常部署三个 Sentinel？

因为哨兵需要通过多个节点协作判断故障、选举领导者，避免单个哨兵误判导致错误切换。

---

## **二、哨兵机制的工作原理 ⭐⭐⭐⭐⭐**

整个过程可以分为 **5 个步骤**。

### **① 监控主节点**

Sentinel 会定期向 Redis 主从节点发送 `PING` 命令，检查节点是否正常。

例如：

```text
Sentinel → PING → Master
Sentinel ← PONG ← Master
```

如果 Master 正常响应，说明节点可以正常通信。

如果长时间没有收到有效响应，Sentinel 就会怀疑 Master 出现故障。

### **② 主观下线（SDOWN）**

假设 Master 突然宕机：

```text
Sentinel 1 → PING → Master ❌
```

Sentinel 1 在指定时间内没有收到有效响应，就会将 Master 标记为：

**主观下线（Subjectively Down，SDOWN）**

为什么叫主观下线？

因为这只是 Sentinel 1 自己的判断。

有可能并不是 Master 真正宕机，而是 Sentinel 1 与 Master 之间发生了网络故障。

因此，不能仅凭一个 Sentinel 的判断就进行故障转移。

### **③ 客观下线（ODOWN）**

Sentinel 1 会询问其他 Sentinel：

**你们能正常连接 Master 吗？**

假设：

```text
Sentinel 1：Master 挂了！
Sentinel 2：Master 挂了！
Sentinel 3：Master 正常！
```

如果达到配置的 `quorum` 数量，例如 2：

```text
3 个 Sentinel
quorum = 2

至少 2 个 Sentinel 认为 Master 下线
                │
                ▼
         判定为客观下线
```

这时 Master 被判定为：

**客观下线（Objectively Down，ODOWN）**

注意：

- **主观下线**：单个 Sentinel 判断 Master 出现故障。
- **客观下线**：达到指定数量的 Sentinel 认为 Master 出现故障。

### **④ 选举 Sentinel 领导者**

确认 Master 客观下线后，Sentinel 之间需要选举一个领导者。

为什么？

因为不能让三个 Sentinel 同时执行故障转移，否则可能发生冲突。

例如：

```text
Sentinel 1 ──┐
             │
Sentinel 2 ──┼──→ 选举领导者
             │
Sentinel 3 ──┘
                  │
                  ▼
              Sentinel 2
```

领导者负责执行后续故障转移。

这里要注意：**领导者选举需要获得 Sentinel 多数节点的授权，而不只是达到 quorum。**

例如三个 Sentinel，至少需要获得两个节点的授权。

### **⑤ 故障转移（Failover）**

假设原来的主从架构：

```text
         Master ❌
         /      \
        ▼        ▼
    Replica A  Replica B
```

领导者 Sentinel 会从从节点中选择一个合适的节点作为新 Master。

选择时主要考虑：

- 从节点的优先级（`replica-priority`）。
- 与原 Master 的复制偏移量，优先选择数据更新的节点。
- 如果前面条件相同，再比较节点运行 ID。

假设最终选择 Replica A：

```text
         Master ❌
         /      \
        ▼        ▼
    Replica A  Replica B
        │
        ▼
     新 Master
```

Sentinel 会向 Replica A 发送：

```redis
REPLICAOF NO ONE
```

让它脱离原来的主从关系，成为新的 Master。

随后，Sentinel 会让 Replica B 复制新的 Master：

```redis
REPLICAOF <新Master的IP> <端口>
```

最终形成：

```text
              新 Master
              Replica A
                  │
                  ▼
              Replica B
```

如果原来的 Master 后来恢复正常，Sentinel 通常会将其重新配置为新 Master 的从节点。

---

## **三、客户端怎么知道 Master 已经切换？**

假设 Java 项目原来连接：

```text
Master：192.168.1.10:6379
```

Master 宕机后，新 Master 变成：

```text
Master：192.168.1.11:6379
```

如果客户端仍然连接旧地址，就会出现问题。

因此，支持 Sentinel 的 Redis 客户端可以向哨兵查询当前 Master 地址。

```text
Java 客户端
     │
     │ 查询当前 Master
     ▼
  Sentinel
     │
     │ 返回新 Master 地址
     ▼
192.168.1.11:6379
```

客户端通过 Sentinel 感知主节点变化，并重新建立连接。

例如 Spring Boot 可以配置 Sentinel 节点，让 Lettuce 等客户端处理主节点切换。

需要注意，故障转移期间仍可能出现短暂的连接失败或写入中断，哨兵并不能保证业务完全无感知。

---

## **四、Redis 哨兵机制有什么缺点？**

主要有三个：

**① 故障转移需要时间**

Master 宕机后，需要经过故障检测、领导者选举、从节点提升等步骤。

因此，服务可能出现短暂不可用。

**② 不能保证数据完全不丢失**

因为 Redis 主从复制默认是异步的。

例如：

```text
客户端 → Master 写入成功
              │
              │ 尚未同步给 Replica
              ▼
          Master 宕机
```

如果新 Master 没有收到这次写入，就可能丢失数据。

**③ 哨兵机制不能解决单主节点的写入性能瓶颈**

Sentinel 主要解决的是高可用问题，而不是数据分片问题。

如果需要将数据分散到多个主节点，可以考虑 Redis Cluster。

---

## **五、面试怎么回答？**

Redis Sentinel 是 Redis 提供的高可用机制，主要负责监控、自动故障转移和主节点地址通知。

首先，Sentinel 会定期向 Redis 节点发送 PING 命令，检查节点是否正常。

如果某个 Sentinel 发现 Master 长时间没有响应，就会将其标记为主观下线。

随后，Sentinel 会询问其他哨兵，当认为 Master 下线的哨兵数量达到 quorum 时，就会判定 Master 客观下线。

接着，哨兵之间会选举一个领导者，由领导者负责故障转移。

领导者会根据从节点优先级、复制偏移量等因素选择新的 Master，然后让其他从节点复制新 Master。

最后，支持 Sentinel 的客户端可以获取新的 Master 地址，重新建立连接。

需要注意，Sentinel 只能提高 Redis 的可用性，不能保证数据零丢失，因为 Redis 主从复制默认是异步的。

### **六、最后记住这张图**

```text
          Master 宕机
               │
               ▼
        Sentinel 检测
               │
               ▼
          主观下线
          （SDOWN）
               │
               ▼
       多个 Sentinel 确认
               │
               ▼
          客观下线
          （ODOWN）
               │
               ▼
       选举 Sentinel 领导者
               │
               ▼
       选择一个 Replica
               │
               ▼
         提升为新 Master
               │
               ▼
       其他 Replica 重新复制
               │
               ▼
       客户端连接新 Master
```

**一句话记忆：Redis Sentinel 通过监控、主客观下线判断、领导者选举和自动故障转移，实现 Redis 主从架构的高可用。**