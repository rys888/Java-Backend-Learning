[[#五、面试怎么回答？]]

主从复制解决了读扩展和数据备份的问题，但主节点本身还是单点：Master 一挂，就得人工从 Replica 里挑一个提上来，中间这段时间服务是空的。

**哨兵机制（Sentinel）解决的就是这件事：当 Redis 主节点（Master）宕机时，自动从从节点（Replica）中选出新的主节点，保证 Redis 服务的高可用性。**

具体来说，哨兵干三件事：

1. **监控**：检查 Redis 主从节点是否正常运行
2. **自动故障转移**：主节点宕机后，自动选出新的主节点
3. **通知**：将新的主节点地址通知客户端

## 一、Redis 哨兵架构

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

三个角色分工：

- **Master**：负责处理写请求，也可以处理读请求
- **Replica**：复制 Master 的数据
- **Sentinel**：负责监控 Redis 节点，并在必要时进行故障转移

为什么通常部署三个 Sentinel？因为判断故障、选举领导者都要靠多个哨兵协作投票，单个哨兵一旦误判（比如是它自己到 Master 的网络断了，Master 其实没挂），整个集群就会被错误地切换一次。

## 二、哨兵机制的工作原理

整个过程可以分为 **5 个步骤**。

### ① 监控主节点

Sentinel 会定期向 Redis 主从节点发送 `PING` 命令检查节点是否正常，也就是 **Sentinel → PING → Master**，Master 正常的话回一个 **PONG**。

只要收到正常响应，就说明这个节点可以正常通信。如果长时间收不到有效响应，Sentinel 就会开始怀疑 Master 出故障了。

### ② 主观下线（SDOWN）

假设 Master 突然宕机，**Sentinel 1 → PING → Master ❌**，超时之后还是没响应，Sentinel 1 就会把 Master 标记为：

**主观下线（Subjectively Down，SDOWN）**

为什么叫"主观"？因为这只是 Sentinel 1 自己的判断。有可能 Master 真的宕机了，也有可能只是 Sentinel 1 和 Master 之间的网络出了问题，Master 其实活得好好的。

所以，不能只凭一个 Sentinel 的判断就去做故障转移。

### ③ 客观下线（ODOWN）

这个时候 Sentinel 1 会去问其他 Sentinel：**Master 还活着吗？** 假设得到的结果是这样：

- Sentinel 1：Master 挂了！
- Sentinel 2：Master 挂了！
- Sentinel 3：Master 正常！

如果认为 Master 挂了的哨兵数量达到了配置的 `quorum`，比如 2：

```text
3 个 Sentinel
quorum = 2

至少 2 个 Sentinel 认为 Master 下线
                │
                ▼
         判定为客观下线
```

这时 Master 才被判定为：

**客观下线（Objectively Down，ODOWN）**

⚠️ 这里容易搞混，两个下线的区别是：

- **主观下线**：单个 Sentinel 判断 Master 出现故障
- **客观下线**：达到指定数量的 Sentinel 认为 Master 出现故障

### ④ 选举 Sentinel 领导者

确认 Master 客观下线后，Sentinel 之间还需要选举出一个领导者。

为什么不能三个一起上？因为三个 Sentinel 同时执行故障转移会互相冲突，搞不好选出两个新 Master。

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

选出来的领导者负责执行后续的故障转移。

⚠️ 这里有个容易忽略的点：**领导者选举需要获得 Sentinel 多数节点的授权，而不只是达到 quorum。** 比如三个 Sentinel，至少要拿到两个节点的授权，才能确认这个领导者。

### ⑤ 故障转移（Failover）

假设原来的主从架构是这样：

```text
         Master ❌
         /      \
        ▼        ▼
    Replica A  Replica B
```

领导者 Sentinel 会从从节点中选一个合适的作为新 Master，选择时依次看这几项：

- 从节点的优先级（`replica-priority`）
- 与原 Master 的复制偏移量，优先选择数据更新的节点
- 如果前面条件都相同，再比较节点运行 ID

假设最终选择 Replica A，Sentinel 会向它发送：

```redis
REPLICAOF NO ONE
```

这条命令的意思是"从现在起不属于任何主节点"，Replica A 由此脱离原来的主从关系，成为新的 Master。

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

## 三、客户端怎么知道 Master 已经切换？

假设 Java 项目原来连接 `192.168.1.10:6379`，Master 宕机、故障转移之后，新 Master 的地址变成了 `192.168.1.11:6379`。客户端如果还连旧地址，请求自然就全失败了。

因此，支持 Sentinel 的 Redis 客户端不会把 Master 地址写死，而是向哨兵查询当前 Master 的地址：

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

拿到新地址之后重新建立连接，客户端就通过 Sentinel 感知到了主节点的变化。比如 Spring Boot 里配置好 Sentinel 节点，Lettuce 这类客户端会自动处理主节点切换。

⚠️ 需要注意，**故障转移期间仍然可能出现短暂的连接失败或写入中断，哨兵并不能保证业务完全无感知。**

## 四、Redis 哨兵机制有什么缺点？

**① 故障转移需要时间。** Master 宕机后要经过故障检测、领导者选举、从节点提升这些步骤，这期间服务可能出现短暂不可用。

**② 不能保证数据完全不丢失。** 因为 Redis 主从复制默认是异步的，可能会出现这种情况：

```text
客户端 → Master 写入成功
              │
              │ 尚未同步给 Replica
              ▼
          Master 宕机
```

如果新 Master 恰好没有收到这次写入，这部分数据就丢了。

**③ 解决不了单主节点的写入性能瓶颈。** Sentinel 主要解决的是高可用问题，而不是数据分片问题。需要把数据分散到多个主节点，那是 Redis Cluster 的事。

# Q：

Redis Sentinel 是 Redis 提供的**高可用机制**，主要负责监控、自动故障转移和主节点地址通知。

Sentinel 会定期向 Redis 节点发送 `PING` 命令检查节点是否正常。如果某个 Sentinel 发现 Master 长时间没有响应，就会将其标记为主观下线。随后 Sentinel 会询问其他哨兵，当认为 Master 下线的哨兵数量达到 `quorum` 时，才会判定 Master 客观下线。

接下来，哨兵之间会选举一个领导者，由领导者负责故障转移。领导者会根据从节点优先级、复制偏移量等因素选择新的 Master，然后让其他从节点改为复制新 Master。

最后，支持 Sentinel 的客户端可以从哨兵那里获取新的 Master 地址，重新建立连接。

需要注意，Sentinel 只能提高 Redis 的可用性，不能保证数据零丢失，因为 Redis 主从复制默认是异步的。

## 六、流程图

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

相关笔记：[[Redis主从同步中的增量和完全同步怎么实现？]]
