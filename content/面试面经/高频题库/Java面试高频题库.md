<!-- java-interview-daily:generated:v1 -->

# Java面试高频题库

频次=实际采集且已核实正文的不同面经数；不是提问条数、生成次数或项目练习次数。已有答案复用，新增角度需由Agent复核后修订。

当前来源 38 篇；归一问题 181 题。

| 问题 | 次数 | 领域 |
| --- | --- | --- |
| [HashMap 的存储与查找原理](#hashmap-core-mechanism) | 9 | Java 基础与集合 |
| [数据库查询如何调优](#mysql-query-tuning-workflow) | 7 | MySQL |
| [JVM运行时内存区域](#jvm-runtime-memory-areas) | 6 | Java 并发与 JVM |
| [如何介绍项目的技术设计](#project-technical-introduction) | 6 | 项目设计与技术选型 |
| [Java创建和执行线程任务的方式](#java-thread-creation) | 5 | Java 并发与 JVM |
| [线程池提交任务流程与拒绝策略](#thread-pool-submit-rejection) | 5 | Java 并发与 JVM |
| [ArrayList与LinkedList的区别及场景](#arraylist-versus-linkedlist) | 4 | Java 基础与集合 |
| [后端如何选择并发控制方式](#backend-locking-choices) | 4 | Java 并发与 JVM |
| [List、Set与Map的区别](#java-list-set-map-contracts) | 4 | Java 基础与集合 |
| [面向对象的理解与价值](#java-object-oriented-basics) | 4 | Java 基础与集合 |
| [Java基本类型与包装类](#java-primitive-wrappers) | 4 | Java 基础与集合 |
| [事务的ACID特性](#mysql-transaction-acid) | 4 | MySQL |
| [Spring AOP的作用与实现](#spring-aop-concept) | 4 | Spring / Spring Boot / MyBatis |
| [自定义线程池与七个核心参数](#thread-pool-configuration) | 4 | Java 并发与 JVM |
| [ThreadLocal的场景与风险](#threadlocal-scenarios-risks) | 4 | Java 并发与 JVM |
| [如何保证缓存与数据库的一致性](#cache-database-consistency) | 3 | Redis |
| [类加载、链接与初始化](#class-loading-process) | 3 | Java 并发与 JVM |
| [ConcurrentHashMap如何保证并发安全](#concurrenthashmap-jdk8-mechanism) | 3 | Java 并发与 JVM |
| [HashMap如何扩容](#hashmap-resize-jdk8) | 3 | Java 基础与集合 |
| [JVM的职责](#jvm-basic-responsibility) | 3 | Java 并发与 JVM |
| [Spring如何使用声明式事务](#spring-declarative-transaction) | 3 | Spring / Spring Boot / MyBatis |
| [Spring事务不生效与不回滚的场景](#spring-transaction-proxy-failure) | 3 | Spring / Spring Boot / MyBatis |
| [如何避免重复下单或重复预约](#business-request-idempotency) | 2 | 项目设计与技术选型 |
| [缓存穿透、击穿与雪崩的区别及应对](#cache-penetration-breakdown-avalanche) | 2 | Redis |
| [数据库乐观锁与悲观锁如何选择](#database-optimistic-pessimistic-lock) | 2 | MySQL |
| [垃圾判活与回收的基本机制](#gc-collection-mechanism) | 2 | Java 并发与 JVM |
| [HashMap并发修改有哪些风险](#hashmap-concurrent-modification-risks) | 2 | Java 基础与集合 |
| [HashMap与Hashtable的区别](#hashmap-versus-hashtable) | 2 | Java 基础与集合 |
| [HTTP、HTTPS与TLS握手](#https-tls-handshake) | 2 | 计算机网络与操作系统 |
| [Java如何实现一次编译到处执行](#java-bytecode-portability) | 2 | Java 基础与集合 |
| [方法重载与重写的区别](#java-overload-versus-override) | 2 | Java 基础与集合 |
| [Java引用类型与垃圾回收](#java-reference-strengths) | 2 | Java 并发与 JVM |
| [Java反射的原理与应用场景](#java-reflection-use-cases) | 2 | Java 基础与集合 |
| [常见集合中哪些支持线程安全访问](#java-thread-safe-collections) | 2 | Java 基础与集合 |
| [Java常用版本与Java 17特性](#java-version-features) | 2 | Java 基础与集合 |
| [OOM 与频繁 GC 如何排查](#jvm-oom-gc-troubleshooting) | 2 | Java 并发与 JVM |
| [为什么使用消息队列](#mq-business-use-cases) | 2 | RabbitMQ / 消息队列 |
| [如何保证消息消费幂等](#mq-consumer-idempotence) | 2 | RabbitMQ / 消息队列 |
| [MyBatis与MyBatis-Plus的区别](#mybatis-plus-versus-mybatis) | 2 | Spring / Spring Boot / MyBatis |
| [MySQL的B+树索引为什么快](#mysql-bplus-tree-index) | 2 | MySQL |
| [联合索引中的等值、范围与条件书写顺序](#mysql-composite-equality-range) | 2 | MySQL |
| [索引的优点与代价](#mysql-index-benefits-costs) | 2 | MySQL |
| [MySQL索引的分类与使用](#mysql-index-types) | 2 | MySQL |
| [MySQL常见存储引擎及区别](#mysql-storage-engine-comparison) | 2 | MySQL |
| [Redis常用基本数据类型](#redis-basic-data-types) | 2 | Redis |
| [Lua在Redis Cluster中的约束](#redis-lua-cluster-safety) | 2 | Redis |
| [Spring Boot自动配置原理](#spring-boot-auto-configuration) | 2 | Spring / Spring Boot / MyBatis |
| [DispatcherServlet的作用](#springmvc-dispatcherservlet) | 2 | Spring / Spring Boot / MyBatis |
| [策略模式的好处与边界](#strategy-pattern-benefits) | 2 | 项目设计与技术选型 |
| [synchronized与锁优化](#synchronized-lock-optimization-states) | 2 | Java 并发与 JVM |
| [synchronized与ReentrantLock的区别](#synchronized-versus-reentrantlock) | 2 | Java 并发与 JVM |
| [为什么使用线程池](#thread-pool-benefits) | 2 | Java 并发与 JVM |
| [AI 生成代码持续不符合要求怎么办](#ai-coding-requirement-iteration) | 1 | 其他问题 |
| [AI 代码能运行就能直接用于业务吗](#ai-generated-code-acceptance) | 1 | 其他问题 |
| [二叉树直径如何计算](#algorithm-binary-tree-diameter) | 1 | 其他问题 |
| [冒泡排序的实现与复杂度](#algorithm-bubble-sort) | 1 | 其他问题 |
| [利用栈求表达式的值](#algorithm-expression-stack-evaluation) | 1 | 其他问题 |
| [斐波那契数有哪些计算方法](#algorithm-fibonacci-methods) | 1 | 其他问题 |
| [堆排序的步骤与复杂度](#algorithm-heap-sort) | 1 | 其他问题 |
| [大文件共有数字如何求解](#algorithm-large-file-common-numbers) | 1 | 其他问题 |
| [内存受限时求两个大文件的共有字符串](#algorithm-large-file-common-strings) | 1 | 其他问题 |
| [最长升序子序列](#algorithm-longest-increasing-subsequence) | 1 | 其他问题 |
| [用队列实现栈](#algorithm-queue-implements-stack) | 1 | 其他问题 |
| [成对数字中的唯一数及三次变体](#algorithm-single-number-frequency) | 1 | 其他问题 |
| [手写栈的实现](#algorithm-stack-implementation) | 1 | 其他问题 |
| [树中两节点的最短路径](#algorithm-tree-two-node-shortest-path) | 1 | 其他问题 |
| [后端错误如何返回并在前端展示](#api-error-response) | 1 | Spring / Spring Boot / MyBatis |
| [AQS是什么](#aqs-synchronizer-framework) | 1 | Java 并发与 JVM |
| [单体与微服务开发的区别](#architecture-monolith-microservice-difference) | 1 | 项目设计与技术选型 |
| [单体是否需要拆分及如何划分服务](#architecture-service-split) | 1 | 项目设计与技术选型 |
| [ArrayList 与 HashSet 的区别](#arraylist-versus-hashset) | 1 | Java 基础与集合 |
| [异常处理如何提供有用信息并保证业务一致性](#backend-exception-handling-design) | 1 | 项目设计与技术选型 |
| [后端日志应该记录什么与遵循哪些规范](#backend-logging-practices) | 1 | 项目设计与技术选型 |
| [如何降低布隆过滤器假阳性概率](#bloom-filter-false-positive-tuning) | 1 | Redis |
| [逻辑过期的 key 不设置 TTL 有什么问题](#cache-logical-expiration-costs) | 1 | Redis |
| [CAS与synchronized的区别](#cas-versus-synchronized) | 1 | Java 并发与 JVM |
| [数据库分表如何设计](#database-sharding-design) | 1 | MySQL |
| [常见数据库类型及适用场景](#database-types-relational-nosql) | 1 | MySQL |
| [项目中分布式锁的实际用法](#distributed-lock-project-usage) | 1 | Redis |
| [Docker常用命令](#docker-common-commands) | 1 | 计算机网络与操作系统 |
| [Elasticsearch的基本用途与结构](#elasticsearch-basic-overview) | 1 | 其他问题 |
| [BM25与KNN检索原理](#es-bm25-knn-retrieval) | 1 | 其他问题 |
| [G1如何划分堆内存](#g1-region-generations) | 1 | Java 并发与 JVM |
| [常见垃圾回收算法](#gc-basic-algorithms) | 1 | Java 并发与 JVM |
| [GC Roots与引用计数的局限](#gc-roots-reference-counting) | 1 | Java 并发与 JVM |
| [Git 版本回退如何选择 revert 与 reset](#git-revert-versus-reset) | 1 | 其他问题 |
| [HashMap指定初始容量13时的数组长度](#hashmap-initial-capacity-rounding) | 1 | Java 基础与集合 |
| [HashMap负载因子的取舍](#hashmap-load-factor-tradeoff) | 1 | Java 基础与集合 |
| [HashMap是否允许null键与null值](#hashmap-null-key-value) | 1 | Java 基础与集合 |
| [HashSet 在 JDK 7 与 JDK 8 中的实现](#hashset-jdk-implementation) | 1 | Java 基础与集合 |
| [HTTP/1.1与HTTP/2的区别](#http11-versus-http2) | 1 | 计算机网络与操作系统 |
| [如何解决超卖](#inventory-overselling-prevention) | 1 | 项目设计与技术选型 |
| [受检异常与运行时异常的区别](#java-checked-unchecked-exceptions) | 1 | Java 基础与集合 |
| [什么是死锁以及如何减少死锁](#java-deadlock-prevention) | 1 | Java 并发与 JVM |
| [JDK动态代理与CGLIB的区别](#java-dynamic-proxy-jdk-cglib) | 1 | Spring / Spring Boot / MyBatis |
| [== 与 equals 的区别](#java-equals-versus-reference) | 1 | Java 基础与集合 |
| [Java异常体系如何分类](#java-exception-hierarchy) | 1 | Java 基础与集合 |
| [final修饰变量、方法与类的含义](#java-final-semantics) | 1 | Java 基础与集合 |
| [try中return后finally是否执行](#java-finally-return-semantics) | 1 | Java 基础与集合 |
| [Java泛型的T、问号与extends](#java-generics-bounds) | 1 | Java 基础与集合 |
| [按商品种类计算平均价格](#java-group-average-price) | 1 | Java 基础与集合 |
| [接口与抽象类有什么区别](#java-interface-versus-abstract-class) | 1 | Java 基础与集合 |
| [项目为何选择某个JDK版本](#java-jdk-selection) | 1 | 项目设计与技术选型 |
| [Java内存模型与happens-before](#java-memory-model-happens-before) | 1 | Java 并发与 JVM |
| [线程获取的对象监视器锁对应什么](#java-monitor-lock-target) | 1 | Java 并发与 JVM |
| [多线程是否更快及CPU与IO任务如何选线程数](#java-multithreading-workload-selection) | 1 | Java 并发与 JVM |
| [notify与notifyAll有什么区别](#java-notify-versus-notifyall) | 1 | Java 并发与 JVM |
| [Java多态的实现](#java-polymorphism-method-dispatch) | 1 | Java 基础与集合 |
| [对象序列化的机制与用途](#java-serialization-purpose) | 1 | Java 基础与集合 |
| [多个线程操作同一个变量可能发生什么](#java-shared-variable-races) | 1 | Java 并发与 JVM |
| [static关键字的含义](#java-static-semantics) | 1 | Java 基础与集合 |
| [线程是什么及使用线程的好处](#java-thread-definition-benefits) | 1 | Java 并发与 JVM |
| [volatile的可见性与重排序约束](#java-volatile-ordering) | 1 | Java 并发与 JVM |
| [堆的分代与不同收集器布局](#jvm-heap-generations) | 1 | Java 并发与 JVM |
| [JVM内存区域为何区分线程私有与共享](#jvm-memory-layout-design) | 1 | Java 并发与 JVM |
| [JWT的用途、结构与校验](#jwt-structure-and-validation) | 1 | Spring / Spring Boot / MyBatis |
| [如何用 JMeter 验证一人一单和不超卖](#load-test-order-invariants) | 1 | 项目设计与技术选型 |
| [消息队列如何降低消息丢失风险](#mq-reliable-delivery) | 1 | RabbitMQ / 消息队列 |
| [MyBatis的井号与美元参数占位区别](#mybatis-hash-dollar-parameters) | 1 | Spring / Spring Boot / MyBatis |
| [MyBatis如何从Mapper方法执行SQL](#mybatis-mapper-execution) | 1 | Spring / Spring Boot / MyBatis |
| [MyBatis如何传递多个参数](#mybatis-multiple-parameters) | 1 | Spring / Spring Boot / MyBatis |
| [如何用条件UPDATE防止库存扣成负数](#mysql-conditional-stock-update) | 1 | MySQL |
| [SELECT COUNT(*)经过哪些执行节点](#mysql-count-execution-pipeline) | 1 | MySQL |
| [如何利用覆盖索引减少回表](#mysql-covering-index-avoid-lookup) | 1 | MySQL |
| [不同MySQL存储引擎如何存放索引与数据](#mysql-engine-index-storage) | 1 | MySQL |
| [EXPLAIN执行计划怎么看](#mysql-explain-plan-reading) | 1 | MySQL |
| [如何统计每个年级各班的学生数](#mysql-group-by-class-count) | 1 | MySQL |
| [如何查询学生总分最高者并保留并列](#mysql-group-sum-top-ties) | 1 | MySQL |
| [哪些情况使索引难以有效定位数据](#mysql-index-unusable-scenarios) | 1 | MySQL |
| [INNER JOIN与LEFT JOIN的结果差异](#mysql-inner-left-join) | 1 | MySQL |
| [InnoDB有哪些锁及锁定范围](#mysql-innodb-lock-types) | 1 | MySQL |
| [LIKE查询是否一定无法使用索引](#mysql-like-index-range) | 1 | MySQL |
| [InnoDB的MVCC如何工作](#mysql-mvcc-consistent-read) | 1 | MySQL |
| [MySQL如何分页查询](#mysql-pagination-offset-keyset) | 1 | MySQL |
| [事务的四种隔离级别](#mysql-transaction-isolation-levels) | 1 | MySQL |
| [UNION与UNION ALL的区别](#mysql-union-versus-union-all) | 1 | MySQL |
| [Nacos的注册发现与配置作用](#nacos-registry-config) | 1 | Spring / Spring Boot / MyBatis |
| [乐观锁的思想与实现](#optimistic-concurrency-control) | 1 | Java 并发与 JVM |
| [CPU调度的基本单位是什么](#os-thread-scheduling-unit) | 1 | 计算机网络与操作系统 |
| [如何说明Java优势在项目中的实际运用](#project-java-language-benefits) | 1 | 项目设计与技术选型 |
| [如何说明消息异步驱动的数据库更新内容](#project-mq-database-update-boundary) | 1 | 项目设计与技术选型 |
| [项目中的多线程如何实现与说明](#project-multithreading-implementation) | 1 | 项目设计与技术选型 |
| [项目角色数量与权限模型设计](#project-role-model) | 1 | 项目设计与技术选型 |
| [如何讲述项目难点与解决过程](#project-technical-problem-solving) | 1 | 项目设计与技术选型 |
| [如何说明项目中的ThreadLocal用途](#project-threadlocal-usage-evidence) | 1 | 项目设计与技术选型 |
| [Spring AI与RAG的问答链路](#rag-query-pipeline) | 1 | 项目设计与技术选型 |
| [缓存删除后大量请求回源怎么办](#redis-cache-breakdown) | 1 | Redis |
| [Redis的特点与使用边界](#redis-characteristics-tradeoffs) | 1 | Redis |
| [Redis Cluster的哈希槽](#redis-cluster-hash-slots) | 1 | Redis |
| [Redis分布式锁的原理与配置](#redis-distributed-lock-mechanism) | 1 | Redis |
| [Redis过期与内存淘汰的区别](#redis-expiration-and-eviction) | 1 | Redis |
| [HyperLogLog的用途与原理](#redis-hyperloglog-principle) | 1 | Redis |
| [分布式锁的租期与续期](#redis-lock-lease-renewal) | 1 | Redis |
| [分布式锁与随机TTL](#redis-lock-random-ttl) | 1 | Redis |
| [Lua库存预扣与MySQL扣库存如何取舍](#redis-lua-stock-admission) | 1 | Redis |
| [Redis内存不足如何定位与处理](#redis-memory-exhaustion-troubleshooting) | 1 | Redis |
| [Redis的RDB与AOF持久化](#redis-persistence-rdb-aof) | 1 | Redis |
| [Redis在项目中的用途](#redis-project-purposes) | 1 | Redis |
| [微博热搜排行榜如何存储和更新](#redis-ranking-design) | 1 | Redis |
| [Redis Set 与 ZSet 的区别](#redis-set-versus-zset) | 1 | Redis |
| [Redis Set与ZSet的底层编码如何选择](#redis-set-zset-encoding-comparison) | 1 | Redis |
| [如何说明Redis主从、哨兵与分片部署](#redis-topology-deployment-discussion) | 1 | Redis |
| [ZSet场景、编码与跳跃表](#redis-zset-skiplist) | 1 | Redis |
| [RocketMQ的核心架构组件有哪些](#rocketmq-architecture-components) | 1 | RabbitMQ / 消息队列 |
| [RPC为何看起来像调用本地方法](#rpc-invocation-pipeline) | 1 | 计算机网络与操作系统 |
| [倒排索引是什么](#search-inverted-index) | 1 | 其他问题 |
| [后端如何每15秒向前端推送消息](#server-periodic-push) | 1 | 计算机网络与操作系统 |
| [单点登录如何实现](#single-sign-on-design) | 1 | 项目设计与技术选型 |
| [单例模式与线程安全](#singleton-pattern-thread-safety) | 1 | Java 基础与集合 |
| [AOP通知类型与环绕通知](#spring-aop-advice-types) | 1 | Spring / Spring Boot / MyBatis |
| [Spring Boot的核心机制](#spring-boot-core-mechanisms) | 1 | Spring / Spring Boot / MyBatis |
| [Spring常见注解及职责](#spring-common-annotations) | 1 | Spring / Spring Boot / MyBatis |
| [PostConstruct的作用与时机](#spring-postconstruct-lifecycle) | 1 | Spring / Spring Boot / MyBatis |
| [应用启动后执行初始化逻辑](#spring-startup-runner) | 1 | Spring / Spring Boot / MyBatis |
| [如何防止SQL注入](#sql-injection-prevention) | 1 | MySQL |
| [SQLite与MySQL如何选型](#sqlite-versus-mysql-selection) | 1 | 项目设计与技术选型 |
| [TCP与UDP的区别](#tcp-versus-udp) | 1 | 计算机网络与操作系统 |
| [线程interrupt的作用](#thread-interrupt-cooperative-cancel) | 1 | Java 并发与 JVM |
| [订单和本地消息表为何放在同一事务](#transactional-outbox-pattern) | 1 | RabbitMQ / 消息队列 |
| [输入URL到页面显示会经历哪些过程](#web-url-request-lifecycle) | 1 | 计算机网络与操作系统 |
| [WebSocket与普通HTTP的区别](#websocket-versus-http) | 1 | 计算机网络与操作系统 |

<a id="hashmap-core-mechanism"></a>

## hashmap-core-mechanism · HashMap 的存储与查找原理

**次数**：9；**领域**：Java 基础与集合。

**A（AI参考答案）**：HashMap 根据键的哈希值定位桶，再通过 equals 区分发生冲突的键。JDK 8 中桶采用链表或红黑树，链较长且数组容量足够时才树化，容量不足时优先扩容；元素数量超过容量与负载因子的乘积也会触发扩容。哈希分布均匀时查询平均接近 O(1)，但不能保证所有场景都为常数时间。它允许 null 键和值，不保证遍历顺序，也不适合并发修改。

**🔍 面试追问（AI生成）**：
- 为什么不能修改已经作为键的对象的判等字段？ **简答**：修改后计算出的哈希位置或 equals 结果可能与插入时不同，导致原有映射难以正常查找和删除。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）
- [熙牛医疗 杭州java实习生 一面面经 2026.9.3](https://www.nowcoder.com/feed/main/detail/6512d3ef462a49cbb0aa5167d57d372f)（采集日 2026-10-25，熙牛医疗）
- [华盛通JAVA实习生二面](https://www.nowcoder.com/feed/main/detail/fd30324de36044c69ab16437026163d4)（采集日 2026-10-25，华盛通）
- [北森客开实习生(实习转正) 2026.10.13](https://www.nowcoder.com/feed/main/detail/cecac304535c4b3c99e6ff117908251e)（采集日 2026-10-28，北森）
- [阿里菜鸟实习Java一面面经](https://www.nowcoder.com/discuss/353157949398917120)（采集日 2026-10-30，阿里菜鸟）
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="mysql-query-tuning-workflow"></a>

## mysql-query-tuning-workflow · 数据库查询如何调优

**次数**：7；**领域**：MySQL。

**A（AI参考答案）**：先从慢查询日志和监控定位高耗时、高调用量SQL，再用EXPLAIN检查访问路径、扫描行数、连接顺序和索引使用，结合真实数据分布判断瓶颈。常见改进包括减少返回列与数据量、设计匹配过滤和排序条件的联合索引、避免不必要回表及优化分页。修改后验证结果一致性、实际延迟和写入成本；没有实测就说明方法，不编造优化百分比或个人成果。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）
- [极兔后端一面](https://www.nowcoder.com/discuss/932663753219244032)（采集日 2026-10-29，极兔）
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）

<a id="jvm-runtime-memory-areas"></a>

## jvm-runtime-memory-areas · JVM运行时内存区域

**次数**：6；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：按JVM规范可说明程序计数器、虚拟机栈、本地方法栈、堆和方法区。计数器与栈随线程组织，堆和方法区通常在线程间共享；栈帧包含局部变量表、操作数栈等，堆主要存放对象和数组。方法区是规范概念，HotSpot在Java8后主要以元空间承载类元数据，不能把元空间当作堆内老年代。直接内存也不能简单列成规范规定的第六块运行时区域。

版本口径：JVM规范概念与HotSpot Java 8实现分开说明。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [唯智信息技术 Java开发实习生 一面面经 2026.9.16](https://www.nowcoder.com/feed/main/detail/e00abf3b34e94e4398194442a9a826fb)（采集日 2026-10-21，唯智信息技术）
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））
- [佛山宏旺 java实习生](https://www.nowcoder.com/feed/main/detail/5083b0fbb75e480db6e8db2bbafc1195)（采集日 2026-10-27，佛山宏旺（原文标题））
- [极兔后端一面](https://www.nowcoder.com/discuss/932663753219244032)（采集日 2026-10-29，极兔）
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）

<a id="project-technical-introduction"></a>

## project-technical-introduction · 如何介绍项目的技术设计

**次数**：6；**领域**：项目设计与技术选型。

**A（AI参考答案）**：通用AI参考思路：先说明业务目标、核心流程和本人负责的技术模块，再解释架构、数据模型、接口及关键技术选型，结合一个真实难点说明方案、取舍与验证方式。原文没有披露完整项目实现，不能据此断言采用了微服务、缓存或消息队列，也不能编造性能指标；回答者应以自己实际做过、能够展示代码依据的内容展开，区分已实现能力与后续优化建议。

**实际来源**：
- [神州信息 java实习生面经（已offer）](https://www.nowcoder.com/discuss/353159627783217152)（采集日 2026-10-30，神州信息）
- [美团后台开发Java 实习面经](https://www.nowcoder.com/discuss/353156179603955712)（采集日 2026-10-30，美团）
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））
- [浪潮暑期实习java开发面经](https://www.nowcoder.com/discuss/353156399897190400)（采集日 2026-11-03，浪潮）
- [阅文面试结束，一共四面[Java]](https://www.nowcoder.com/discuss/353155938444058624)（采集日 2026-11-03，阅文）

<a id="java-thread-creation"></a>

## java-thread-creation · Java创建和执行线程任务的方式

**次数**：5；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：可继承Thread重写run，或把Runnable交给Thread后调用start；需要返回值时可用Callable配合FutureTask或提交给ExecutorService。Runnable、Callable描述任务，本身不是操作系统线程；调用run只是当前线程普通方法调用，start才请求启动新线程。实际工程常使用受控线程池复用线程，并处理任务异常、超时和关闭流程，不能无界地为每个请求新建线程。

版本口径：Java 8口径，不把后续JDK虚拟线程写成两个项目已使用的实现。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [27届学院本Agent秋招（OC已拒）](https://www.nowcoder.com/discuss/932329388496945152)（采集日 2026-10-26，匿名公司）
- [几百人小厂Java实习面经 第50场面!](https://www.nowcoder.com/feed/main/detail/a2476f1aebb84c9191ab53717464f55c)（采集日 2026-10-29，武汉众智鸿图）
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）

<a id="thread-pool-submit-rejection"></a>

## thread-pool-submit-rejection · 线程池提交任务流程与拒绝策略

**次数**：5；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：提交任务时，若工作线程少于核心数就尝试创建核心线程；否则尝试入队。入队成功后还会复查运行状态与工作线程情况；入队失败则尝试创建非核心线程，达到上限或无法接收时执行拒绝策略。Java内置Abort、CallerRuns、Discard和DiscardOldest。选择要结合业务是否允许丢任务，不能默认静默丢弃；关闭中的线程池也可能拒绝任务。

版本口径：Java 8 ThreadPoolExecutor。

**🔍 面试追问（AI生成）**：
- CallerRuns一定适合吗？ **简答**：它可能让调用线程执行任务从而施加反压，但会占用请求线程；线程池关闭时也不是可靠持久化机制。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）
- [极兔后端一面](https://www.nowcoder.com/discuss/932663753219244032)（采集日 2026-10-29，极兔）

<a id="arraylist-versus-linkedlist"></a>

## arraylist-versus-linkedlist · ArrayList与LinkedList的区别及场景

**次数**：4；**领域**：Java 基础与集合。

**A（AI参考答案）**：ArrayList基于可扩容数组，按下标访问为O(1)，尾部追加通常是摊销O(1)，中间插入删除需要移动元素。LinkedList基于双向链表，按下标定位仍为O(n)，只有已经定位节点或在两端操作时，链接调整才是O(1)，不能笼统说插入一定更快。一般列表优先ArrayList；需要双端操作可比较ArrayDeque等实现。两者都不自动保证并发安全，选择时还要考虑节点内存和缓存局部性。

**实际来源**：
- [26届 小厂java实习面经](https://www.nowcoder.com/discuss/862367705284816896)（采集日 2026-10-29，深圳市中科保泰科技有限公司）
- [用友金融一面](https://www.nowcoder.com/feed/main/detail/b087698fedff49668324389ed50f3829)（采集日 2026-10-29，用友金融）
- [京东物流java实习一面面经](https://www.nowcoder.com/discuss/353157644422684672)（采集日 2026-10-30，京东物流）
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）

<a id="backend-locking-choices"></a>

## backend-locking-choices · 后端如何选择并发控制方式

**次数**：4；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：先明确竞争的数据和作用范围。单进程内共享变量可用synchronized或ReentrantLock，跨实例共同修改数据库时，优先考虑原子条件更新、唯一约束或数据库行锁；确需协调跨节点任务时再评估分布式锁。选择时还要看事务边界、锁粒度、超时与死锁处理。加锁只能保护参与同一协议的访问，不能拿到锁就认为重复请求、远程调用失败和业务幂等都已解决。

**🔍 面试追问（AI生成）**：
- 为什么多实例不能只用synchronized保护数据库余额？ **简答**：监视器只协调当前JVM，另一实例仍可同时更新同一行。应让竞争请求在同一数据库约束或其他共享协调机制下竞争。

**实际来源**：
- [健康160-JAVA开发实习生](https://www.nowcoder.com/discuss/943496145010020352)（采集日 2026-10-25，健康160）
- [用友 Java实习面经](https://www.nowcoder.com/discuss/784203612955090944)（采集日 2026-11-01，用友）
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）

<a id="java-list-set-map-contracts"></a>

## java-list-set-map-contracts · List、Set与Map的区别

**次数**：4；**领域**：Java 基础与集合。

**A（AI参考答案）**：List表示有序序列，通常允许重复元素，可按下标访问；Set主要表达元素唯一性；Map保存键值映射，键唯一而值可以重复，Map本身不继承Collection。具体顺序和空值规则取决于实现：HashSet不保证迭代顺序，TreeSet按排序规则组织元素。HashMap或HashSet中的自定义键要正确实现equals与hashCode，并避免修改参与判等的字段。选择时先看是否需要位置、去重或按键查询，再考虑并发和性能。

**实际来源**：
- [神州信息 java实习生面经（已offer）](https://www.nowcoder.com/discuss/353159627783217152)（采集日 2026-10-30，神州信息）
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））

<a id="java-object-oriented-basics"></a>

## java-object-oriented-basics · 面向对象的理解与价值

**次数**：4；**领域**：Java 基础与集合。

**A（AI参考答案）**：面向对象把数据与操作数据的行为组织到对象中，通过封装隐藏实现细节，通过抽象和接口表达稳定契约，通过多态在调用方不依赖具体实现的情况下替换行为。它有助于控制复杂业务的职责与变化，但不是类越多越好；继承应满足合理的类型关系，复用行为也可优先组合。设计时围绕业务边界划分职责，避免所有逻辑集中在一个大类中。

**实际来源**：
- [终于找到实习了！](https://www.nowcoder.com/feed/main/detail/067e9a7c702a4c2eb87ac95c952bdea2)（采集日 2026-10-22，匿名小厂（作者自述））
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））
- [京东物流java实习一面面经](https://www.nowcoder.com/discuss/353157644422684672)（采集日 2026-10-30，京东物流）
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）

<a id="java-primitive-wrappers"></a>

## java-primitive-wrappers · Java基本类型与包装类

**次数**：4；**领域**：Java 基础与集合。

**A（AI参考答案）**：Java有byte、short、int、long、float、double、char、boolean八种基本类型，对应包装类为Byte、Short、Integer、Long、Float、Double、Character、Boolean。包装类可用于泛型和允许null的对象场景，自动装箱拆箱提供便利，但拆箱null会抛空指针异常。比较包装数值应关注equals语义，不能依赖引用相等或缓存范围；金额通常用BigDecimal并明确精度与舍入。

版本口径：Java 8基础口径；不把包装类缓存范围等同于所有数值都能用==比较。

**实际来源**：
- [唯智信息技术 Java开发实习生 一面面经 2026.9.16](https://www.nowcoder.com/feed/main/detail/e00abf3b34e94e4398194442a9a826fb)（采集日 2026-10-21，唯智信息技术）
- [26届 小厂java实习面经](https://www.nowcoder.com/discuss/862367705284816896)（采集日 2026-10-29，深圳市中科保泰科技有限公司）
- [神州信息 java实习生面经（已offer）](https://www.nowcoder.com/discuss/353159627783217152)（采集日 2026-10-30，神州信息）
- [京东物流java实习一面面经](https://www.nowcoder.com/discuss/353157644422684672)（采集日 2026-10-30，京东物流）

<a id="mysql-transaction-acid"></a>

## mysql-transaction-acid · 事务的ACID特性

**次数**：4；**领域**：MySQL。

**A（AI参考答案）**：ACID指原子性、一致性、隔离性和持久性。原子性要求事务操作整体提交或回滚；一致性要求满足业务规则和数据库约束，不能只靠开启事务自动得到。隔离性控制并发事务间的相互影响，强度取决于隔离级别；持久性要求提交后的结果能够按配置保障恢复。以InnoDB为例，可从undo、redo、锁和MVCC解释实现分工，避免把每项特性归因于单一日志。

**实际来源**：
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））
- [熙牛医疗 杭州java实习生 一面面经 2026.9.3](https://www.nowcoder.com/feed/main/detail/6512d3ef462a49cbb0aa5167d57d372f)（采集日 2026-10-25，熙牛医疗）
- [用友金融一面](https://www.nowcoder.com/feed/main/detail/b087698fedff49668324389ed50f3829)（采集日 2026-10-29，用友金融）
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）

<a id="spring-aop-concept"></a>

## spring-aop-concept · Spring AOP的作用与实现

**次数**：4；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：AOP把事务、日志或权限等横切逻辑从业务代码中分离，通过切点选择连接点并织入通知。Spring AOP通常基于JDK动态代理或CGLIB代理，在代理调用处增强方法，因此对象是否由容器管理、调用是否经过代理会影响增强生效。它不是修改所有类的任意代码位置，也不等同于完整的AspectJ编织；项目中的声明式事务可作为有代码依据的典型应用。

**实际来源**：
- [昆山java后端小厂面经](https://www.nowcoder.com/feed/main/detail/bcf78a7db16f4d22a7ce33aca1358876)（采集日 2026-10-22，匿名昆山小厂（标题自述））
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）
- [26届 小厂java实习面经](https://www.nowcoder.com/discuss/862367705284816896)（采集日 2026-10-29，深圳市中科保泰科技有限公司）
- [阿里菜鸟实习Java一面面经](https://www.nowcoder.com/discuss/353157949398917120)（采集日 2026-10-30，阿里菜鸟）

<a id="thread-pool-configuration"></a>

## thread-pool-configuration · 自定义线程池与七个核心参数

**次数**：4；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：ThreadPoolExecutor常见七个参数是corePoolSize、maximumPoolSize、keepAliveTime、时间单位、任务队列、ThreadFactory和拒绝处理器。配置需结合CPU或IO特征、下游容量、允许排队时间和资源限制，不能只套公式。优先使用有界队列，并给线程命名、监控活跃数和拒绝次数；长队列可能延迟扩容，最大线程数也不能超出系统可承受范围。

版本口径：Java 8 ThreadPoolExecutor。

**🔍 面试追问（AI生成）**：
- 无界队列有什么影响？ **简答**：在核心线程繁忙后通常持续入队，maximumPoolSize难以发挥预期扩容作用，还可能积压内存和延迟。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）

<a id="threadlocal-scenarios-risks"></a>

## threadlocal-scenarios-risks · ThreadLocal的场景与风险

**次数**：4；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：ThreadLocal为每个线程保存独立变量，常用于请求上下文或事务资源绑定，不负责让同一对象的并发访问自动安全。线程池会复用线程，任务结束后若不remove，旧数据可能串到下个任务；ThreadLocalMap的弱键也不能替代清理，因为值仍可能被线程长期引用。应在finally中清理，异步任务需要显式传递必要上下文，不能假设换线程后原值仍然可见。

**实际来源**：
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））
- [阿里菜鸟实习Java一面面经](https://www.nowcoder.com/discuss/353157949398917120)（采集日 2026-10-30，阿里菜鸟）
- [美团后台开发Java 实习面经](https://www.nowcoder.com/discuss/353156179603955712)（采集日 2026-10-30，美团）
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="cache-database-consistency"></a>

## cache-database-consistency · 如何保证缓存与数据库的一致性

**次数**：3；**领域**：Redis。

**A（AI参考答案）**：常见 Cache-Aside 方案以数据库为准：读取先查缓存，未命中再查库并回填；写入先提交数据库事务，再删除缓存，后续读取重建。删除失败需要可靠重试或消息补偿，并以 TTL 限制陈旧时间。并发读写仍可能出现旧值回填，所以它通常提供最终一致性，不能直接保证强一致；更高要求可结合版本校验、串行化更新，或对关键读取直接访问数据库，再根据延迟和业务容忍度选择方案。

**🔍 面试追问（AI生成）**：
- 延迟双删能否保证所有并发场景都不出现旧缓存？ **简答**：不能，延迟选择、失败和执行顺序仍可能出问题；它只是降低风险，不能代替一致性边界和可靠补偿。

**实际来源**：
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）
- [南京车300 Java 实习面经](https://www.nowcoder.com/feed/main/detail/8b78085106ae45a4bada11cb75141d8f)（采集日 2026-10-24，南京车300）
- [京东物流java实习一面面经](https://www.nowcoder.com/discuss/353157644422684672)（采集日 2026-10-30，京东物流）

<a id="class-loading-process"></a>

## class-loading-process · 类加载、链接与初始化

**次数**：3；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：通常按加载、链接和初始化说明，链接又包括验证、准备和解析。加载得到类的二进制表示；验证检查合法性；准备为类变量分配空间并设置初始值，解析把符号引用转换为直接引用；初始化再按规则执行类初始化逻辑。各阶段未必严格一次性完成，例如解析可延迟。类加载与对象实例化不同，静态字段赋值也不能都笼统说在加载阶段执行。

版本口径：Java 8/JVM规范基础口径。

**实际来源**：
- [唯智信息技术 Java开发实习生 一面面经 2026.9.16](https://www.nowcoder.com/feed/main/detail/e00abf3b34e94e4398194442a9a826fb)（采集日 2026-10-21，唯智信息技术）
- [阿里菜鸟实习Java一面面经](https://www.nowcoder.com/discuss/353157949398917120)（采集日 2026-10-30，阿里菜鸟）
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））

<a id="concurrenthashmap-jdk8-mechanism"></a>

## concurrenthashmap-jdk8-mechanism · ConcurrentHashMap如何保证并发安全

**次数**：3；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：以JDK 8为例，ConcurrentHashMap使用桶数组，冲突桶可为链表或树。空桶插入主要通过CAS竞争，非空桶更新会使用桶级同步，并配合可见性机制，使不同桶上的操作尽量并行；扩容时线程也可协助迁移。不能把JDK 7的Segment分段锁当成JDK 8实现。单次操作安全不代表先判断再写入的组合操作原子，应使用putIfAbsent、compute等合适接口，遍历和size也不能当成全表一致快照。

**🔍 面试追问（AI生成）**：
- 为什么不允许null键和值？ **简答**：可以避免并发读取时无法区分不存在映射与映射值为null的歧义，接口直接禁止这类输入。

**实际来源**：
- [熙牛医疗 杭州java实习生 一面面经 2026.9.3](https://www.nowcoder.com/feed/main/detail/6512d3ef462a49cbb0aa5167d57d372f)（采集日 2026-10-25，熙牛医疗）
- [北森客开实习生(实习转正) 2026.10.13](https://www.nowcoder.com/feed/main/detail/cecac304535c4b3c99e6ff117908251e)（采集日 2026-10-28，北森）
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="hashmap-resize-jdk8"></a>

## hashmap-resize-jdk8 · HashMap如何扩容

**次数**：3；**领域**：Java 基础与集合。

**A（AI参考答案）**：以JDK 8为例，HashMap通常在元素数量超过容量乘负载因子的阈值时扩容，新桶数组一般扩大为原来的两倍。迁移节点时利用容量为二的幂这一特点，检查哈希值与旧容量对应的位，节点留在原位置或移动到原下标加旧容量的位置，不需要重新调用键的hashCode。扩容有分配和迁移成本，可按预计规模设置初始容量；这些规则并不使HashMap具备并发安全性。

**实际来源**：
- [熙牛医疗 杭州java实习生 一面面经 2026.9.3](https://www.nowcoder.com/feed/main/detail/6512d3ef462a49cbb0aa5167d57d372f)（采集日 2026-10-25，熙牛医疗）
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））

<a id="jvm-basic-responsibility"></a>

## jvm-basic-responsibility · JVM的职责

**次数**：3；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：JVM负责执行Java字节码，提供类加载、运行时内存管理、解释与即时编译以及垃圾回收等能力。通常先由javac把源码编译为class文件，再由具体JVM实现加载和执行；跨平台来自统一字节码规范与各平台的JVM实现。回答时区分JDK开发工具、运行环境和JVM，也不要把Java内存模型JMM与JVM运行时内存区域混为一谈。

**实际来源**：
- [终于找到实习了！](https://www.nowcoder.com/feed/main/detail/067e9a7c702a4c2eb87ac95c952bdea2)（采集日 2026-10-22，匿名小厂（作者自述））
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）

<a id="spring-declarative-transaction"></a>

## spring-declarative-transaction · Spring如何使用声明式事务

**次数**：3；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：在Spring管理的业务Bean上使用Transactional，配置适用的事务管理器，再通过代理调用让多个数据库操作处于同一事务。需要明确传播行为、隔离级别与回滚规则；默认通常对RuntimeException和Error回滚，受检异常要按需要配置rollbackFor。数据库事务只能协调它管理的资源，不能因为同方法里也写了Redis或发MQ就认为它们会一起回滚。

版本口径：Spring代理事务，结合项目Spring Boot2.x；不扩展到未经核实的分布式事务框架。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [终于找到实习了！](https://www.nowcoder.com/feed/main/detail/067e9a7c702a4c2eb87ac95c952bdea2)（采集日 2026-10-22，匿名小厂（作者自述））
- [华盛通JAVA实习生二面](https://www.nowcoder.com/feed/main/detail/fd30324de36044c69ab16437026163d4)（采集日 2026-10-25，华盛通）

<a id="spring-transaction-proxy-failure"></a>

## spring-transaction-proxy-failure · Spring事务不生效与不回滚的场景

**次数**：3；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：先区分没有进入事务与进入后没有回滚。代理模式下，同类内部直接调用、对象不是Spring管理的Bean等会绕开事务代理；方法可见性和代理类型也要结合版本判断。已进入事务时，异常被业务捕获不再抛出，或受检异常未匹配回滚规则，可能不会按预期回滚。新线程不会自动继承当前线程事务。排查要看调用链、管理器与实际SQL，不能只看方法上有注解。

版本口径：项目Spring Boot2.x代理式事务；方法可见性规则不泛化为所有Spring新版本。

**🔍 面试追问（AI生成）**：
- 把注解加在private方法上就能修复吗？ **简答**：项目这种常见代理模式不能靠private方法注解获得预期拦截，应把事务边界放在可被代理调用的业务方法并验证。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）
- [极兔后端一面](https://www.nowcoder.com/discuss/932663753219244032)（采集日 2026-10-29，极兔）

<a id="business-request-idempotency"></a>

## business-request-idempotency · 如何避免重复下单或重复预约

**次数**：2；**领域**：项目设计与技术选型。

**A（AI参考答案）**：先明确哪些请求属于同一次业务操作，为它们分配稳定的业务请求号，在数据库建立唯一约束，并让业务写入与幂等记录在同一事务内完成。重复请求应查询并返回原结果，处理中则返回明确状态。Redis SET NX、短期令牌或前端按钮防抖可以减少重复流量，但锁过期、请求超时后重试仍可能发生，不能代替持久化约束。预约还要明确取消后能否再次预约，避免唯一键把合法操作一起拦住。

**🔍 面试追问（AI生成）**：
- 为什么不能直接把用户ID和商品ID设为订单唯一键？ **简答**：同一用户可能合法地再次购买；唯一键应表示同一次业务请求，而不是永久禁止重复购买。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）

<a id="cache-penetration-breakdown-avalanche"></a>

## cache-penetration-breakdown-avalanche · 缓存穿透、击穿与雪崩的区别及应对

**次数**：2；**领域**：Redis。

**A（AI参考答案）**：AI参考答案：穿透是反复查询缓存和数据库都不存在的数据，可用参数校验、短期空值缓存或布隆过滤器减少回源，注意误判及数据新增。击穿是热点键失效引发大量并发回源，可用互斥重建、预热或逻辑过期。雪崩是大量键集中失效或缓存整体故障，可通过过期时间打散、限流降级和高可用减轻影响。方案要明确容忍的旧数据时间和数据库承载能力，不能忽略超时与失败。

**实际来源**：
- [用友 Java实习面经](https://www.nowcoder.com/discuss/784203612955090944)（采集日 2026-11-01，用友）
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="database-optimistic-pessimistic-lock"></a>

## database-optimistic-pessimistic-lock · 数据库乐观锁与悲观锁如何选择

**次数**：2；**领域**：MySQL。

**A（AI参考答案）**：悲观锁先取得数据库锁再处理竞争，例如在InnoDB事务中使用SELECT ... FOR UPDATE读取需要修改的记录；锁范围受索引、条件与隔离级别影响，事务应尽量短。乐观锁通常通过版本号条件更新，更新时同时校验旧版本并递增版本，根据影响行数判断冲突，再按业务决定重试或返回失败。低冲突场景可减少等待，高冲突时重试成本可能较高。两者都需要正确事务边界，不能用普通先查后改代替并发控制。

**实际来源**：
- [京东物流java实习一面面经](https://www.nowcoder.com/discuss/353157644422684672)（采集日 2026-10-30，京东物流）
- [美团后台开发Java 实习面经](https://www.nowcoder.com/discuss/353156179603955712)（采集日 2026-10-30，美团）

<a id="gc-collection-mechanism"></a>

## gc-collection-mechanism · 垃圾判活与回收的基本机制

**次数**：2；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：Java通常通过从GC Roots出发的可达性分析判断对象是否仍被使用，不能只看引用计数，否则循环引用难以处理。确定可回收对象后，由具体收集器选择复制、清除或整理等方式处理；不同阶段可能需要暂停应用或并发执行。垃圾回收主要管理堆内存，不替代文件、网络连接等外部资源的显式关闭，也不能保证某个对象在指定时刻马上被回收。

版本口径：JVM基础机制；与“算法有哪些”相关但不是同一原题，不合并虚增同题次数。

**实际来源**：
- [唯智信息技术 Java开发实习生 一面面经 2026.9.16](https://www.nowcoder.com/feed/main/detail/e00abf3b34e94e4398194442a9a826fb)（采集日 2026-10-21，唯智信息技术）
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="hashmap-concurrent-modification-risks"></a>

## hashmap-concurrent-modification-risks · HashMap并发修改有哪些风险

**次数**：2；**领域**：Java 基础与集合。

**A（AI参考答案）**：AI参考答案：HashMap没有为并发修改提供同步保证，多线程put可能发生覆盖、丢更新或读取到不符合预期的结果，size和遍历也不能视为一致快照。JDK 7扩容的链表成环问题不能直接套到JDK 8，但8仍不是线程安全容器。共享可变映射应使用ConcurrentHashMap或统一外部锁，先查后改等复合业务也需原子API或完整加锁。

**实际来源**：
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="hashmap-versus-hashtable"></a>

## hashmap-versus-hashtable · HashMap与Hashtable的区别

**次数**：2；**领域**：Java 基础与集合。

**A（AI参考答案）**：HashMap通常不提供并发安全保证，允许一个null键和多个null值；Hashtable是较早的同步容器，通常通过方法级同步保护访问，不允许null键和值。两者都通过哈希组织映射，但不能把Hashtable的方法同步理解成多个调用组成的业务操作必然原子。现代并发场景常考虑ConcurrentHashMap及其原子API，选择时还要看遍历、一致性和复合操作要求，而不是只记线程安全与否。

**实际来源**：
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）

<a id="https-tls-handshake"></a>

## https-tls-handshake · HTTP、HTTPS与TLS握手

**次数**：2；**领域**：计算机网络与操作系统。

**A（AI参考答案）**：HTTPS通过TLS保护HTTP传输，提供身份认证、机密性和完整性。以常见TLS 1.3证书握手为例，双方协商参数，通常用ECDHE交换密钥材料、派生会话密钥，用RSA-PSS或ECDSA等签名完成身份验证，再用AES-GCM或ChaCha20-Poly1305等对称算法保护应用数据。还需校验证书信任链、域名和有效期；不能说全程公钥加密，也不能把旧版RSA密钥交换当成所有TLS版本通用流程。

**🔍 面试追问（AI生成）**：
- HTTPS能保证业务接口没有漏洞吗？ **简答**：不能。它主要保护传输链路，业务权限、输入校验和终端安全仍需单独处理。

**实际来源**：
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）
- [用友 Java实习面经](https://www.nowcoder.com/discuss/784203612955090944)（采集日 2026-11-01，用友）

<a id="java-bytecode-portability"></a>

## java-bytecode-portability · Java如何实现一次编译到处执行

**次数**：2；**领域**：Java 基础与集合。

**A（AI参考答案）**：AI参考答案：Java源码通常经javac编译为符合虚拟机规范的class字节码，各操作系统和处理器平台提供对应JVM，由其加载、解释或即时编译后执行，因此可复用同一份兼容字节码。可移植性依赖目标JVM支持该class版本，也依赖所需类库和外部资源；JNI、本地库、文件路径或平台相关行为仍可能限制跨平台。它不表示JVM本身无需针对平台实现，也不保证任意新版本字节码可在旧JVM运行。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）
- [Java 后端新手的第一次面试复盘](https://www.cnblogs.com/thr-0103/p/18113538)（采集日 2026-11-02，匿名公司）

<a id="java-overload-versus-override"></a>

## java-overload-versus-override · 方法重载与重写的区别

**次数**：2；**领域**：Java 基础与集合。

**A（AI参考答案）**：重载是在同一类或继承体系中使用相同方法名、不同参数列表，编译器根据声明类型和参数选择调用目标，不能只改变返回类型来重载。重写是子类对继承的实例方法提供兼容实现，调用时再按对象实际类型动态分派；返回类型需兼容，不能收紧访问权限或任意扩大受检异常范围。静态方法是隐藏而非实例方法重写，私有方法也不按普通重写规则参与动态分派。

**实际来源**：
- [27届学院本Agent秋招（OC已拒）](https://www.nowcoder.com/discuss/932329388496945152)（采集日 2026-10-26，匿名公司）
- [北森客开实习生(实习转正) 2026.10.13](https://www.nowcoder.com/feed/main/detail/cecac304535c4b3c99e6ff117908251e)（采集日 2026-10-28，北森）

<a id="java-reference-strengths"></a>

## java-reference-strengths · Java引用类型与垃圾回收

**次数**：2；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：通常区分强引用、软引用、弱引用和虚引用。对象若仍通过有效的强引用链从GC Roots可达，就不能当作垃圾回收；软引用对象在内存压力下可能被清理，弱引用不会阻止其所指对象被回收。虚引用的get始终返回null，常配合引用队列进行回收后的资源管理通知。具体回收时机由收集器决定，不能承诺一次GC必定回收；弱键也不代表容器里相关的强引用值会自动及时释放。

**实际来源**：
- [熙牛医疗 杭州java实习生 一面面经 2026.9.3](https://www.nowcoder.com/feed/main/detail/6512d3ef462a49cbb0aa5167d57d372f)（采集日 2026-10-25，熙牛医疗）
- [阿里菜鸟实习Java一面面经](https://www.nowcoder.com/discuss/353157949398917120)（采集日 2026-10-30，阿里菜鸟）

<a id="java-reflection-use-cases"></a>

## java-reflection-use-cases · Java反射的原理与应用场景

**次数**：2；**领域**：Java 基础与集合。

**A（AI参考答案）**：反射是在运行时通过Class等对象获取类、字段、构造器和方法信息，并按权限规则创建实例或调用成员。常见场景包括依赖注入、对象映射、注解解析、测试框架和动态代理的调用分发，使框架不必为每种业务类写死处理逻辑。代价是额外运行开销、访问检查和对成员名称的运行时依赖，应缓存元数据并控制使用范围；反射不会自动让对象线程安全。Java 9后的模块封装也可能限制深反射，不能假定setAccessible永远可用。

版本口径：Java 9+模块访问限制。

**实际来源**：
- [佛山宏旺 java实习生](https://www.nowcoder.com/feed/main/detail/5083b0fbb75e480db6e8db2bbafc1195)（采集日 2026-10-27，佛山宏旺（原文标题））
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）

<a id="java-thread-safe-collections"></a>

## java-thread-safe-collections · 常见集合中哪些支持线程安全访问

**次数**：2；**领域**：Java 基础与集合。

**A（AI参考答案）**：AI参考答案：常用ArrayList、HashMap、HashSet不提供并发修改安全保证。可按需求使用ConcurrentHashMap、CopyOnWriteArrayList或阻塞队列，也可用Collections的同步包装；Vector和Hashtable的方法虽有同步，复合操作仍可能产生竞争。并发Map的“先判断再写入”应使用putIfAbsent、compute等原子接口。CopyOnWrite适合读多写少，写入会复制数组；遍历同步包装集合通常仍需外部加同一把锁。

**实际来源**：
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="java-version-features"></a>

## java-version-features · Java常用版本与Java 17特性

**次数**：2；**领域**：Java 基础与集合。

**A（AI参考答案）**：应先如实说明使用版本。Java 8常见特性包括Lambda、Stream和新的日期时间API；升级到17可使用已正式发布的record、文本块、switch表达式和密封类，但这些特性并非都首次出现在17。Java 17是LTS版本，虚拟线程则到Java 21才正式发布。项目是否用到某项特性应以构建配置和源码为证，不能把可用特性说成已经使用。

**实际来源**：
- [终于找到实习了！](https://www.nowcoder.com/feed/main/detail/067e9a7c702a4c2eb87ac95c952bdea2)（采集日 2026-10-22，匿名小厂（作者自述））
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））

<a id="jvm-oom-gc-troubleshooting"></a>

## jvm-oom-gc-troubleshooting · OOM 与频繁 GC 如何排查

**次数**：2；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：先结合异常类型、GC 日志和监控区分堆不足、元空间、直接内存或线程资源耗尽，不能看到 OOM 就只调大堆。堆问题可分析堆转储中的大对象、支配关系和 GC Roots，判断是正常容量需求、分配过快还是对象被长期持有；频繁 GC 还需看回收后占用、停顿时间和分配速率。优先修复泄漏、无界队列等根因，再通过压测决定容量或收集器参数，抓取诊断数据也要控制线上开销。

**实际来源**：
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）
- [用友金融一面](https://www.nowcoder.com/feed/main/detail/b087698fedff49668324389ed50f3829)（采集日 2026-10-29，用友金融）

<a id="mq-business-use-cases"></a>

## mq-business-use-cases · 为什么使用消息队列

**次数**：2；**领域**：RabbitMQ / 消息队列。

**A（AI参考答案）**：消息队列常用于异步处理、服务解耦和削峰，让请求先完成必要的准入与落账，再由消费者处理后续任务。它会引入重复投递、积压、顺序和一致性问题，不能只说性能更高；要说明确认机制、失败重试、幂等、监控与补偿。用户必须立即得到最终结果或强事务提交时，不能把仅已入队解释为业务成功，需设计处理中状态或改用合适的同步链路。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="mq-consumer-idempotence"></a>

## mq-consumer-idempotence · 如何保证消息消费幂等

**次数**：2；**领域**：RabbitMQ / 消息队列。

**A（AI参考答案）**：消息可能因确认丢失或故障重试被重复投递，消费者应根据业务唯一标识判断是否已产生效果。常见做法是在同一数据库事务中写业务记录与去重记录，配合唯一约束、条件状态更新及冲突处理，事务成功后再确认消息。只在Redis写一个已消费标记会遇到标记与业务提交不同步的问题；分布式锁也不能代替持久化幂等，更不能据此声称消息只会投递一次。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））

<a id="mybatis-plus-versus-mybatis"></a>

## mybatis-plus-versus-mybatis · MyBatis与MyBatis-Plus的区别

**次数**：2；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：MyBatis负责SQL映射与结果封装，复杂查询通常通过XML或注解显式编写；MyBatis-Plus是在其基础上的增强，提供通用CRUD、条件构造器和分页等能力，减少重复代码，但不会让SQL设计、索引和事务问题自动消失。简单单表操作可用通用Mapper，复杂业务仍可写自定义SQL。应按项目依赖版本说明API，不把starter版本直接当作MyBatis核心版本。

版本口径：采云台MyBatis starter 2.2.0；研约通MyBatis-Plus 3.4.3。

**实际来源**：
- [28届Java后端实习面试](https://www.nowcoder.com/discuss/941324379416166400)（采集日 2026-10-21，百川云璟）
- [Java 后端新手的第一次面试复盘](https://www.cnblogs.com/thr-0103/p/18113538)（采集日 2026-11-02，匿名公司）

<a id="mysql-bplus-tree-index"></a>

## mysql-bplus-tree-index · MySQL的B+树索引为什么快

**次数**：2；**领域**：MySQL。

**A（AI参考答案）**：InnoDB常用B+树组织索引，节点按页存储、分支多，树通常较矮，查找只需访问较少层级的页；内部节点主要保存导航信息，叶子节点有序并支持相邻遍历，适合等值与范围查询。聚簇索引的叶子保存行数据，二级索引叶子通常保存主键，取非覆盖列可能需要回表。查询快还依赖选择性、缓存命中和执行计划，不能仅凭建了B+树就认定不会扫描大量记录。

**实际来源**：
- [华盛通JAVA实习生二面](https://www.nowcoder.com/feed/main/detail/fd30324de36044c69ab16437026163d4)（采集日 2026-10-25，华盛通）
- [美团后台开发Java 实习面经](https://www.nowcoder.com/discuss/353156179603955712)（采集日 2026-10-30，美团）

<a id="mysql-composite-equality-range"></a>

## mysql-composite-equality-range · 联合索引中的等值、范围与条件书写顺序

**次数**：2；**领域**：MySQL。

**A（AI参考答案）**：对联合索引(a,b,c,d)，条件a=1、b=2、c=5、d>6可形成前三列等值加最后一列范围的连续索引范围，WHERE里把d写在c前面通常不改变这一逻辑。关键是索引列顺序和谓词性质，而非文本先后。“范围后不能用”也不能理解成范围列本身失效；范围后列能否用于过滤、覆盖或ICP还需区分。最终是否选择该索引及扫描多少行，要结合EXPLAIN验证。

版本口径：MySQL 8.x / InnoDB；不把优化器一定选用某索引当作保证。

**🔍 面试追问（AI生成）**：
- 范围列后还有列就完全没用了吗？ **简答**：不一定能继续缩小连续扫描区间，但仍可能用于索引条件下推或覆盖查询；需区分访问范围与过滤。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [极兔后端一面](https://www.nowcoder.com/discuss/932663753219244032)（采集日 2026-10-29，极兔）

<a id="mysql-index-benefits-costs"></a>

## mysql-index-benefits-costs · 索引的优点与代价

**次数**：2；**领域**：MySQL。

**A（AI参考答案）**：索引可减少满足过滤、连接或排序条件时的扫描范围，但收益取决于选择性、查询条件和执行计划。索引需要占用存储，并让插入、删除及修改相关字段承担维护成本；数量越多不一定越快。设计时围绕高频查询确定联合索引顺序，检查回表、排序及覆盖情况，再用真实数据验证。仅为低选择性字段单独建索引，或为每个字段建索引，都可能得不偿失。

**实际来源**：
- [广东某公司java实习生面经](https://www.nowcoder.com/feed/main/detail/6fe8d56b45144d4b81f0082cb0f35572)（采集日 2026-10-23，匿名广东公司）
- [26届 小厂java实习面经](https://www.nowcoder.com/discuss/862367705284816896)（采集日 2026-10-29，深圳市中科保泰科技有限公司）

<a id="mysql-index-types"></a>

## mysql-index-types · MySQL索引的分类与使用

**次数**：2；**领域**：MySQL。

**A（AI参考答案）**：索引可从不同维度分类：约束上有主键、唯一和普通索引，列数上有单列与联合索引；InnoDB常用B+树，主键索引组织完整行，二级索引叶子保存主键值，必要时回表。不能把这些分类并排当成互斥选项。选索引要结合过滤、关联、排序和覆盖需求，既看查询收益，也考虑写放大与空间成本；是否实际使用需看执行计划和数据分布。

版本口径：MySQL 8.x / InnoDB常用B+树场景，其他引擎能力需另行区分。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [几百人小厂Java实习面经 第50场面!](https://www.nowcoder.com/feed/main/detail/a2476f1aebb84c9191ab53717464f55c)（采集日 2026-10-29，武汉众智鸿图）

<a id="mysql-storage-engine-comparison"></a>

## mysql-storage-engine-comparison · MySQL常见存储引擎及区别

**次数**：2；**领域**：MySQL。

**A（AI参考答案）**：AI参考答案：常见引擎有InnoDB、MyISAM、MEMORY等。MySQL 8.0默认InnoDB，支持事务、崩溃恢复、外键和行级锁，适合常见业务表。MyISAM不支持事务，主要使用表级锁；MEMORY将数据保存在内存中，重启后数据会丢失，不能代替持久业务存储。选择应看事务、一致性、恢复能力和访问模式，不能单凭读写速度作结论。

**实际来源**：
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="redis-basic-data-types"></a>

## redis-basic-data-types · Redis常用基本数据类型

**次数**：2；**领域**：Redis。

**A（AI参考答案）**：AI参考答案：常用类型包括String、Hash、List、Set和ZSet。String适合简单缓存或计数，Hash适合对象字段，List适合两端操作的序列，Set适合去重及交并差，ZSet适合按分数排序和范围查询。类型是对外的数据语义，底层编码会随元素数量、大小及版本变化。选型应结合查询与更新方式、内存和过期粒度；Stream等也是Redis支持的类型，不能把传统五种说成全部类型。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="redis-lua-cluster-safety"></a>

## redis-lua-cluster-safety · Lua在Redis Cluster中的约束

**次数**：2；**领域**：Redis。

**A（AI参考答案）**：Lua可把多个Redis操作放在一次脚本执行中，减少往返并避免其他命令穿插，但原子执行不等于出错时自动回滚已做修改。脚本应显式传入所访问的键，避免长时间阻塞服务；在Cluster中，相关键需满足同槽要求，可按业务设计hash tag。脚本不能把数据库和消息队列也纳入原子范围，更不能只因单机测试通过就宣称已经适配集群。

**实际来源**：
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）

<a id="spring-boot-auto-configuration"></a>

## spring-boot-auto-configuration · Spring Boot自动配置原理

**次数**：2；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：SpringBootApplication组合了配置、组件扫描和启用自动配置等能力。自动配置导入机制发现候选配置，再根据类路径、属性和已有Bean等条件决定是否装配；例如ConditionalOnMissingBean允许用户配置覆盖默认实现。它不是无条件扫描所有依赖里的类。Boot2.x不同小版本的候选注册方式有演进，2.7支持AutoConfiguration.imports，不能把Boot3机制直接套到所有Boot2项目。

版本口径：采云台Boot2.7.3；研约通Boot2.3.12。区别2.7新候选文件与早期spring.factories机制。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [26届 小厂java实习面经](https://www.nowcoder.com/discuss/862367705284816896)（采集日 2026-10-29，深圳市中科保泰科技有限公司）

<a id="springmvc-dispatcherservlet"></a>

## springmvc-dispatcherservlet · DispatcherServlet的作用

**次数**：2；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：DispatcherServlet是Spring MVC的前端控制器，负责把Servlet容器交给它的请求接入MVC处理链。它通过HandlerMapping找到处理器，再由HandlerAdapter调用Controller；返回结果按配置交给视图解析器或消息转换器，例如将对象转换为JSON。异常也可进入相应解析器。Filter通常在Servlet层包围请求，MVC拦截器则处于MVC处理流程内；不能把DispatcherServlet本身等同于监听端口的HTTP服务器。

**实际来源**：
- [华盛通JAVA实习生二面](https://www.nowcoder.com/feed/main/detail/fd30324de36044c69ab16437026163d4)（采集日 2026-10-25，华盛通）
- [佛山宏旺 java实习生](https://www.nowcoder.com/feed/main/detail/5083b0fbb75e480db6e8db2bbafc1195)（采集日 2026-10-27，佛山宏旺（原文标题））

<a id="strategy-pattern-benefits"></a>

## strategy-pattern-benefits · 策略模式的好处与边界

**次数**：2；**领域**：项目设计与技术选型。

**A（AI参考答案）**：策略模式把一组可替换算法或规则封装为实现同一接口的对象，由调用方根据上下文选择策略，适合计费、校验等存在稳定调用契约而规则多变的场景。它能减少把所有分支堆在一个大方法中的耦合，方便单独测试，但会增加类和选择逻辑，并不消除分支本身。规则很少且变化不大时不必强行抽象；项目是否已使用需看实际代码，不能仅凭有接口就认定采用了策略模式。

**实际来源**：
- [广东某公司java实习生面经](https://www.nowcoder.com/feed/main/detail/6fe8d56b45144d4b81f0082cb0f35572)（采集日 2026-10-23，匿名广东公司）
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）

<a id="synchronized-lock-optimization-states"></a>

## synchronized-lock-optimization-states · synchronized与锁优化

**次数**：2；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：synchronized通过对象监视器提供互斥及可见性，可修饰实例方法、静态方法或代码块，锁对象分别取决于实例、类或指定对象。传统HotSpot锁优化会涉及偏向锁、轻量级锁和重量级监视器，并可能使用自旋、锁消除与锁粗化降低开销。需要说明版本边界：偏向锁从JDK 15起默认禁用并废弃，较新JDK的轻量级锁实现也有变化，不能将旧版对象头状态与固定升级路径直接套用于所有版本。

**实际来源**：
- [美团后台开发Java 实习面经](https://www.nowcoder.com/discuss/353156179603955712)（采集日 2026-10-30，美团）
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="synchronized-versus-reentrantlock"></a>

## synchronized-versus-reentrantlock · synchronized与ReentrantLock的区别

**次数**：2；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：两者都支持互斥和可重入。synchronized由JVM管理监视器，退出同步块或异常离开时自动释放，使用简单；ReentrantLock需要在成功加锁后用finally解锁，但支持可中断获取、限时尝试及可选公平策略，还能创建多个Condition。公平锁并不保证线程调度的绝对先后，性能也要结合竞争情况测试。普通临界区可优先用简单方式，确有取消、超时或多条件等待需求时再选择显式锁。

**实际来源**：
- [熙牛医疗 杭州java实习生 一面面经 2026.9.3](https://www.nowcoder.com/feed/main/detail/6512d3ef462a49cbb0aa5167d57d372f)（采集日 2026-10-25，熙牛医疗）
- [北森客开实习生(实习转正) 2026.10.13](https://www.nowcoder.com/feed/main/detail/cecac304535c4b3c99e6ff117908251e)（采集日 2026-10-28，北森）

<a id="thread-pool-benefits"></a>

## thread-pool-benefits · 为什么使用线程池

**次数**：2；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：线程池通过复用工作线程减少频繁创建和销毁的成本，并集中管理并发数、任务队列和生命周期。相比每个任务新建线程，它更便于限制资源、监控和实施拒绝策略，但不会让任务自动变快。需要结合CPU或IO特征、下游容量和超时要求选择线程数与有界队列，避免无界排队拖垮内存；任务异常、取消及应用关闭也要有处理策略。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））
- [用友 Java实习面经](https://www.nowcoder.com/discuss/784203612955090944)（采集日 2026-11-01，用友）

<a id="ai-coding-requirement-iteration"></a>

## ai-coding-requirement-iteration · AI 生成代码持续不符合要求怎么办

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：先把需求拆成小而可验证的任务，说明输入输出、约束、现有接口及不能改动的范围，并给出一个最小失败样例或失败测试。让 AI 先解释理解和改动位置，再逐步实现，每轮检查差异并运行对应验证；发现偏离就回到明确的验收条件，而不是不断追加模糊指令。多轮仍失败时，应缩小问题、自己定位关键逻辑或改为手工实现，避免累积无法解释的补丁。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）

<a id="ai-generated-code-acceptance"></a>

## ai-generated-code-acceptance · AI 代码能运行就能直接用于业务吗

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：能运行只能说明某条路径没有立即报错，不能证明需求、边界和并发语义正确。我会先对照接口契约检查权限、事务、错误处理与依赖使用，再补正常、异常和边界测试；涉及金额、库存或幂等时，还要验证并发与重试。随后做代码审查和必要的集成验证，再按项目发布流程上线。AI 生成的实现仍由提交者负责，不能把演示成功或模型自述当作测试证据。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）

<a id="algorithm-binary-tree-diameter"></a>

## algorithm-binary-tree-diameter · 二叉树直径如何计算

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：AI参考答案：先确认直径按边数还是节点数计。常见按边数定义时，后序DFS返回每个节点向下的最大边长，通过左右子树高度之和更新全局最大值；用空节点高度0、非空高度1加子树最大高度的写法时，左右高度之和也恰为经过当前节点的路径边数。最长路径未必经过根节点。每个节点处理一次，时间O(n)、辅助栈O(h)；退化树可能栈溢出，可改显式栈后序遍历，并约定空树结果。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="algorithm-bubble-sort"></a>

## algorithm-bubble-sort · 冒泡排序的实现与复杂度

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：常见实现用两层循环：外层控制轮数，最多n-1轮；内层比较尚未排好部分的相邻元素，逆序就交换，每轮把最大元素移到该部分末尾，所以下一轮比较范围缩小。可设置交换标志，某轮没有交换就提前结束。平均和最坏时间复杂度O(n²)，有提前终止时已排序输入最好为O(n)，额外空间O(1)。仅在前者严格大于后者时交换可保持稳定性，适合小规模数据或教学，较大数据通常采用更高效的排序。

**实际来源**：
- [北森客开实习生(实习转正) 2026.10.13](https://www.nowcoder.com/feed/main/detail/cecac304535c4b3c99e6ff117908251e)（采集日 2026-10-28，北森）

<a id="algorithm-expression-stack-evaluation"></a>

## algorithm-expression-stack-evaluation · 利用栈求表达式的值

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：原文没有给出表达式语法、运算符集合和输入示例，无法确定唯一实现。若是常见中缀算术表达式，可用操作数栈与运算符栈，按优先级和结合性归约，括号控制归约边界；也可先转逆波兰表达式再求值。必须先确认是否支持一元负号、小数、空白和幂运算，并约定非法输入、除零及溢出行为。对有限运算符集合的常见实现，时间与辅助空间通常为O(n)。

**实际来源**：
- [美团后台开发Java 实习面经](https://www.nowcoder.com/discuss/353156179603955712)（采集日 2026-10-30，美团）

<a id="algorithm-fibonacci-methods"></a>

## algorithm-fibonacci-methods · 斐波那契数有哪些计算方法

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：先约定数列起点，例如F(0)=0、F(1)=1。直接递归按F(n)=F(n-1)+F(n-2)计算，但重复子问题很多，时间呈指数增长；记忆化递归或动态规划可降到O(n)。只求某一项时用两个变量滚动迭代，时间O(n)、额外空间O(1)；更大n可用矩阵快速幂或快速倍增，按算术操作数计为O(log n)。通项公式涉及浮点误差，不宜直接用于大整数精确计算；数值超范围需使用大整数或按题意取模。

**实际来源**：
- [北森客开实习生(实习转正) 2026.10.13](https://www.nowcoder.com/feed/main/detail/cecac304535c4b3c99e6ff117908251e)（采集日 2026-10-28，北森）

<a id="algorithm-heap-sort"></a>

## algorithm-heap-sort · 堆排序的步骤与复杂度

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：AI参考答案：升序排序可先把数组建成大顶堆，从最后一个非叶节点向前下沉，整体建堆为O(n)。随后反复交换堆顶与未排序区末尾元素，缩小堆范围，再对堆顶下沉恢复堆性质，每轮把当前最大值放到最终位置。总时间为O(n log n)，迭代下沉时额外空间O(1)，通常不稳定。要区分堆的有序约束与整个数组已排序，注意子节点下标和堆边界，不能把建堆误算成必须O(n log n)。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="algorithm-large-file-common-numbers"></a>

## algorithm-large-file-common-numbers · 大文件共有数字如何求解

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：AI参考答案：数字同样可采用一致哈希分桶后逐桶求交，或外部排序后双指针归并。若已知数字落在较小、有限且稠密的整数范围，可用位图记录出现情况，再扫描另一个文件求交；范围过大或数字并非整数时不能直接采用该方案。原文未给数值范围、重复次数和输出要求，需先澄清是否去重及是否保留频次。精确结果不能只依赖有误判概率的布隆过滤器，应保留最终验证。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="algorithm-large-file-common-strings"></a>

## algorithm-large-file-common-strings · 内存受限时求两个大文件的共有字符串

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：AI参考答案：先明确字符串分隔、编码、大小写及结果是否去重。可对两个文件使用相同哈希函数按字符串分桶写入外存，让相同字符串进入对应桶，再逐对桶读取，用哈希集合求交并输出。桶仍过大时继续分区，数据倾斜或超长字符串需单独处理；哈希相同后还要比较原字符串，不能把哈希碰撞当作相等。也可分别外部排序后归并求交，方案取决于可用内存、磁盘空间与IO成本。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="algorithm-longest-increasing-subsequence"></a>

## algorithm-longest-increasing-subsequence · 最长升序子序列

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：AI参考答案：先确认要求严格递增还是允许相等，以及返回长度还是序列；子序列不要求连续。基础动态规划令dp[i]表示以当前位置结尾的最长长度，遍历此前更小元素转移，时间O(n²)、空间O(n)。只求长度可维护各长度对应的最小尾值，用二分定位替换，降至O(n log n)；严格递增使用首个大于等于当前值的位置。需要恢复序列时另存前驱，不能直接把尾值数组当作最终子序列。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="algorithm-queue-implements-stack"></a>

## algorithm-queue-implements-stack · 用队列实现栈

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：AI参考答案：可用一个队列实现后进先出：入栈时先把新元素入队，再把此前的元素依次从队首取出放到队尾，使新元素位于队首；出栈直接删除队首，查看栈顶直接读队首。此方案入栈O(n)，出栈与取顶O(1)，空间O(n)。也可用两个队列在出栈时搬运，交换时间成本。原题未指定接口和容量，应确认空栈行为及是否要求某个操作为常数时间。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="algorithm-single-number-frequency"></a>

## algorithm-single-number-frequency · 成对数字中的唯一数及三次变体

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：AI参考答案：若严格满足只有一个数出现一次、其他数均出现两次，对所有元素异或即可，时间O(n)、额外空间O(1)。原文“三次”没有明确指谁出现三次，必须先确认：若其他数均出现三次、目标出现一次，可逐位计数模3恢复目标；若只是目标出现三次而其他数仍成对，异或仍得到目标。还应明确整数位宽和有符号数处理，不把含糊追问自动改写成某个完整的力扣输入条件。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="algorithm-stack-implementation"></a>

## algorithm-stack-implementation · 手写栈的实现

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：可用数组或链表实现后进先出的栈，定义push、pop、peek与判空操作，并明确空栈访问时的异常或返回约定。数组方案以size标记下一写入位置，容量不足时扩容，弹出引用后清空槽位避免对象滞留；链表方案在表头插入和删除。单次基本操作通常为O(1)，动态数组扩容后的入栈为均摊O(1)。原文未指定容量、泛型和线程安全要求，应先确认约束，不把自选接口当作原题条件。

**实际来源**：
- [美团后台开发Java 实习面经](https://www.nowcoder.com/discuss/353156179603955712)（采集日 2026-10-30，美团）

<a id="algorithm-tree-two-node-shortest-path"></a>

## algorithm-tree-two-node-shortest-path · 树中两节点的最短路径

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：原题未说明树是否有根、节点如何标识、边是否带权以及要求返回距离还是路径，需要先补充这些条件。若为普通无权树，两节点间只有一条简单路径，可从起点做DFS或BFS并记录父节点，再回溯得到路径；若为有根树且已具备父指针，可经最近公共祖先拼接两段路径。单次遍历时间和空间均可为O(n)，多次查询可预处理LCA；不能凭原文假定为二叉搜索树或自行补造输入。

**实际来源**：
- [美团后台开发Java 实习面经](https://www.nowcoder.com/discuss/353156179603955712)（采集日 2026-10-30，美团）

<a id="api-error-response"></a>

## api-error-response · 后端错误如何返回并在前端展示

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：后端应统一约定错误码、可读消息和请求追踪号，并用合适的 HTTP 状态表达参数错误、权限问题或服务异常。Spring 项目可以通过全局异常处理统一转换业务异常和校验异常；完整堆栈记录在服务端，前端根据稳定错误码展示提示或引导重试，不直接显示数据库语句、内部路径等细节。对可能已成功的写请求，要提供结果查询或幂等重试，避免前端收到报错后重复执行。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）

<a id="aqs-synchronizer-framework"></a>

## aqs-synchronizer-framework · AQS是什么

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：AI参考答案：AQS是构建锁和同步器的基础框架，通过整数同步状态和等待队列组织竞争线程。子类定义如何尝试获取、释放资源，框架负责获取失败后的排队、阻塞和唤醒，支持独占和共享模式。ReentrantLock、Semaphore等可基于它实现不同语义；状态含义由同步器决定，不能都理解成重入次数。FIFO等待队列也不代表所有实现天然公平，是否允许插队由获取策略决定。

**实际来源**：
- [用友 Java实习面经](https://www.nowcoder.com/discuss/784203612955090944)（采集日 2026-11-01，用友）

<a id="architecture-monolith-microservice-difference"></a>

## architecture-monolith-microservice-difference · 单体与微服务开发的区别

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：单体通常统一构建、部署，进程内调用方便，同一数据库事务相对容易组织；微服务按服务独立发布和扩缩容，但必须明确接口契约、数据归属与兼容策略。网络调用可能超时或部分失败，需要幂等、限流、监控和链路追踪，跨服务不能简单沿用本地事务。面试应结合真实经历说清收益与成本，没遇到过的问题不能包装成亲身解决过的事故。

**实际来源**：
- [28届Java后端实习面试](https://www.nowcoder.com/discuss/941324379416166400)（采集日 2026-10-21，百川云璟）

<a id="architecture-service-split"></a>

## architecture-service-split · 单体是否需要拆分及如何划分服务

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：先说明拆分要解决的实际矛盾，例如不同模块独立扩缩容、发布节奏或团队边界，再按业务职责与数据所有权划分，尽量保持高内聚、低耦合。拆分会把本地调用和事务变成远程调用与跨服务一致性问题，还需处理超时、重试、幂等和可观测性。实习项目若没有这些痛点，单体往往更易维护；不能为使用中间件而虚构业务规模或拆分经历。

**🔍 面试追问（AI生成）**：
- 单体就没有模块边界吗？ **简答**：有。可以先按领域模块化，限制跨模块依赖，出现真实独立部署需求后再拆服务。

**实际来源**：
- [28届Java后端实习面试](https://www.nowcoder.com/discuss/941324379416166400)（采集日 2026-10-21，百川云璟）

<a id="arraylist-versus-hashset"></a>

## arraylist-versus-hashset · ArrayList 与 HashSet 的区别

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：ArrayList 基于动态数组，允许重复、保留列表顺序，适合按下标访问和顺序处理；HashSet 通过哈希结构去重，不提供下标，也不保证遍历顺序。ArrayList 的按下标访问通常为 O(1)，contains 一般需要 O(n) 扫描；HashSet 在哈希分布良好时 contains、add 平均接近 O(1)，但取决于哈希与判等实现。需要去重选 Set，需要位置和重复元素选 List，不能只根据“哪种更快”决定。

**实际来源**：
- [南京车300 Java 实习面经](https://www.nowcoder.com/feed/main/detail/8b78085106ae45a4bada11cb75141d8f)（采集日 2026-10-24，南京车300）

<a id="backend-exception-handling-design"></a>

## backend-exception-handling-design · 异常处理如何提供有用信息并保证业务一致性

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：AI参考答案：异常应表达失败原因、业务错误码和必要上下文，包装时保留原始cause，让调用方能够判断是否可恢复或重试。业务异常与系统故障分开处理，在请求边界统一转换响应，内部堆栈只留在服务端，不泄露敏感数据。不要捕获后直接忽略或返回成功；涉及数据库事务时确认异常传播与回滚规则，外部调用失败还需考虑幂等、补偿和超时。没有真实项目细节时按通用设计思路说明。

**实际来源**：
- [Java 后端新手的第一次面试复盘](https://www.cnblogs.com/thr-0103/p/18113538)（采集日 2026-11-02，匿名公司）

<a id="backend-logging-practices"></a>

## backend-logging-practices · 后端日志应该记录什么与遵循哪些规范

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：AI参考答案：日志用于定位故障、追踪请求和观察关键业务状态。可统一记录追踪号、操作名称、耗时、结果码及必要的业务标识，按DEBUG、INFO、WARN、ERROR区分级别，使用参数化日志。异常应保留堆栈与上下文，避免多层重复打印。密码、令牌和敏感个人信息不能原样写入日志；大报文应截断或采样，并配置滚动、保留周期和访问权限。回答实践经历时只说自己实际做过的部分。

**实际来源**：
- [Java 后端新手的第一次面试复盘](https://www.cnblogs.com/thr-0103/p/18113538)（采集日 2026-11-02，匿名公司）

<a id="bloom-filter-false-positive-tuning"></a>

## bloom-filter-false-positive-tuning · 如何降低布隆过滤器假阳性概率

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：AI参考答案：布隆过滤器用位数组与多个哈希位置判断成员，误判率取决于位数、哈希次数和实际插入量。应按预期元素数量与目标误判率设计，增加每个元素可用的位数，并选择合适的哈希次数；哈希越多并非总越准确，也会增加计算成本。容量明显超出设计值时应扩容或重建，并保证数据同步。普通布隆过滤器不能直接清位删除，阳性结果仍需查询真实存储确认。

**实际来源**：
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="cache-logical-expiration-costs"></a>

## cache-logical-expiration-costs · 逻辑过期的 key 不设置 TTL 有什么问题

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：逻辑过期把业务失效时间放进缓存值，查询发现过期时可以先返回旧数据，再由受控异步任务刷新，以降低热点失效时的阻塞。但不设置 Redis TTL 会让冷数据长期占内存，数据被删除后也可能留下旧值，必须设计清理任务、容量限制或更长的物理过期时间。它适合允许短暂陈旧的热点数据，不适合必须立即读到最新值的业务；刷新失败、并发刷新和线程池拥塞也需要明确降级策略。

**实际来源**：
- [南京车300 Java 实习面经](https://www.nowcoder.com/feed/main/detail/8b78085106ae45a4bada11cb75141d8f)（采集日 2026-10-24，南京车300）

<a id="cas-versus-synchronized"></a>

## cas-versus-synchronized · CAS与synchronized的区别

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：原题syscornized按synchronized理解。CAS比较期望值后原子更新，常用于原子变量，适合较小的共享状态操作；竞争激烈时重试会消耗CPU，还需考虑ABA和多变量一致性。synchronized对监视器保护的临界区提供互斥及可见性，可表达一组操作的原子边界。两者解决问题的粒度不同，不能一概说CAS性能一定更好，也不能把volatile的可见性误当成复合操作原子性。

**实际来源**：
- [广东某公司java实习生面经](https://www.nowcoder.com/feed/main/detail/6fe8d56b45144d4b81f0082cb0f35572)（采集日 2026-10-23，匿名广东公司）

<a id="database-sharding-design"></a>

## database-sharding-design · 数据库分表如何设计

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：AI参考答案：先确认单表瓶颈是否可通过索引、归档或SQL优化解决，再按业务访问路径选择分片键。水平分表分散数据行，可按哈希均匀分布，也可按时间等范围便于归档；垂直拆分则按字段或业务职责拆开。设计时考虑热点、分片路由、全局ID、跨表分页与聚合，以及跨分片事务和扩容迁移。原文没有表结构、数据量和查询条件，只能给通用取舍，不能假定某个固定分片数。

**实际来源**：
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）

<a id="database-types-relational-nosql"></a>

## database-types-relational-nosql · 常见数据库类型及适用场景

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：常见分类包括关系型数据库和多种非关系型数据库。MySQL等关系型数据库以表、约束和事务组织数据，适合订单、账户等关联查询与一致性要求明确的业务；Redis偏向键值访问和丰富数据结构，文档库便于保存结构变化较多的文档，图数据库擅长关系遍历。应按访问模式、事务需求和维护成本选型，不能把非关系型简单理解为没有事务，也不能把数据库类别混同于MySQL存储引擎。

**实际来源**：
- [健康160-JAVA开发实习生](https://www.nowcoder.com/discuss/943496145010020352)（采集日 2026-10-25，健康160）

<a id="distributed-lock-project-usage"></a>

## distributed-lock-project-usage · 项目中分布式锁的实际用法

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：先说明锁保护的资源、粒度、获取方式、超时与释放，再解释为什么还需要数据库兜底。分布式锁可能因租期到期、进程暂停或网络问题失去互斥，不能把它当作业务幂等和数据库约束的替代。若锁有所有者标识，应比较后再释放，避免删除别人的锁；若给出显式租期，就必须说明超过租期的边界，不能把计划实现的锁写成已经使用。

**🔍 面试追问（AI生成）**：
- 显式10秒租期下业务超过10秒怎么办？ **简答**：可能失去互斥，应按实际耗时选择租期/续期方案并保留数据库幂等；优化建议不能写成现有实现。

**实际来源**：
- [唯智信息技术 Java开发实习生 一面面经 2026.9.16](https://www.nowcoder.com/feed/main/detail/e00abf3b34e94e4398194442a9a826fb)（采集日 2026-10-21，唯智信息技术）

<a id="docker-common-commands"></a>

## docker-common-commands · Docker常用命令

**次数**：1；**领域**：计算机网络与操作系统。

**A（AI参考答案）**：可按生命周期介绍：docker pull拉取镜像，build构建镜像，run创建并启动容器，ps查看容器，logs查看日志，exec进入运行容器执行命令，inspect查看配置，stop停止容器，rm删除容器，images与rmi管理镜像。说明镜像、容器和持久化卷的区别，删除容器不应被当成业务数据备份策略。面试只需说明用途，不能把清理命令直接拿到真实服务器执行。

**实际来源**：
- [昆山java后端小厂面经](https://www.nowcoder.com/feed/main/detail/bcf78a7db16f4d22a7ce33aca1358876)（采集日 2026-10-22，匿名昆山小厂（标题自述））

<a id="elasticsearch-basic-overview"></a>

## elasticsearch-basic-overview · Elasticsearch的基本用途与结构

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：AI参考答案：Elasticsearch是基于Lucene的分布式检索与分析系统，适合全文搜索、日志检索和聚合分析。文档进入索引后按映射和分析器处理，全文字段通过倒排索引支持检索；分片承担数据划分，副本用于冗余及部分读扩展。它通常是近实时搜索，写入成功不代表马上可检索。选型还要考虑映射、分片和资源成本，不能把它当作关系数据库事务与约束的直接替代品。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="es-bm25-knn-retrieval"></a>

## es-bm25-knn-retrieval · BM25与KNN检索原理

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：BM25属于关键词相关性评分，综合词频饱和、逆文档频率和文档长度归一化，适合精确术语和文本匹配。KNN根据向量距离或相似度寻找语义相近的内容，ES可用近似向量检索降低搜索成本，但召回率与延迟受索引和候选参数影响。两者可做混合检索，但分数不能不经处理就直接相加；要根据真实查询集评估效果，不虚构项目已使用ES。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））

<a id="g1-region-generations"></a>

## g1-region-generations · G1如何划分堆内存

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：G1把堆划分为多个大小相同的Region，按需要把部分Region作为Eden、Survivor或老年代使用，因此仍然是分代收集，只是不再要求各代占据固定连续的大块区域。大对象还可能占用连续的专用Region。回收时通过复制整理，把存活对象迁移到其他Region，并按垃圾收益和暂停目标选择回收集合。暂停目标是优化目标而非绝对时限，不能认为启用G1就不再出现停顿或Full GC。

**实际来源**：
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）

<a id="gc-basic-algorithms"></a>

## gc-basic-algorithms · 常见垃圾回收算法

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：常见算法有标记清除、复制和标记整理。标记清除思路直接但可能留下碎片；复制把存活对象转移到另一块区域，分配简单但需要预留空间；整理在标记后移动对象，减少碎片但增加移动成本。分代思想根据对象存活特征选择策略，不是独立的第四种基本回收算法。算法与具体收集器不同，暂停时间也受对象存活量、堆规模和实现影响。

版本口径：基础算法口径，不编造项目GC调优结果。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="gc-roots-reference-counting"></a>

## gc-roots-reference-counting · GC Roots与引用计数的局限

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：AI参考答案：可达性分析从GC Roots沿引用关系遍历，不能经有效强引用链到达的对象才可能进入回收处理。常见根包括活动线程栈中使用的对象引用、已加载类的静态引用及JNI引用等，具体根集合由实现确定。引用计数在引用增减时维护计数，普通引用计数难以识别相互引用但整体不可达的环。不可达也不表示立刻释放，回收时机和引用处理仍由收集器决定。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="git-revert-versus-reset"></a>

## git-revert-versus-reset · Git 版本回退如何选择 revert 与 reset

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：已经推送并由多人共享的提交，通常用 git revert 生成一个抵消目标改动的新提交，保留历史，便于协作审查。git reset 会移动当前分支指针：soft 保留暂存和工作区，mixed 重置暂存区但保留工作区，hard 还会覆盖受影响的已跟踪文件。reset 更适合整理尚未共享的本地提交，不能把两者理解成习惯不同的等价操作；操作前应确认未提交改动和团队分支状态。

**🔍 面试追问（AI生成）**：
- revert 一定不需要处理冲突吗？ **简答**：不一定；目标提交之后的修改可能与反向补丁冲突，需要正常解决，合并提交还要明确主线父提交。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）

<a id="hashmap-initial-capacity-rounding"></a>

## hashmap-initial-capacity-rounding · HashMap指定初始容量13时的数组长度

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：AI参考答案：以OpenJDK 8的new HashMap<>(13)为例，构造时通常尚未分配桶数组，而是保存向上取整到2的幂后的初始阈值16。首次插入分配长度16的数组，默认负载因子0.75使后续扩容阈值成为12；加入第13个不同键时通常扩为32。因此必须区分构造后、首次插入后与放入13个元素后的时刻，参数13不是保证无需扩容保存13条映射的容量承诺。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="hashmap-load-factor-tradeoff"></a>

## hashmap-load-factor-tradeoff · HashMap负载因子的取舍

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：AI参考答案：负载因子影响扩容阈值，常见默认值为0.75。因子较小会更早扩容、通常减少桶内竞争与冲突链长度，但占用更多数组空间；因子较大可节省部分桶空间，却可能增加冲突与查找成本。实际影响还取决于哈希分布、元素量和访问模式，不能简单认为越小越快。迭代成本还与容量有关，预估元素数与设置初始容量时应同时考虑负载因子，避免不必要扩容和过度预分配。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="hashmap-null-key-value"></a>

## hashmap-null-key-value · HashMap是否允许null键与null值

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：AI参考答案：HashMap允许一个null键及多个null值；再次写入null键会更新同一映射。get返回null既可能表示没有该键，也可能表示该键对应的值为null，需要containsKey区分。允许空值与线程安全是不同问题；ConcurrentHashMap不允许null键和值，不能把HashMap的规则推广到所有Map。设计接口时应说明缺失值与空值各自的业务含义。

**实际来源**：
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））

<a id="hashset-jdk-implementation"></a>

## hashset-jdk-implementation · HashSet 在 JDK 7 与 JDK 8 中的实现

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：HashSet 底层使用 HashMap，把元素作为键，并为所有键关联同一个占位对象，所以去重依赖 hashCode 与 equals。JDK 7 的 HashMap 桶主要是链表，JDK 8 增加红黑树，在冲突较多且数组容量达到条件时树化；容量较小时会先扩容。这个变化改善了部分冲突场景，但不让集合天然线程安全，也不保证有序；元素加入后修改影响判等的字段，可能破坏正常查询与去重。

**实际来源**：
- [南京车300 Java 实习面经](https://www.nowcoder.com/feed/main/detail/8b78085106ae45a4bada11cb75141d8f)（采集日 2026-10-24，南京车300）

<a id="http11-versus-http2"></a>

## http11-versus-http2 · HTTP/1.1与HTTP/2的区别

**次数**：1；**领域**：计算机网络与操作系统。

**A（AI参考答案）**：HTTP/2使用二进制分帧，在同一连接中通过多个流承载请求响应，并用头部压缩减少重复开销；HTTP/1.1通常以文本形式表达头部，实践中常用多个连接并行请求。HTTP/2改善了应用层请求排队，但底层仍基于TCP，丢包可能阻塞连接上多个流，不等于完全消除队头阻塞。浏览器中通常经TLS协商使用HTTP/2，不能简单把版本升级等同于业务接口必然更快。

**实际来源**：
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））

<a id="inventory-overselling-prevention"></a>

## inventory-overselling-prevention · 如何解决超卖

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：通用AI参考思路：先明确库存权威数据源与下单事务边界，数据库扣减可采用带库存充足条件的原子UPDATE，并检查影响行数，避免先查询再无条件扣减。并发较高时可用缓存原子预扣削峰，但仍需处理消息可靠投递、消费幂等、失败补偿和库存对账。原题未给出项目架构和一致性要求，不能断言必须使用分布式锁或某种队列；具体方案应按流量、超时及容错要求选择。

**实际来源**：
- [神州信息 java实习生面经（已offer）](https://www.nowcoder.com/discuss/353159627783217152)（采集日 2026-10-30，神州信息）

<a id="java-checked-unchecked-exceptions"></a>

## java-checked-unchecked-exceptions · 受检异常与运行时异常的区别

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：AI参考答案：所谓“编译时异常”通常指受检异常，并不是异常真的在编译阶段抛出。除RuntimeException、Error及其子类外，受检异常需要在编译时满足捕获或声明要求，例如IOException；运行时异常如NullPointerException不强制捕获或声明，但同样在运行中发生。异常类型应表达调用方能否合理恢复，不能为逃避处理一律包装为运行时异常。包装需保留cause，资源释放优先使用try-with-resources。

**实际来源**：
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）

<a id="java-deadlock-prevention"></a>

## java-deadlock-prevention · 什么是死锁以及如何减少死锁

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：AI参考答案：死锁是多个线程互相等待对方持有的资源，导致都无法继续。典型条件包括互斥、持有并等待、不可抢占和循环等待。工程中可统一多把锁的获取顺序、缩小持锁范围，避免持锁进行远程调用；必要时用带超时的tryLock并在失败后释放已持有资源。通过线程转储检查等待关系和持有者，确认实际环路。超时重试也需退避和次数限制，防止死锁变成活锁或持续重试。

**实际来源**：
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）

<a id="java-dynamic-proxy-jdk-cglib"></a>

## java-dynamic-proxy-jdk-cglib · JDK动态代理与CGLIB的区别

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：JDK动态代理通常基于接口生成代理对象，通过InvocationHandler转发调用；CGLIB通过生成目标类的子类实现增强，因此不能靠子类重写增强final方法，也不能继承final类。Spring AOP可根据配置和目标类型选择实现，不能笼统说始终使用其中一种。无论哪种代理，普通同类内部直接调用都可能绕过代理增强；判断事务或切面是否生效，要看实际调用是否经过代理对象。

**实际来源**：
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）

<a id="java-equals-versus-reference"></a>

## java-equals-versus-reference · == 与 equals 的区别

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：== 对基本类型比较数值，对引用类型比较是否指向同一对象；equals 是对象的方法，默认实现也比较引用，但 String 等类重写后按内容判断。业务对象需要按关键字段判等时，应同时重写 equals 和 hashCode，保证相等对象具有相同哈希值，否则放入 HashMap、HashSet 可能出现查找或去重异常。比较字符串内容通常用 equals，并注意接收者为 null 时的空指针问题。

**🔍 面试追问（AI生成）**：
- 两个对象 hashCode 相同就一定相等吗？ **简答**：不一定，哈希冲突允许存在，还要通过 equals 判断；equals 相等则必须具有相同 hashCode。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）

<a id="java-exception-hierarchy"></a>

## java-exception-hierarchy · Java异常体系如何分类

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：AI参考答案：Throwable主要分为Error与Exception。Error通常代表虚拟机或运行环境的严重问题；Exception中，RuntimeException及其子类是非受检异常，其余常见受检异常要求捕获或声明。空指针、越界属于运行时异常，IOException是受检异常。按调用方能否恢复选择处理边界，保留异常原因，资源释放优先用try-with-resources，不应捕获后静默吞掉。

**实际来源**：
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））

<a id="java-final-semantics"></a>

## java-final-semantics · final修饰变量、方法与类的含义

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：final修饰变量表示只能赋值一次；引用变量不能再指向其他对象，但对象内部状态仍可能变化，所以不等于不可变或线程安全。修饰方法表示不能被子类重写，修饰类表示不能被继承。成员final字段需在声明、初始化块或构造过程中完成赋值；局部变量需在使用前赋值。并发中final字段有专门的初始化可见性语义，但前提包括构造期间不让this逸出，仍不能代替对可变共享状态的同步。

**实际来源**：
- [神州信息 java实习生面经（已offer）](https://www.nowcoder.com/discuss/353159627783217152)（采集日 2026-10-30，神州信息）

<a id="java-finally-return-semantics"></a>

## java-finally-return-semantics · try中return后finally是否执行

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：通常会执行。try中的return先计算返回值，随后执行finally；若finally正常结束，才完成原来的返回。finally若也return或抛异常，会覆盖原本的返回或异常，因此应避免在finally里改变控制流。finally中修改局部基本类型变量通常不改变已计算的返回值，但修改返回对象的内容可能被调用方看到。进程被终止、JVM退出或代码一直未离开try等情况下，不能保证执行finally。

**实际来源**：
- [北森客开实习生(实习转正) 2026.10.13](https://www.nowcoder.com/feed/main/detail/cecac304535c4b3c99e6ff117908251e)（采集日 2026-10-28，北森）

<a id="java-generics-bounds"></a>

## java-generics-bounds · Java泛型的T、问号与extends

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：T通常是声明时命名的类型参数，问号表示未知类型，? extends X表示某个X或其子类型，适合从中按X读取，但通常不能安全加入具体的非null值。? super X可接收X及其子类对象，读取时一般只能保证Object。Java泛型不具有协变继承关系，List<Integer>不是List<Number>的子类型；多数泛型信息经擦除，运行时也不能直接new T或使用基本类型作为类型实参。

**实际来源**：
- [昆山java后端小厂面经](https://www.nowcoder.com/feed/main/detail/bcf78a7db16f4d22a7ce33aca1358876)（采集日 2026-10-22，匿名昆山小厂（标题自述））

<a id="java-group-average-price"></a>

## java-group-average-price · 按商品种类计算平均价格

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：遍历商品List，以种类为键维护累计金额和数量，最后对每组求平均值，时间复杂度为O(n)，额外空间与种类数有关。金额一般用BigDecimal按约定精度累加和除法，明确舍入方式，避免直接用浮点数造成价格误差；也可以用Stream分组配合自定义累计器。先约定空价格、空种类和空列表的处理规则，不要为每种商品反复扫描全表，也不应并行修改普通HashMap。

**🔍 面试追问（AI生成）**：
- 同组商品价格先除以总数再求和可以吗？ **简答**：不宜作为默认金额计算方式，逐项舍入可能累计误差。通常先汇总精确金额，再按组内数量统一除法和舍入。

**实际来源**：
- [重庆小小小厂面试](https://www.nowcoder.com/feed/main/detail/3375e792921b46a0ae44aefae6fbcba3)（采集日 2026-10-26，重庆某小厂（匿名））

<a id="java-interface-versus-abstract-class"></a>

## java-interface-versus-abstract-class · 接口与抽象类有什么区别

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：AI参考答案：接口主要定义能力契约，一个类可以实现多个接口；抽象类适合表达同一类型体系中的共享状态和部分实现，一个类只能直接继承一个类。抽象类可以有实例字段、构造器和不同可见性的方法；接口字段是常量，不能保存每个对象的实例状态。Java 8接口可有default和static方法，Java 9起还可有private方法。选择时优先根据类型关系与职责决定，不要仅为了代码复用建立不合理继承。

**实际来源**：
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）

<a id="java-jdk-selection"></a>

## java-jdk-selection · 项目为何选择某个JDK版本

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：JDK选型先看框架最低要求、依赖兼容性、部署平台和维护周期，再评估语言特性、GC及监控工具带来的收益。Java 17是LTS版本，但长期支持期限取决于具体发行商；升级还需验证编译目标、第三方库、反射访问和回归测试。原题作者使用17不代表用户项目使用17，不能为了回答选型题把两项目已声明的Java 8写成Java 17。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））

<a id="java-memory-model-happens-before"></a>

## java-memory-model-happens-before · Java内存模型与happens-before

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：Java内存模型JMM规定线程对共享变量读写时允许观察到的行为，重点是可见性、有序性和同步关系，与堆、栈等JVM运行时内存区域不是同一概念。可通过同一锁的释放与后续获取、volatile写与后续读等建立happens-before关系。volatile能提供相应可见性与顺序保证，但不能让i++这样的复合操作自动原子化；需要互斥锁或原子类，并结合业务整体不变量设计同步。

**实际来源**：
- [用友金融一面](https://www.nowcoder.com/feed/main/detail/b087698fedff49668324389ed50f3829)（采集日 2026-10-29，用友金融）

<a id="java-monitor-lock-target"></a>

## java-monitor-lock-target · 线程获取的对象监视器锁对应什么

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：AI参考答案：以synchronized为例，线程竞争的是某个对象关联的监视器，保护范围由共同遵守的锁协议决定，并非自动锁住对象的全部字段。实例同步方法锁当前this，静态同步方法锁对应Class对象，代码块锁括号中的对象。两个线程必须使用同一把锁才能互斥；同一对象的普通方法仍可被其他线程调用。应选稳定、私有且职责明确的锁，避免锁引用变化。

**实际来源**：
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="java-multithreading-workload-selection"></a>

## java-multithreading-workload-selection · 多线程是否更快及CPU与IO任务如何选线程数

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：多线程不保证更快：并发是任务交错推进，并行才是在多个执行资源上同时计算。CPU密集任务通常把工作线程控制在可用CPU核数附近，再通过压测调整；线程过多会增加调度、锁竞争和缓存开销。IO密集任务有较多等待时间，可用更多线程覆盖等待，但仍受数据库连接数、远端限流和内存约束。Java 21虚拟线程适合大量阻塞式IO任务，也不会增加CPU算力或下游容量；最终应以吞吐、延迟和资源占用验证。

版本口径：Java 21虚拟线程与平台线程区分。

**实际来源**：
- [佛山宏旺 java实习生](https://www.nowcoder.com/feed/main/detail/5083b0fbb75e480db6e8db2bbafc1195)（采集日 2026-10-27，佛山宏旺（原文标题））

<a id="java-notify-versus-notifyall"></a>

## java-notify-versus-notifyall · notify与notifyAll有什么区别

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：AI参考答案：两者都要求当前线程持有目标对象的监视器。notify任意唤醒一个在该对象上等待的线程，notifyAll唤醒全部等待线程，但它们仍需重新竞争锁；通知不会立即释放当前线程持有的锁。等待线程应在while循环中重新检查条件，防止虚假唤醒或条件已被其他线程改变。存在多种等待条件时，仅通知一个线程可能选错等待者，应结合正确性与唤醒成本选择。

**实际来源**：
- [浪潮暑期实习java开发面经](https://www.nowcoder.com/discuss/353156399897190400)（采集日 2026-11-03，浪潮）

<a id="java-polymorphism-method-dispatch"></a>

## java-polymorphism-method-dispatch · Java多态的实现

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：常见做法是通过父类或接口引用指向具体实现对象，调用被重写的实例方法时由实际对象类型决定执行实现，从而让调用方依赖稳定契约。方法重载主要在编译期根据声明类型和参数选择，不能与运行时重写混为一谈；字段、静态方法和私有方法也不能直接套用同样的动态分派结论。多态有助于扩展，但仍需控制接口职责，避免为变化很少的逻辑增加无谓层次。

**实际来源**：
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））

<a id="java-serialization-purpose"></a>

## java-serialization-purpose · 对象序列化的机制与用途

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：序列化是把对象所表示的数据按约定格式编码，供网络传输或持久化；反序列化再按格式恢复数据结构。Java原生对象流依赖Serializable等协议，可处理对象图；JSON和Protobuf则采用各自的数据模型与兼容规则，并不要求都实现Serializable。实际选型要看跨语言、体积、性能与版本演进。不能把所有序列化都等同于Java对象流，也应避免对不可信输入直接使用原生反序列化。

**实际来源**：
- [华盛通JAVA实习生二面](https://www.nowcoder.com/feed/main/detail/fd30324de36044c69ab16437026163d4)（采集日 2026-10-25，华盛通）

<a id="java-shared-variable-races"></a>

## java-shared-variable-races · 多个线程操作同一个变量可能发生什么

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：AI参考答案：多个线程操作同一变量不一定出错，要看是否存在并发写入及正确同步。像count++包含读、计算、写，交错执行可能丢失更新；即使单次读写原子，也可能有可见性和顺序问题。可用同一把锁保护完整操作，或用AtomicInteger等原子类更新单个状态；多个变量共同维护不变量时仍需整体同步。volatile主要提供可见性与有序性，不能让复合操作自动原子化。

**实际来源**：
- [Java 后端新手的第一次面试复盘](https://www.cnblogs.com/thr-0103/p/18113538)（采集日 2026-11-02，匿名公司）

<a id="java-static-semantics"></a>

## java-static-semantics · static关键字的含义

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：AI参考答案：static成员属于类，静态字段通常由该类的实例共享，静态方法无需先创建实例即可调用。静态方法没有this，不能直接访问实例成员；同名静态方法是隐藏，不是实例方法的动态重写。静态初始化块在类初始化阶段执行。static不等于常量、单例或线程安全，共享可变静态字段仍需同步；不同类加载器加载的同名类也可能拥有各自的静态状态。

**实际来源**：
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）

<a id="java-thread-definition-benefits"></a>

## java-thread-definition-benefits · 线程是什么及使用线程的好处

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：AI参考答案：线程是程序的一条执行路径，有自己的栈和执行现场，同一进程的线程通常共享堆等资源。多线程可让耗时任务与请求处理分离，重叠IO等待，并在多核条件下并行计算，提高响应性或吞吐量。但线程越多不一定越快，创建、切换和共享状态同步都有成本。实际应限制并发并保护共享数据，不能把多线程等同于自动提高性能。

**实际来源**：
- [用友 Java实习面经](https://www.nowcoder.com/discuss/784203612955090944)（采集日 2026-11-01，用友）

<a id="java-volatile-ordering"></a>

## java-volatile-ordering · volatile的可见性与重排序约束

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：AI参考答案：volatile写与后续对同一变量的读建立happens-before关系，使写之前的操作对正确观察该写的线程可见。编译器和处理器必须遵守Java内存模型要求，不能把普通操作跨越volatile读写重排到破坏该关系的位置；并不是整个程序都禁止重排。volatile适合状态发布等场景，不能让自增、先检查再更新等复合操作自动原子化，需要结合锁或原子类保护业务不变量。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="jvm-heap-generations"></a>

## jvm-heap-generations · 堆的分代与不同收集器布局

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：在常见Java8分代收集器中，堆可按年轻代和老年代讨论，年轻代通常包含Eden及两个Survivor区，对象经存活和年龄判断等规则进入老年代，但并非所有对象都必须依次走完固定路线。G1使用Region组织内存，年轻与老年代是逻辑集合，布局不能直接套成连续的三块。元空间存类元数据，不是堆内分代；回答时先说明JDK与收集器。

版本口径：Java 8常见分代收集器与G1的概念比较；不假定项目实际GC参数。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="jvm-memory-layout-design"></a>

## jvm-memory-layout-design · JVM内存区域为何区分线程私有与共享

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：AI参考答案：原题“内存模型”可能指运行时内存区域，也可能指JMM，应先澄清。若指区域划分，线程私有的程序计数器和栈保存执行位置、局部变量及调用现场，避免线程调用状态相互覆盖；共享堆便于对象共享，方法区承载类级信息。共享也带来同步和回收问题。若指JMM，则应讨论可见性、有序性和happens-before，不能拿堆栈分区代替并发语义。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="jwt-structure-and-validation"></a>

## jwt-structure-and-validation · JWT的用途、结构与校验

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：JWT可用于携带签名的身份声明。常见的签名JWT采用紧凑JWS表示，由Header、Payload和Signature三段组成；前两段只是编码，默认并不保密，所以不应放密码等敏感数据。服务端不能只解码就信任内容，还应校验签名、允许的算法、有效期及业务要求的签发者和受众。客户端按约定携带令牌，授权判断仍由服务端完成；若需要立即撤销，可结合服务端会话或名单机制。

**实际来源**：
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）

<a id="load-test-order-invariants"></a>

## load-test-order-invariants · 如何用 JMeter 验证一人一单和不超卖

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：先准备可回滚的测试数据，分别构造同一用户重复提交、多用户竞争有限库存、超时重试等场景，并通过并发线程与同步启动制造竞争。响应码和成功率只是过程指标，还应在测试后核对数据库：同一业务唯一键的有效订单不重复、库存不为负、成功订单数量与库存扣减一致，失败请求没有残留扣减。测试账号和请求号要参数化，避免把测试脚本重复数据造成的错误当成服务端问题；这些属于验证方案，不代表项目已做过压测。

**实际来源**：
- [南京车300 Java 实习面经](https://www.nowcoder.com/feed/main/detail/8b78085106ae45a4bada11cb75141d8f)（采集日 2026-10-24，南京车300）

<a id="mq-reliable-delivery"></a>

## mq-reliable-delivery · 消息队列如何降低消息丢失风险

**次数**：1；**领域**：RabbitMQ / 消息队列。

**A（AI参考答案）**：AI参考答案：按生产、存储、消费三个阶段分别保证可靠性。以RabbitMQ为例，生产者处理发布确认与不可路由返回，确认不明的消息需可重试；队列与消息按需求持久化，关键数据可采用合适的复制队列。消费者完成业务提交后再手动确认，失败重试并设置死信或人工补偿，避免无限重投。重试可能产生重复，消费必须幂等；数据库提交与发消息的一致性可用本地消息表等方案，不能承诺任意故障下绝不丢失。

**实际来源**：
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）

<a id="mybatis-hash-dollar-parameters"></a>

## mybatis-hash-dollar-parameters · MyBatis的井号与美元参数占位区别

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：MyBatis的#{value}通常生成PreparedStatement的问号占位并绑定参数，适合传递数据值；${value}是直接把字符串替换进SQL结构，不能依靠参数绑定防止注入。表名、列名和排序方向不能简单当作普通问号参数，确需动态选择时，应由服务端把有限选项映射到固定SQL片段或做严格白名单校验。不要将用户输入直接放入${}；模糊查询也可使用绑定参数构造匹配值。

**实际来源**：
- [26届 小厂java实习面经](https://www.nowcoder.com/discuss/862367705284816896)（采集日 2026-10-29，深圳市中科保泰科技有限公司）

<a id="mybatis-mapper-execution"></a>

## mybatis-mapper-execution · MyBatis如何从Mapper方法执行SQL

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：MyBatis加载配置、Mapper XML或注解，建立映射语句等元数据；获取Mapper接口时通常返回动态代理。调用方法后，代理按接口与方法定位MappedStatement，将参数及动态SQL处理成可执行SQL和参数映射，再由执行器经JDBC完成预编译、绑定、查询或更新，最后按结果映射转为对象。MyBatis主要封装SQL执行与映射，SQL仍需开发者负责；SqlSession本身不宜跨线程共享，Spring集成通常通过SqlSessionTemplate参与事务管理。

版本口径：MyBatis 3及常见Spring集成。

**实际来源**：
- [佛山宏旺 java实习生](https://www.nowcoder.com/feed/main/detail/5083b0fbb75e480db6e8db2bbafc1195)（采集日 2026-10-27，佛山宏旺（原文标题））

<a id="mybatis-multiple-parameters"></a>

## mybatis-multiple-parameters · MyBatis如何传递多个参数

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：Mapper可接收单个DTO或Map，也可在多个方法参数上用@Param声明稳定名称，再在XML中通过#{}绑定对应属性。多个复杂参数要明确引用路径，批量集合可配合foreach，不应依赖编译参数名或不同版本的默认命名碰巧生效。#{}处理值参数，表名、列名等结构性内容不能随意作为值绑定；必须动态选择时用白名单，避免用${}直接拼接用户输入。

**实际来源**：
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））

<a id="mysql-conditional-stock-update"></a>

## mysql-conditional-stock-update · 如何用条件UPDATE防止库存扣成负数

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：可用参数化SQL：UPDATE goods SET stock=stock-? WHERE id=? AND stock>=?，扣减数量必须为正数，两个数量参数一致。根据影响行数判断成功或库存不足，避免先普通查询再无条件扣减。InnoDB会对更新涉及的记录加锁，并发更新会按锁规则检查条件，因此库存不足的请求不能扣成负数；扣库存和写订单应置于同一数据库事务，业务异常须回滚。唯一业务号或唯一约束另行解决重复请求，不能把防超卖等同于幂等。

版本口径：MySQL InnoDB。

**🔍 面试追问（AI生成）**：
- 影响行数为0一定表示库存不足吗？ **简答**：也可能记录不存在或其他条件不满足；需要按业务约定区分，不能仅凭0编造原因。

**实际来源**：
- [南京某小厂java实习面经](https://www.nowcoder.com/feed/main/detail/0da5ca7b308e49d985dd22aa5fe3a9fc)（采集日 2026-10-27，南京某小厂（匿名，作者自述））

<a id="mysql-count-execution-pipeline"></a>

## mysql-count-execution-pipeline · SELECT COUNT(*)经过哪些执行节点

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：AI参考答案：以MySQL 8.0与InnoDB为例，请求经过连接与权限检查、SQL解析、优化器选访问路径，再由执行器调用存储引擎扫描并聚合，最终返回计数。COUNT(*)统计符合条件的行，包括字段为NULL的行。无过滤条件时通常选择较小的可用二级索引扫描，没有合适索引则扫描聚簇索引；InnoDB受事务可见性影响，不能直接使用一个全局精确行数。具体扫描路径仍需看执行计划。

**实际来源**：
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="mysql-covering-index-avoid-lookup"></a>

## mysql-covering-index-avoid-lookup · 如何利用覆盖索引减少回表

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：AI参考答案：让查询所需的过滤、返回等列尽量由同一个索引提供，可以减少从二级索引再次访问聚簇索引的操作。例如按业务查询模式设计联合索引并只选择必要列，避免无目的SELECT *。InnoDB二级索引通常包含主键，查询主键也可被覆盖。索引越宽越占空间、增加写入成本，不能把全部字段都塞入索引；需要结合EXPLAIN与实测验证，事务可见性等细节也可能影响实际访问。

**实际来源**：
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="mysql-engine-index-storage"></a>

## mysql-engine-index-storage · 不同MySQL存储引擎如何存放索引与数据

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：AI参考答案：InnoDB通常以B+树组织索引，聚簇索引叶子保存完整行，二级索引叶子保存索引键和主键，读取其他列时可能再查聚簇索引。没有显式主键时按规则选择合适唯一键或生成隐藏行标识。MyISAM的索引与数据分开存放，索引叶子通过数据地址定位记录。MEMORY可使用HASH或BTREE索引。回答应先明确引擎，不能把所有引擎的索引叶子都说成保存行数据。

**实际来源**：
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="mysql-explain-plan-reading"></a>

## mysql-explain-plan-reading · EXPLAIN执行计划怎么看

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：EXPLAIN主要观察优化器选择的访问路径。结合type判断访问方式，possible_keys和key区分候选与实际索引，key_len辅助分析索引使用情况，rows与filtered查看估计扫描和过滤规模，Extra了解覆盖索引、额外排序等信息。字段要联动分析，不能仅凭用了索引就断言高效；估计值也不是实际耗时。MySQL 8.0.18起提供EXPLAIN ANALYZE，会实际执行支持的查询并给出运行信息，生产使用前需评估开销。

**🔍 面试追问（AI生成）**：
- Using filesort一定表示磁盘排序吗？ **简答**：不一定，它表示不能直接按所需索引顺序完成排序，具体是否落盘还取决于数据规模、内存及执行方式。

**实际来源**：
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）

<a id="mysql-group-by-class-count"></a>

## mysql-group-by-class-count · 如何统计每个年级各班的学生数

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：假设 student 表中每行代表一名学生，字段为 id、grade、class，可以写 SELECT grade, class, COUNT(*) AS student_count FROM student GROUP BY grade, class。把年级一起分组，是为了避免不同年级的同名班级合并。COUNT(*) 统计行数，COUNT(字段) 会忽略该字段为 NULL 的行。若还要展示没有学生的班级，应从班级表 LEFT JOIN 学生表，并统计学生ID，不能对连接后的空行直接用 COUNT(*)。

**实际来源**：
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）

<a id="mysql-group-sum-top-ties"></a>

## mysql-group-sum-top-ties · 如何查询学生总分最高者并保留并列

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：先按学生分组计算SUM(score)，再取最高总分对应的全部学生。MySQL 8.0可先在派生表或CTE中聚合，再用DENSE_RANK() OVER(ORDER BY total DESC)排名，筛选排名为1；也可以把聚合结果与最大总分比较。不能只用ORDER BY总分DESC LIMIT 1，因为它只返回一行，可能漏掉并列者。原题仅给姓名、科目和分数；若现实中可能同名，应补充稳定学号分组，并明确重复科目、补考和NULL分数的计算规则。

版本口径：MySQL 8.0窗口函数。

**🔍 面试追问（AI生成）**：
- 为什么不能直接按姓名就认定学生唯一？ **简答**：同名学生会被错误合并；真实表应使用学号或其他稳定学生ID，原题未提供时明确这一假设。

**实际来源**：
- [佛山宏旺 java实习生](https://www.nowcoder.com/feed/main/detail/5083b0fbb75e480db6e8db2bbafc1195)（采集日 2026-10-27，佛山宏旺（原文标题））

<a id="mysql-index-unusable-scenarios"></a>

## mysql-index-unusable-scenarios · 哪些情况使索引难以有效定位数据

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：AI参考答案：常见情况有在索引列上进行函数或运算、某些隐式类型转换、联合索引缺少可用前导列，以及LIKE以通配符开头，导致普通B+树难以形成有效查找范围。OR条件能否利用索引要结合各分支与优化器判断。即使存在可用索引，选择性低或回表成本高时优化器也可能选扫描。应区分无法有效定位和成本选择，结合EXPLAIN与实际数据验证，避免把范围条件后的列一概说成完全无用。

**实际来源**：
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="mysql-inner-left-join"></a>

## mysql-inner-left-join · INNER JOIN与LEFT JOIN的结果差异

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：INNER JOIN只保留满足连接条件的匹配行；LEFT JOIN除匹配行外，还保留左表未匹配的行，并把对应右表列补为NULL。一对多关系仍可能产生多行结果，不能理解为左连接永远与左表行数相同。右表筛选条件放在ON中或WHERE中可能改变结果：WHERE若要求右表列等于某值，通常会排除那些补NULL的未匹配行。应先明确是否需要保留左表记录，再决定条件位置。

**实际来源**：
- [27届学院本Agent秋招（OC已拒）](https://www.nowcoder.com/discuss/932329388496945152)（采集日 2026-10-26，匿名公司）

<a id="mysql-innodb-lock-types"></a>

## mysql-innodb-lock-types · InnoDB有哪些锁及锁定范围

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：AI参考答案：可从共享锁和排他锁、表级意向锁，以及索引上的记录锁、间隙锁与临键锁说明。记录锁锁住索引记录，间隙锁限制区间插入，临键锁结合二者；还存在插入意向锁与特定配置下的自增锁。实际锁范围由隔离级别、索引和查询条件共同决定，不能认为按主键以外条件更新就一定锁整表，也不能把普通一致性读说成都加行锁。

**实际来源**：
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））

<a id="mysql-like-index-range"></a>

## mysql-like-index-range · LIKE查询是否一定无法使用索引

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：AI参考答案：不一定。普通B+树索引下，LIKE以固定字符串开头，如name LIKE 'abc%'，通常能提取前缀范围；以%或_开头往往不能靠前缀定位，但覆盖索引扫描仍可能出现，不能等同于完全不访问索引。实际选择还受字符集、排序规则、参数形式及数据选择性影响。应通过EXPLAIN区分范围扫描与全索引扫描，前缀匹配之后也可能需要检查完整LIKE条件。

**实际来源**：
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="mysql-mvcc-consistent-read"></a>

## mysql-mvcc-consistent-read · InnoDB的MVCC如何工作

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：InnoDB通过行版本信息、undo日志中的历史版本和Read View实现多版本并发控制，让一致性读按可见性规则找到合适版本，减少读写互相阻塞。在读已提交级别，每次一致性读通常创建新的Read View；可重复读通常复用事务内首次一致性读建立的视图。更新和锁定读属于当前读，需要结合锁机制分析。MVCC不是复制整张表，也不意味着所有读都无锁，或能单独解决任何隔离级别下的幻读。

**🔍 面试追问（AI生成）**：
- 为什么长事务可能增加历史版本负担？ **简答**：仍活跃的旧Read View可能需要较早版本，影响undo历史清理，应关注事务持续时间和实际访问模式。

**实际来源**：
- [熙牛医疗 杭州java实习生 一面面经 2026.9.3](https://www.nowcoder.com/feed/main/detail/6512d3ef462a49cbb0aa5167d57d372f)（采集日 2026-10-25，熙牛医疗）

<a id="mysql-pagination-offset-keyset"></a>

## mysql-pagination-offset-keyset · MySQL如何分页查询

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：常见方式是配合稳定的ORDER BY使用LIMIT offset,count。偏移量较大时，即使只返回少量行，也可能先扫描并丢弃大量前置记录，深分页成本较高。连续翻页可考虑基于上页最后一个排序键的游标分页，并以唯一键打破排序值相同的情况，结合合适索引减少扫描。游标分页不便直接跳任意页；并发插入删除时也要明确展示一致性需求，不能只改LIMIT就保证页面永远无重复或遗漏。

**实际来源**：
- [华盛通JAVA实习生二面](https://www.nowcoder.com/feed/main/detail/fd30324de36044c69ab16437026163d4)（采集日 2026-10-25，华盛通）

<a id="mysql-transaction-isolation-levels"></a>

## mysql-transaction-isolation-levels · 事务的四种隔离级别

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：AI参考答案：四种级别是读未提交、读已提交、可重复读和串行化，隔离增强通常伴随并发成本。InnoDB默认可重复读，普通一致性读通常复用事务内首次一致性读建立的快照；读已提交每次一致性读可建立新视图。更新与锁定读按当前版本并结合锁工作，不能套用快照读结论。幻读应区分读方式、锁范围与事务场景，不能说一个级别能无条件消除所有并发异常。

**实际来源**：
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））

<a id="mysql-union-versus-union-all"></a>

## mysql-union-versus-union-all · UNION与UNION ALL的区别

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：UNION合并多个兼容查询结果时会去除重复行；UNION ALL保留所有行，通常能省去去重处理，但不能据此保证任何场景都更快。各查询返回列数须一致，对应列类型应能兼容，重复判断针对结果行而非只看主键。业务需要保留明细或已保证结果互斥时可优先考虑UNION ALL；需要集合去重时使用UNION，并结合数据量检查执行计划和资源开销。

**实际来源**：
- [广东某公司java实习生面经](https://www.nowcoder.com/feed/main/detail/6fe8d56b45144d4b81f0082cb0f35572)（采集日 2026-10-23，匿名广东公司）

<a id="nacos-registry-config"></a>

## nacos-registry-config · Nacos的注册发现与配置作用

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：Nacos常用于服务注册发现和集中配置管理。服务把实例地址注册到注册中心，调用方据此发现可用实例；配置中心则管理配置并通知客户端变化，具体一致性和推送行为取决于版本与配置。它不等于网关，也不自动替业务保证分布式事务。回答时区分服务发现与配置管理两种职责；自己的项目没引入Nacos，就不要说已经依赖它完成微服务治理。

版本口径：通用职责说明；未假定具体Nacos版本，两份项目当前未核实到Nacos业务接入。

**实际来源**：
- [28届Java后端实习面试](https://www.nowcoder.com/discuss/941324379416166400)（采集日 2026-10-21，百川云璟）

<a id="optimistic-concurrency-control"></a>

## optimistic-concurrency-control · 乐观锁的思想与实现

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：AI参考答案：乐观并发控制假设冲突较少，先读取旧值或版本，更新时原子校验它是否变化，成功才提交修改，失败则按业务重试或返回冲突。Java原子类常利用CAS，数据库也可用版本号条件更新，作用范围不同。要关注高竞争下的重试开销、ABA问题和复合操作的原子边界；它不表示完全没有底层同步，也不能靠普通先查后改保证正确。

**实际来源**：
- [用友 Java实习面经](https://www.nowcoder.com/discuss/784203612955090944)（采集日 2026-11-01，用友）

<a id="os-thread-scheduling-unit"></a>

## os-thread-scheduling-unit · CPU调度的基本单位是什么

**次数**：1；**领域**：计算机网络与操作系统。

**A（AI参考答案）**：在通常的现代通用操作系统面试语境中，线程是CPU调度的基本单位，进程主要作为资源分配与隔离的单位。一个进程可含多个线程，线程共享进程地址空间，但各自有执行上下文和栈，内核调度可运行线程到CPU上执行。若问题说的是CPU“执行”的最小单位，需要先澄清它问调度单位还是机器指令，不能混为一谈；Java虚拟线程又由JVM调度到载体线程上，内核并非直接调度每个虚拟线程。

版本口径：现代操作系统通常语境；虚拟线程边界另行说明。

**实际来源**：
- [佛山宏旺 java实习生](https://www.nowcoder.com/feed/main/detail/5083b0fbb75e480db6e8db2bbafc1195)（采集日 2026-10-27，佛山宏旺（原文标题））

<a id="project-java-language-benefits"></a>

## project-java-language-benefits · 如何说明Java优势在项目中的实际运用

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：AI参考答案：通用AI参考思路：把语言优势与真实实现对应，例如用接口和多态隔离可替换实现，用成熟类库处理集合、并发和数据库访问，用JVM工具观察运行状态。可移植性还受JDK版本、本地依赖和部署环境限制，垃圾回收也不等于无需管理连接等外部资源。只讲自己代码能证明的选择及代价；原文没有说明具体优势与项目细节，不能补写技术经历或性能收益。

**实际来源**：
- [阅文面试结束，一共四面[Java]](https://www.nowcoder.com/discuss/353155938444058624)（采集日 2026-11-03，阅文）

<a id="project-mq-database-update-boundary"></a>

## project-mq-database-update-boundary · 如何说明消息异步驱动的数据库更新内容

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：AI参考答案：通用思路：先明确实际业务事件、生产者、消息字段、消费者及更新的表和状态，再解释为什么可以异步，以及用户何时看到最终结果。数据库写入需考虑幂等键、状态流转校验、重复与乱序消息、失败重试和补偿；还要说明原事务提交与消息发送之间的一致性方案。原面经没有披露更新内容，不能替作者或用户填成订单、库存等具体经历，只能结合真实实现作答。

**实际来源**：
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="project-multithreading-implementation"></a>

## project-multithreading-implementation · 项目中的多线程如何实现与说明

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：AI参考答案：通用AI参考思路：先指出真实可并行的任务及为何需要异步，再按代码说明任务提交、受控线程池、结果汇总和关闭方式。共享数据需明确锁、原子操作或线程隔离，任务还要处理异常、超时、取消和队列满时的策略。多线程会增加调度与下游压力，不能默认一定提速。原文没有披露实现，不应替作者或回答者虚构线程数、吞吐或已经使用的框架。

**实际来源**：
- [浪潮暑期实习java开发面经](https://www.nowcoder.com/discuss/353156399897190400)（采集日 2026-11-03，浪潮）

<a id="project-role-model"></a>

## project-role-model · 项目角色数量与权限模型设计

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：先列出真实角色及各自允许的操作，再区分身份认证、角色授权和具体资源归属。角色决定能否进入某类接口，资源校验决定能否操作这条数据，二者不能互相替代。角色数量要按自己的代码回答，避免套用原面经作者的系统。设计时可把稳定的角色与可变的权限分离；若代码仅实现固定角色注解，就如实说明没有完整的动态RBAC管理。

**实际来源**：
- [28届Java后端实习面试](https://www.nowcoder.com/discuss/941324379416166400)（采集日 2026-10-21，百川云璟）

<a id="project-technical-problem-solving"></a>

## project-technical-problem-solving · 如何讲述项目难点与解决过程

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：AI参考答案：通用AI参考思路：选择自己确实参与的问题，说明触发场景、影响范围和限制条件，再展示如何通过日志、监控、复现或代码阅读定位根因。比较候选方案的成本与风险，解释采用方案、边界处理和验证方式，并交代遗留问题。没有实测数据就描述可核查的现象和验证步骤，不编造性能收益；原文未公开项目实现，不能替作者或回答者补写某次故障经历。

**实际来源**：
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）

<a id="project-threadlocal-usage-evidence"></a>

## project-threadlocal-usage-evidence · 如何说明项目中的ThreadLocal用途

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：AI参考答案：通用思路：先如实确认是否使用，再说明保存什么、谁设置、谁读取、何时清理，以及调用是否跨线程。常见场景是请求用户上下文或链路标识，入口设置、业务读取、finally中remove，防止线程池复用造成数据串用。异步任务需明确传递上下文，不能假设自动继承。若项目没有使用，应直接说明，并解释可替代的参数传递方案；不能把这些例子当作个人实现。

**实际来源**：
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="rag-query-pipeline"></a>

## rag-query-pipeline · Spring AI与RAG的问答链路

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：先区分离线建库和在线问答：建库时解析文档、分块、生成向量并保存文本及来源；在线收到问题后做身份与权限校验，按需改写问题并生成查询向量，结合关键词或向量检索取回候选，过滤和重排后组装带上下文的提示词，再调用模型并返回答案与引用。Spring AI可提供模型、向量存储和检索链的集成能力，具体组件依所用版本配置。检索无证据时应说明不足，不能把模型生成内容冒充文档事实；还需控制上下文长度和超时。

版本口径：Spring AI具体API依版本配置。

**实际来源**：
- [南京某小厂java实习面经](https://www.nowcoder.com/feed/main/detail/0da5ca7b308e49d985dd22aa5fe3a9fc)（采集日 2026-10-27，南京某小厂（匿名，作者自述））

<a id="redis-cache-breakdown"></a>

## redis-cache-breakdown · 缓存删除后大量请求回源怎么办

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：这是热点 key 失效造成的缓存击穿，区别于访问不存在数据的缓存穿透和大量 key 同时失效的雪崩。可以为同一热点 key 做互斥重建：获得锁后再次检查缓存，只有必要时才查库回填，其他请求有限等待或降级；锁必须有过期时间并校验持有者后释放。允许短暂旧数据时可用逻辑过期和异步刷新。还需限制数据库并发，因为锁超时、等待耗尽或缓存故障仍可能导致并发回源。

**🔍 面试追问（AI生成）**：
- 为什么拿到重建锁后还要再次查询缓存？ **简答**：等待期间前一个持锁请求可能已经完成回填，双重检查可以避免再次查询数据库和重复重建。

**实际来源**：
- [南京车300 Java 实习面经](https://www.nowcoder.com/feed/main/detail/8b78085106ae45a4bada11cb75141d8f)（采集日 2026-10-24，南京车300）

<a id="redis-characteristics-tradeoffs"></a>

## redis-characteristics-tradeoffs · Redis的特点与使用边界

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：AI参考答案：Redis以内存数据访问为主，提供字符串、哈希、列表、集合和有序集合等结构，常用于缓存、计数和排行榜，也可配置持久化、复制与集群。需要权衡内存成本、过期淘汰和故障恢复时的数据丢失窗口，不能默认数据永不丢失。以常见Redis开源版本为例，核心命令处理以串行为主，但网络IO及后台任务可使用其他线程或进程，不能笼统说整个Redis只有一个线程。

**实际来源**：
- [恒生电子Java实习超短面经](https://www.nowcoder.com/discuss/353156540611895296)（采集日 2026-11-01，恒生电子）

<a id="redis-cluster-hash-slots"></a>

## redis-cluster-hash-slots · Redis Cluster的哈希槽

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：Redis Cluster把键空间划分为16384个哈希槽，节点负责其中一部分；通常对键计算CRC16再取模来确定槽位置，客户端根据槽映射定位节点。花括号中的有效hash tag可以让相关键落入同一槽。扩缩容迁移的是槽及其数据，客户端还需处理MOVED或ASK重定向。它不是简单按键数量均分，多键事务和Lua脚本也不能任意跨槽执行。

**实际来源**：
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））

<a id="redis-distributed-lock-mechanism"></a>

## redis-distributed-lock-mechanism · Redis分布式锁的原理与配置

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：单个Redis实例上可用SET key 唯一标识 NX PX 租期原子加锁，失败后按策略重试或退出；释放时需原子比较所有者标识再删除，避免误删别人已重新获得的锁。租期过短可能让业务并发执行，过长会延迟故障恢复；还需考虑续期、主从切换与持久化边界。工程中可使用Redisson，但必须说明实际等待和租期配置，数据库幂等与约束仍需保留。

**实际来源**：
- [昆山java后端小厂面经](https://www.nowcoder.com/feed/main/detail/bcf78a7db16f4d22a7ce33aca1358876)（采集日 2026-10-22，匿名昆山小厂（标题自述））

<a id="redis-expiration-and-eviction"></a>

## redis-expiration-and-eviction · Redis过期与内存淘汰的区别

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：过期处理针对设置了TTL且已到期的键，Redis会在访问时惰性删除，并周期性主动检查部分过期键。内存淘汰则在达到maxmemory限制后，依据noeviction、allkeys或volatile范围内的LRU、LFU、随机等策略决定是否及如何释放数据；具体可选策略以版本为准。二者触发条件不同，设置TTL不代表内存永远够用，也不能用缓存淘汰承载必须可靠保存的业务状态。

**实际来源**：
- [昆山java后端小厂面经](https://www.nowcoder.com/feed/main/detail/bcf78a7db16f4d22a7ce33aca1358876)（采集日 2026-10-22，匿名昆山小厂（标题自述））

<a id="redis-hyperloglog-principle"></a>

## redis-hyperloglog-principle · HyperLogLog的用途与原理

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：HyperLogLog用概率统计估计集合基数，适合UV等允许少量误差的大规模去重计数，不能枚举元素或判断某个元素是否存在。它对元素哈希后分桶，通过各桶观察到的特定位模式估计基数，再做统计校正。Redis实现的标准误差约0.81%，稠密表示通常约12KB；PFADD用于加入、PFCOUNT用于估计、PFMERGE用于合并。要求精确去重时应选Set等结构。

**实际来源**：
- [昆山java后端小厂面经](https://www.nowcoder.com/feed/main/detail/bcf78a7db16f4d22a7ce33aca1358876)（采集日 2026-10-22，匿名昆山小厂（标题自述））

<a id="redis-lock-lease-renewal"></a>

## redis-lock-lease-renewal · 分布式锁的租期与续期

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：锁租期用于在持有者故障时释放资源，但业务耗时超过租期可能出现两个持有者并发执行。续期应确认所有者身份，且只在持锁进程仍存活并满足条件时延长，不能直接无条件续命。以Redisson为例，默认看门狗续期与显式指定leaseTime的调用语义不同，需结合实际版本和代码说明；即使有续期，长暂停和网络故障仍要求业务幂等、数据库约束或其他正确性兜底。

**实际来源**：
- [广东某公司java实习生面经](https://www.nowcoder.com/feed/main/detail/6fe8d56b45144d4b81f0082cb0f35572)（采集日 2026-10-23，匿名广东公司）

<a id="redis-lock-random-ttl"></a>

## redis-lock-random-ttl · 分布式锁与随机TTL

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：应先确认原题说的是锁的租期加随机量，还是失败重试的随机退避，两者目的不同。随机退避可减少多个客户端同时重试的竞争；缓存TTL加随机量常用于打散集中失效。给锁租期加随机量并不能保证业务在过期前完成，也不能解决误解锁、故障切换或幂等问题。锁仍要有所有者校验、合理租期或续期和数据库兜底，不能把随机TTL当作锁正确性的证明。

**实际来源**：
- [昆山java后端小厂面经](https://www.nowcoder.com/feed/main/detail/bcf78a7db16f4d22a7ce33aca1358876)（采集日 2026-10-22，匿名昆山小厂（标题自述））

<a id="redis-lua-stock-admission"></a>

## redis-lua-stock-admission · Lua库存预扣与MySQL扣库存如何取舍

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：Lua把库存检查和扣减放到Redis服务端一次执行，减少网络往返；同一节点上的脚本执行不被其他命令插入，库存为1时，先执行者扣成0，后执行者检查后失败。高并发场景可用它提前拦截无库存请求，减轻数据库压力，但MySQL条件更新本身也能防超卖。Redis预扣成功不等于订单落库成功，还需处理重复请求、异步落库失败补偿和对账；脚本运行报错也不代表自动回滚已执行的写操作。

**🔍 面试追问（AI生成）**：
- Redis Cluster下多key脚本要注意什么？ **简答**：相关key须位于同一哈希槽，可设计一致的hash tag；脚本原子执行不解决跨节点或Redis与MySQL的事务一致性。

**实际来源**：
- [南京某小厂java实习面经](https://www.nowcoder.com/feed/main/detail/0da5ca7b308e49d985dd22aa5fe3a9fc)（采集日 2026-10-27，南京某小厂（匿名，作者自述））

<a id="redis-memory-exhaustion-troubleshooting"></a>

## redis-memory-exhaustion-troubleshooting · Redis内存不足如何定位与处理

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：AI参考答案：先区分达到maxmemory后的写入OOM报错与操作系统因内存不足终止进程。结合INFO memory、键数量和TTL分布，观察数据增长、大key、客户端缓冲及内存碎片；可用MEMORY USAGE抽样定位，避免在线上执行高开销全量操作。确认业务后清理无用数据、补齐过期时间或拆分大key，并评估容量和淘汰策略。持久化、复制还需额外内存，不能把maxmemory直接等同于进程RSS上限。

**实际来源**：
- [纯干货-华为OD面经 [Java]](https://juejin.cn/post/7370994785656668187)（采集日 2026-11-02，华为OD）

<a id="redis-persistence-rdb-aof"></a>

## redis-persistence-rdb-aof · Redis的RDB与AOF持久化

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：RDB保存某时刻的数据快照，文件紧凑、恢复快，但两次快照之间的修改可能丢失；后台快照还要考虑fork与写时复制成本。AOF记录写操作，丢失窗口取决于刷盘策略，文件与重写也有成本。二者可结合使用，但持久化不等于高可用或零丢失，仍需备份恢复演练。Redis7引入多部件AOF等变化，不能把旧版本的单文件细节当成所有版本都相同。

版本口径：Redis常用RDB/AOF原理；Redis7多部件AOF需与旧版区分。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="redis-project-purposes"></a>

## redis-project-purposes · Redis在项目中的用途

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：回答要从真实业务出发，常见用途包括会话状态、读多写少缓存、计数与原子准入，但不能只罗列数据结构。会话要解释过期与撤销，缓存要解释命中、空值及更新策略，计数和准入要解释原子范围及故障窗口。Redis与MySQL之间并非天然一致，必须按各自权威数据和补偿路径说明取舍；没有实现的用途不应包装为项目亮点。

**实际来源**：
- [唯智信息技术 Java开发实习生 一面面经 2026.9.16](https://www.nowcoder.com/feed/main/detail/e00abf3b34e94e4398194442a9a826fb)（采集日 2026-10-21，唯智信息技术）

<a id="redis-ranking-design"></a>

## redis-ranking-design · 微博热搜排行榜如何存储和更新

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：可以用 ZSet 的成员保存话题ID、score 保存热度，通过 ZADD 更新分数，用 ZINCRBY 增量更新，再按分数倒序取 Top N；标题等详情单独存储，避免把所有信息塞进成员字符串。热度可综合浏览、搜索和互动并定期衰减，批量重算时先构建新版本再切换，降低读到半成品的风险。还要约定同分排序、保留条数、异常流量去重和数据恢复方式；具体权重属于业务设计，不应编造平台真实算法。

**实际来源**：
- [南京车300 Java 实习面经](https://www.nowcoder.com/feed/main/detail/8b78085106ae45a4bada11cb75141d8f)（采集日 2026-10-24，南京车300）

<a id="redis-set-versus-zset"></a>

## redis-set-versus-zset · Redis Set 与 ZSet 的区别

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：Set 保存不重复成员，不维护分数排序，适合标签、去重和集合交并差；ZSet 同样保证成员唯一，但每个成员关联一个分数，可以按分数或排名查询，适合排行榜和延时任务的时间索引。选择时主要看是否需要排序、范围和排名，而不是是否允许重复；两者都不允许相同成员出现多份。ZSet 还要明确分数精度与同分成员的排序规则，避免把它当成可任意重复的有序列表。

**实际来源**：
- [南京车300 Java 实习面经](https://www.nowcoder.com/feed/main/detail/8b78085106ae45a4bada11cb75141d8f)（采集日 2026-10-24，南京车300）

<a id="redis-set-zset-encoding-comparison"></a>

## redis-set-zset-encoding-comparison · Redis Set与ZSet的底层编码如何选择

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：AI参考答案：Set提供无序去重语义，常见编码是哈希表或小型纯整数集合的intset；Redis 7.2起还支持小型Set使用listpack。ZSet维护成员与分数，小集合可用紧凑编码，Redis 7常见listpack，较大集合通常结合字典与跳跃表，分别支持按成员查分和有序范围遍历。编码会按版本、元素大小及数量阈值转换，可用OBJECT ENCODING核实，不能只凭类型断言编码。

**实际来源**：
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="redis-topology-deployment-discussion"></a>

## redis-topology-deployment-discussion · 如何说明Redis主从、哨兵与分片部署

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：AI参考答案：通用AI参考思路：先如实回答是否亲自搭建，再区分三种职责。主从复制同步数据并可分担读流量，异步复制可能产生延迟；Sentinel监控主从并协调故障转移，不负责数据分片；Redis Cluster把键空间按哈希槽分配给不同主节点，并配合副本提供可用性。实际部署还需验证客户端重连、故障恢复和数据丢失窗口，未搭建过不能编造配置或故障演练经历。

**实际来源**：
- [北京小厂Java实习面经 oc](https://www.nowcoder.com/discuss/497888682959974400)（采集日 2026-11-03，匿名（北京小厂））

<a id="redis-zset-skiplist"></a>

## redis-zset-skiplist · ZSet场景、编码与跳跃表

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：AI参考答案：ZSet以唯一成员关联分数，适合排行榜、排名查询和按时间排序的任务索引。常见较大集合编码结合字典与跳跃表，字典方便按成员查询，跳跃表以多层有序链表加速定位并支持范围遍历，平均查找和插入为O(log n)。小集合可能使用紧凑编码，旧版本有ziplist，Redis 7常见listpack；应按版本与阈值说明，不能认为每个ZSet始终都是跳跃表。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="rocketmq-architecture-components"></a>

## rocketmq-architecture-components · RocketMQ的核心架构组件有哪些

**次数**：1；**领域**：RabbitMQ / 消息队列。

**A（AI参考答案）**：AI参考答案：以经典RocketMQ 4.x架构为例，Producer发送消息，Broker负责存储、投递及消费进度等服务，Consumer订阅处理，NameServer提供Broker与Topic路由发现。客户端查询路由后与相应Broker通信，NameServer不负责保存业务消息。Topic下有多个队列，可分布在不同Broker上。部署时还需考虑副本、高可用与消费组；RocketMQ 5.x还可能涉及Proxy等组件，应明确版本和部署模式。

**实际来源**：
- [高德java一面面经](https://www.nowcoder.com/discuss/868599400765874176)（采集日 2026-11-04，高德）

<a id="rpc-invocation-pipeline"></a>

## rpc-invocation-pipeline · RPC为何看起来像调用本地方法

**次数**：1；**领域**：计算机网络与操作系统。

**A（AI参考答案）**：RPC框架通常用客户端代理提供与服务接口相似的方法调用入口：代理把服务名、方法、参数和请求ID编码序列化，通过网络发送；服务端解码后定位实现并执行，将结果或异常信息返回，客户端再关联请求并反序列化。因此相似的是使用方式，实际还多了网络延迟、超时、连接失败和版本兼容问题。超时不代表服务端一定没执行，写操作不能盲目重试，需要幂等设计；鉴权、限流与服务发现也应按场景配置。

**实际来源**：
- [佛山宏旺 java实习生](https://www.nowcoder.com/feed/main/detail/5083b0fbb75e480db6e8db2bbafc1195)（采集日 2026-10-27，佛山宏旺（原文标题））

<a id="search-inverted-index"></a>

## search-inverted-index · 倒排索引是什么

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：AI参考答案：正排关系从文档找到词或字段，倒排索引则从词项找到包含它的文档列表。文本经分析器分词、规范化后建立词典和倒排列表，列表可记录文档标识、词频和位置；查询时对相关列表做交并等运算，并据相关性规则排序。位置等信息可支持短语查询。倒排结构适合全文检索，但词项分析、更新和存储都有成本；它不是数据库B+树索引，也不能直接把词频等同于最终相关性分数。

**实际来源**：
- [贝壳Java实习一二面面经](https://www.nowcoder.com/discuss/353156432944111616)（采集日 2026-10-31，贝壳）

<a id="server-periodic-push"></a>

## server-periodic-push · 后端如何每15秒向前端推送消息

**次数**：1；**领域**：计算机网络与操作系统。

**A（AI参考答案）**：如果只是前端定期取最新状态，15秒轮询最简单，但这属于前端主动请求；需要后端主动推送时，单向通知可选 SSE，双向交互可选 WebSocket。服务端用调度器生成事件，再推送给已建立的连接，不应为每个连接长期占用一个独立业务线程。还要处理连接认证、断线重连、心跳、慢客户端和发送失败，关闭连接时释放资源；消息需要补发时可带事件序号和有限历史。

**实际来源**：
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）

<a id="single-sign-on-design"></a>

## single-sign-on-design · 单点登录如何实现

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：单点登录要解决用户在多个业务系统间只认证一次的问题，可使用统一身份提供方和标准协议，例如OpenID Connect授权码流程。业务系统把用户引导到认证中心，认证完成后校验回调状态并交换、校验令牌，再建立自己的登录态；跨域时不能简单共享任意Cookie。还要设计令牌有效期、退出及撤销策略。JWT只是令牌的一种格式，给各系统发JWT不等于已经完成安全的单点登录。

**实际来源**：
- [重庆小小小厂面试](https://www.nowcoder.com/feed/main/detail/3375e792921b46a0ae44aefae6fbcba3)（采集日 2026-10-26，重庆某小厂（匿名））

<a id="singleton-pattern-thread-safety"></a>

## singleton-pattern-thread-safety · 单例模式与线程安全

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：单例用于在特定类加载器范围内控制某类实例数量，可用静态内部类、枚举或其他正确的初始化方式实现。双重检查锁定需要volatile等条件保证安全发布，不能只检查两次null就认为线程安全。单例只限制实例，不代表实例中的可变状态自动线程安全；容器中的singleton作用域也不等于整个JVM全局唯一。应先确认共享需求，避免滥用全局状态影响测试和依赖管理。

**实际来源**：
- [广东某公司java实习生面经](https://www.nowcoder.com/feed/main/detail/6fe8d56b45144d4b81f0082cb0f35572)（采集日 2026-10-23，匿名广东公司）

<a id="spring-aop-advice-types"></a>

## spring-aop-advice-types · AOP通知类型与环绕通知

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：常见通知包括Before、After、AfterReturning、AfterThrowing和Around。Around可在目标调用前后执行逻辑，通过ProceedingJoinPoint.proceed继续调用，必要时检查参数、返回值及异常。原题“环形切面的三个方法”表述不明确，应先请面试官澄清，不能编造固定三种方法；若指环绕通知API，可结合proceed、getArgs和getSignature解释，但不声称这就是原题唯一含义。

**实际来源**：
- [昆山java后端小厂面经](https://www.nowcoder.com/feed/main/detail/bcf78a7db16f4d22a7ce33aca1358876)（采集日 2026-10-22，匿名昆山小厂（标题自述））

<a id="spring-boot-core-mechanisms"></a>

## spring-boot-core-mechanisms · Spring Boot的核心机制

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：Spring Boot基于Spring容器，通过starter组织常用依赖，通过条件化自动配置提供约定好的Bean，并支持外部化配置和嵌入式服务器，减少重复搭建工作。自动配置会检查类路径、属性及已有Bean，并非把所有组件无条件注册。以Boot 2.7为例可通过AutoConfiguration.imports声明自动配置候选；具体导入方式应结合版本，不把Boot 3要求直接套到现有Boot 2项目。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））

<a id="spring-common-annotations"></a>

## spring-common-annotations · Spring常见注解及职责

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：可按职责组织：Component及Service、Repository等标记组件，Configuration和Bean声明配置与Bean，Autowired或Resource用于依赖注入，RestController、RequestMapping及各HTTP方法映射处理Web接口，Transactional声明事务边界。注解并不是写上就自动生效，仍依赖扫描、Bean生命周期与相应处理器或代理。说明一个实际用例和限制，比无差别背注解名更有用。

版本口径：Spring Framework/Boot2.x；Resource在项目中为javax.annotation包。

**实际来源**：
- [唯智信息技术 Java开发实习生 一面面经 2026.9.16](https://www.nowcoder.com/feed/main/detail/e00abf3b34e94e4398194442a9a826fb)（采集日 2026-10-21，唯智信息技术）

<a id="spring-postconstruct-lifecycle"></a>

## spring-postconstruct-lifecycle · PostConstruct的作用与时机

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：PostConstruct标记由容器管理Bean的初始化回调，通常在依赖注入完成后调用，因此可读取已注入依赖；它不是构造函数之前执行，也不代表整个应用及外部系统全部就绪。适合轻量初始化或检查，不宜直接承载很慢且不幂等的任务。还要注意该时机与代理建立的关系，不能指望同Bean的事务方法在初始化内部自调用就自动被代理拦截。

版本口径：两项目Java8/Boot2使用javax.annotation；Boot3迁移时相关包名为jakarta.annotation。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="spring-startup-runner"></a>

## spring-startup-runner · 应用启动后执行初始化逻辑

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：应先明确逻辑需要运行到哪个生命周期阶段。Bean自己的初始化可用PostConstruct；需要应用上下文准备后执行一次启动逻辑，可考虑ApplicationRunner或CommandLineRunner，并控制顺序与失败策略。扫描整表等重任务会延长启动，宜分页、有界执行或转后台，避免阻塞就绪。多实例部署时“每进程一次”不等于“全系统一次”，仍需幂等、锁或单独任务协调。

版本口径：Spring Boot2.x生命周期；未声称项目已实现启动扫描整表。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="sql-injection-prevention"></a>

## sql-injection-prevention · 如何防止SQL注入

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：首选预编译语句和参数绑定，让数据作为参数传递，避免把用户输入拼接成SQL结构。MyBatis的#{}通常对应参数绑定，${}是直接文本替换，处理排序列或表名时应使用固定映射或白名单，不能把任意输入直接代入。参数绑定不代表可动态替换所有SQL语法，也不能替代权限控制；应配合最小数据库权限、输入约束及日志审计，不依赖简单过滤几个关键词。

**实际来源**：
- [广东某公司java实习生面经](https://www.nowcoder.com/feed/main/detail/6fe8d56b45144d4b81f0082cb0f35572)（采集日 2026-10-23，匿名广东公司）

<a id="sqlite-versus-mysql-selection"></a>

## sqlite-versus-mysql-selection · SQLite与MySQL如何选型

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：SQLite是嵌入式数据库，部署轻、无需独立数据库服务，适合本地工具、单机应用或低写并发场景；同一数据库文件的写入并发有明显约束。MySQL采用独立服务，适合多个应用实例共享数据，并提供更完整的并发管理和运维能力。选型要看访问方式、写入量、事务需求及备份扩展成本。原作者选择SQLite不代表用户两项目也使用SQLite，不能代编个人选型经历。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））

<a id="tcp-versus-udp"></a>

## tcp-versus-udp · TCP与UDP的区别

**次数**：1；**领域**：计算机网络与操作系统。

**A（AI参考答案）**：AI参考答案：TCP提供面向连接的可靠有序字节流，通过序号、确认、重传、流量控制和拥塞控制等机制传输数据，不保留应用消息边界。UDP以数据报为单位，无需TCP式连接握手，不承诺可靠交付或顺序，应用可自行设计这些能力。选择取决于延迟、丢包容忍度和协议要求；不能简单说UDP必然更快，也不能说使用UDP就无法实现可靠通信。

**实际来源**：
- [用友 Java实习面经](https://www.nowcoder.com/discuss/784203612955090944)（采集日 2026-11-01，用友）

<a id="thread-interrupt-cooperative-cancel"></a>

## thread-interrupt-cooperative-cancel · 线程interrupt的作用

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：interrupt是协作式中断请求，不是强制杀死线程。普通运行中的线程通常只是被设置中断标志，需要主动检查并退出；处于sleep、wait或join等可中断等待时，通常会抛出InterruptedException并清除中断标志。捕获异常后应按业务决定向上抛出、结束任务或恢复标志，不能无条件吞掉。部分阻塞操作有各自的中断规则，因此取消任务还要处理资源关闭和退出路径，不能只调用interrupt就认为任务已经停止。

**实际来源**：
- [华盛通JAVA实习生二面](https://www.nowcoder.com/feed/main/detail/fd30324de36044c69ab16437026163d4)（采集日 2026-10-25，华盛通）

<a id="transactional-outbox-pattern"></a>

## transactional-outbox-pattern · 订单和本地消息表为何放在同一事务

**次数**：1；**领域**：RabbitMQ / 消息队列。

**A（AI参考答案）**：本地消息表用于把订单变更与待发送事件一起写入同一数据库事务：提交时两者同时保存，回滚时都不生效，避免订单成功却没有可重试的消息记录。事务外由可靠投递任务读取消息，发送成功并确认后更新状态，失败按策略重试。它解决的是本地事务与消息投递之间的衔接，不是数据库和MQ天然组成一个原子事务；发送后更新状态前宕机可能导致重复投递，因此消费者还要按事件ID或业务唯一键幂等处理，并监控积压和最终失败。

**🔍 面试追问（AI生成）**：
- 收到MQ确认后才写消息表可以吗？ **简答**：会重新引入订单提交与消息记录分离的失败窗口。待发送事件应先和订单原子持久化，再在事务外投递。

**实际来源**：
- [南京某小厂java实习面经](https://www.nowcoder.com/feed/main/detail/0da5ca7b308e49d985dd22aa5fe3a9fc)（采集日 2026-10-27，南京某小厂（匿名，作者自述））

<a id="web-url-request-lifecycle"></a>

## web-url-request-lifecycle · 输入URL到页面显示会经历哪些过程

**次数**：1；**领域**：计算机网络与操作系统。

**A（AI参考答案）**：AI参考答案：浏览器解析URL并检查可用缓存，通常通过DNS获得服务器地址。使用HTTP/1.1或HTTP/2时一般建立TCP连接，HTTPS还需TLS握手与证书校验；已有连接可以复用，HTTP/3则基于QUIC。请求经网关或负载均衡到达后端，后端执行业务并返回响应。浏览器解析HTML，获取样式和脚本等资源，构建页面并布局绘制。实际过程会受到缓存、代理、重定向和协议版本影响。

**实际来源**：
- [Java 后端新手的第一次面试复盘](https://www.cnblogs.com/thr-0103/p/18113538)（采集日 2026-11-02，匿名公司）

<a id="websocket-versus-http"></a>

## websocket-versus-http · WebSocket与普通HTTP的区别

**次数**：1；**领域**：计算机网络与操作系统。

**A（AI参考答案）**：普通HTTP围绕请求与响应交互，长连接只是允许复用底层连接，不等于服务端能随时主动推送任意消息。WebSocket常见实现通过HTTP/1.1 Upgrade建立连接后，使用自己的帧协议进行双向通信，适合聊天或实时协作；单向通知也可评估SSE。实际使用还要处理鉴权、心跳、断线重连和慢客户端，不能因为有持久连接就省略消息顺序、补发或业务确认机制。

**实际来源**：
- [华盛通JAVA实习生面经](https://www.nowcoder.com/feed/main/detail/45c6d1c751e84ec2b3974ec2e4af9e06)（采集日 2026-10-26，华盛通）
