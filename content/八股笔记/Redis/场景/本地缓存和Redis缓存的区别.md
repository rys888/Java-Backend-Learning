
本地缓存和 Redis 缓存最大的区别是：**本地缓存存储在应用程序自己的内存中，而 Redis 缓存存储在独立的 Redis 服务中。**

## **一、什么是本地缓存？**

假设你开发了一个 Spring Boot 项目，需要频繁查询商品信息。

如果使用本地缓存，可以通过 `HashMap`、`ConcurrentHashMap` 或 Caffeine 将数据保存在 JVM 内存中。

```text
       Java 应用
┌──────────────────────┐
│                      │
│   Spring Boot        │
│        │             │
│        ▼             │
│   本地缓存（JVM）      │
│        │             │
│        ▼             │
│      MySQL           │
└──────────────────────┘
```

例如：

```java
Map<Long, String> cache = new ConcurrentHashMap<>();

cache.put(1L, "商品A");

String product = cache.get(1L);
```

这里的商品数据就保存在当前 Java 进程的内存中。

**优点：访问速度非常快，不需要经过网络。**

但问题是：如果部署多个 Java 服务实例，每个实例都有自己的本地缓存。

---

## **二、什么是 Redis 缓存？**

Redis 缓存是将数据存储在独立的 Redis 服务中。

```text
Spring Boot A ──┐
                │
Spring Boot B ──┼──→ Redis
                │
Spring Boot C ──┘
```

例如：

```java
redisTemplate.opsForValue().set("product:1", "商品A");

Object product = redisTemplate.opsForValue().get("product:1");
```

三个 Spring Boot 实例都可以访问同一个 Redis。

**优点：多个应用实例可以共享缓存数据。**

但由于 Redis 通常是独立服务，所以访问时需要网络通信。

---

## **三、本地缓存和 Redis 缓存的区别 ⭐⭐⭐⭐⭐**

|**对比**|**本地缓存**|**Redis 缓存**|
|---|---|---|
|存储位置|JVM 内存|独立 Redis 服务的内存|
|访问速度|**更快**，无需网络通信|较快，但需要网络通信|
|数据共享|不同 JVM 之间无法直接共享|多个服务实例可以共享|
|内存容量|受应用 JVM 内存限制|受 Redis 实例或集群内存限制|
|数据一致性|多实例同步比较困难|共享同一份缓存，较容易管理|
|持久化|通常不持久化|支持 RDB、AOF|
|常见技术|Caffeine、Guava Cache|Redis|
|适用场景|高频读取、变化较少的数据|分布式系统中的共享缓存|

这里要注意：**Redis 共享缓存不代表 Redis 与 MySQL 的数据天然一致**，仍然需要通过 Cache-Aside 等策略维护一致性。

---

## **四、为什么本地缓存会有数据一致性问题？**

假设你部署了两个 Spring Boot 实例：

```text
Spring Boot A          Spring Boot B
     │                      │
     ▼                      ▼
本地缓存：价格100元     本地缓存：价格100元
```

此时，管理员将商品价格修改为 200 元。

Spring Boot A 更新了数据库，并删除了自己的本地缓存：

```text
Spring Boot A          Spring Boot B
     │                      │
     ▼                      ▼
本地缓存：已删除       本地缓存：价格100元
     │                      │
     ▼                      │
MySQL：价格200元             │
```

问题出现了：

**Spring Boot B 不知道数据已经发生变化，仍然可能返回旧价格。**

如果使用 Redis：

```text
Spring Boot A ──┐
                │
                ▼
            Redis 缓存
                ▲
                │
Spring Boot B ──┘
```

当 A 删除 Redis 中的商品缓存后，B 再次查询时也无法命中这条旧缓存，就可以重新从 MySQL 加载数据。

因此，**在多实例部署的场景下，Redis 通常比本地缓存更容易维护数据一致性。**

---

## **五、实际项目中能不能同时使用？**

**可以，这就是多级缓存。**

例如：

```text
           用户请求
               │
               ▼
         Spring Boot
               │
               ▼
        ① 本地缓存
          （Caffeine）
               │
             未命中
               ▼
         ② Redis 缓存
               │
             未命中
               ▼
          ③ MySQL
```

查询顺序：

1. 优先查询本地缓存，速度最快。
2. 本地缓存未命中，查询 Redis。
3. Redis 未命中，查询 MySQL。
4. 将查询结果写入缓存，方便后续访问。

这种方式可以同时利用本地缓存和 Redis 的优势。

不过，多级缓存也会引入新的问题：**当 MySQL 数据发生修改时，需要考虑如何同步失效本地缓存和 Redis 缓存。**

因此，并不是缓存层数越多越好。

---

## Q：

本地缓存和 Redis 缓存主要有三个区别。

第一，存储位置不同。本地缓存存储在应用程序的 JVM 内存中，而 Redis 缓存存储在独立的 Redis 服务中。

第二，访问速度不同。本地缓存不需要网络通信，因此通常比 Redis 更快。

第三，数据共享能力不同。本地缓存只能被当前应用实例直接访问，而 Redis 可以被多个服务实例共享，因此更适合分布式系统。

不过，本地缓存存在多实例数据一致性问题，而 Redis 需要额外的网络通信。

实际项目中，如果数据访问频率很高、变化较少，可以使用 Caffeine 本地缓存；如果需要多个服务共享缓存，可以使用 Redis；如果性能要求更高，也可以采用 Caffeine + Redis 的多级缓存方案。

**一句话记忆：本地缓存速度快，但不方便共享；Redis 缓存需要网络通信，但适合分布式系统。**