<!-- java-interview-daily:generated:v1 -->

# Java面试高频题库

频次=实际采集且已核实正文的不同面经数；不是提问条数、生成次数或项目练习次数。已有答案复用，新增角度需由Agent复核后修订。

当前来源 12 篇；归一问题 77 题。

| 问题 | 次数 | 领域 |
| --- | --- | --- |
| [JVM运行时内存区域](#jvm-runtime-memory-areas) | 3 | Java 并发与 JVM |
| [数据库查询如何调优](#mysql-query-tuning-workflow) | 3 | MySQL |
| [线程池提交任务流程与拒绝策略](#thread-pool-submit-rejection) | 3 | Java 并发与 JVM |
| [如何避免重复下单或重复预约](#business-request-idempotency) | 2 | 项目设计与技术选型 |
| [如何保证缓存与数据库的一致性](#cache-database-consistency) | 2 | Redis |
| [面向对象的理解与价值](#java-object-oriented-basics) | 2 | Java 基础与集合 |
| [Java常用版本与Java 17特性](#java-version-features) | 2 | Java 基础与集合 |
| [JVM的职责](#jvm-basic-responsibility) | 2 | Java 并发与 JVM |
| [如何保证消息消费幂等](#mq-consumer-idempotence) | 2 | RabbitMQ / 消息队列 |
| [Spring如何使用声明式事务](#spring-declarative-transaction) | 2 | Spring / Spring Boot / MyBatis |
| [策略模式的好处与边界](#strategy-pattern-benefits) | 2 | 项目设计与技术选型 |
| [自定义线程池与七个核心参数](#thread-pool-configuration) | 2 | Java 并发与 JVM |
| [AI 生成代码持续不符合要求怎么办](#ai-coding-requirement-iteration) | 1 | 其他问题 |
| [AI 代码能运行就能直接用于业务吗](#ai-generated-code-acceptance) | 1 | 其他问题 |
| [后端错误如何返回并在前端展示](#api-error-response) | 1 | Spring / Spring Boot / MyBatis |
| [单体与微服务开发的区别](#architecture-monolith-microservice-difference) | 1 | 项目设计与技术选型 |
| [单体是否需要拆分及如何划分服务](#architecture-service-split) | 1 | 项目设计与技术选型 |
| [ArrayList 与 HashSet 的区别](#arraylist-versus-hashset) | 1 | Java 基础与集合 |
| [逻辑过期的 key 不设置 TTL 有什么问题](#cache-logical-expiration-costs) | 1 | Redis |
| [CAS与synchronized的区别](#cas-versus-synchronized) | 1 | Java 并发与 JVM |
| [类加载、链接与初始化](#class-loading-process) | 1 | Java 并发与 JVM |
| [项目中分布式锁的实际用法](#distributed-lock-project-usage) | 1 | Redis |
| [Docker常用命令](#docker-common-commands) | 1 | 计算机网络与操作系统 |
| [BM25与KNN检索原理](#es-bm25-knn-retrieval) | 1 | 其他问题 |
| [常见垃圾回收算法](#gc-basic-algorithms) | 1 | Java 并发与 JVM |
| [垃圾判活与回收的基本机制](#gc-collection-mechanism) | 1 | Java 并发与 JVM |
| [Git 版本回退如何选择 revert 与 reset](#git-revert-versus-reset) | 1 | 其他问题 |
| [HashMap 的存储与查找原理](#hashmap-core-mechanism) | 1 | Java 基础与集合 |
| [HashMap与Hashtable的区别](#hashmap-versus-hashtable) | 1 | Java 基础与集合 |
| [HashSet 在 JDK 7 与 JDK 8 中的实现](#hashset-jdk-implementation) | 1 | Java 基础与集合 |
| [HTTP/1.1与HTTP/2的区别](#http11-versus-http2) | 1 | 计算机网络与操作系统 |
| [== 与 equals 的区别](#java-equals-versus-reference) | 1 | Java 基础与集合 |
| [Java泛型的T、问号与extends](#java-generics-bounds) | 1 | Java 基础与集合 |
| [项目为何选择某个JDK版本](#java-jdk-selection) | 1 | 项目设计与技术选型 |
| [Java多态的实现](#java-polymorphism-method-dispatch) | 1 | Java 基础与集合 |
| [Java基本类型与包装类](#java-primitive-wrappers) | 1 | Java 基础与集合 |
| [Java创建和执行线程任务的方式](#java-thread-creation) | 1 | Java 并发与 JVM |
| [堆的分代与不同收集器布局](#jvm-heap-generations) | 1 | Java 并发与 JVM |
| [OOM 与频繁 GC 如何排查](#jvm-oom-gc-troubleshooting) | 1 | Java 并发与 JVM |
| [如何用 JMeter 验证一人一单和不超卖](#load-test-order-invariants) | 1 | 项目设计与技术选型 |
| [为什么使用消息队列](#mq-business-use-cases) | 1 | RabbitMQ / 消息队列 |
| [MyBatis如何传递多个参数](#mybatis-multiple-parameters) | 1 | Spring / Spring Boot / MyBatis |
| [MyBatis与MyBatis-Plus的区别](#mybatis-plus-versus-mybatis) | 1 | Spring / Spring Boot / MyBatis |
| [联合索引中的等值、范围与条件书写顺序](#mysql-composite-equality-range) | 1 | MySQL |
| [如何统计每个年级各班的学生数](#mysql-group-by-class-count) | 1 | MySQL |
| [索引的优点与代价](#mysql-index-benefits-costs) | 1 | MySQL |
| [MySQL索引的分类与使用](#mysql-index-types) | 1 | MySQL |
| [事务的ACID特性](#mysql-transaction-acid) | 1 | MySQL |
| [UNION与UNION ALL的区别](#mysql-union-versus-union-all) | 1 | MySQL |
| [Nacos的注册发现与配置作用](#nacos-registry-config) | 1 | Spring / Spring Boot / MyBatis |
| [项目角色数量与权限模型设计](#project-role-model) | 1 | 项目设计与技术选型 |
| [缓存删除后大量请求回源怎么办](#redis-cache-breakdown) | 1 | Redis |
| [Redis Cluster的哈希槽](#redis-cluster-hash-slots) | 1 | Redis |
| [Redis分布式锁的原理与配置](#redis-distributed-lock-mechanism) | 1 | Redis |
| [Redis过期与内存淘汰的区别](#redis-expiration-and-eviction) | 1 | Redis |
| [HyperLogLog的用途与原理](#redis-hyperloglog-principle) | 1 | Redis |
| [分布式锁的租期与续期](#redis-lock-lease-renewal) | 1 | Redis |
| [分布式锁与随机TTL](#redis-lock-random-ttl) | 1 | Redis |
| [Lua在Redis Cluster中的约束](#redis-lua-cluster-safety) | 1 | Redis |
| [Redis的RDB与AOF持久化](#redis-persistence-rdb-aof) | 1 | Redis |
| [Redis在项目中的用途](#redis-project-purposes) | 1 | Redis |
| [微博热搜排行榜如何存储和更新](#redis-ranking-design) | 1 | Redis |
| [Redis Set 与 ZSet 的区别](#redis-set-versus-zset) | 1 | Redis |
| [后端如何每15秒向前端推送消息](#server-periodic-push) | 1 | 计算机网络与操作系统 |
| [单例模式与线程安全](#singleton-pattern-thread-safety) | 1 | Java 基础与集合 |
| [AOP通知类型与环绕通知](#spring-aop-advice-types) | 1 | Spring / Spring Boot / MyBatis |
| [Spring AOP的作用与实现](#spring-aop-concept) | 1 | Spring / Spring Boot / MyBatis |
| [Spring Boot自动配置原理](#spring-boot-auto-configuration) | 1 | Spring / Spring Boot / MyBatis |
| [Spring Boot的核心机制](#spring-boot-core-mechanisms) | 1 | Spring / Spring Boot / MyBatis |
| [Spring常见注解及职责](#spring-common-annotations) | 1 | Spring / Spring Boot / MyBatis |
| [PostConstruct的作用与时机](#spring-postconstruct-lifecycle) | 1 | Spring / Spring Boot / MyBatis |
| [应用启动后执行初始化逻辑](#spring-startup-runner) | 1 | Spring / Spring Boot / MyBatis |
| [Spring事务不生效与不回滚的场景](#spring-transaction-proxy-failure) | 1 | Spring / Spring Boot / MyBatis |
| [如何防止SQL注入](#sql-injection-prevention) | 1 | MySQL |
| [SQLite与MySQL如何选型](#sqlite-versus-mysql-selection) | 1 | 项目设计与技术选型 |
| [为什么使用线程池](#thread-pool-benefits) | 1 | Java 并发与 JVM |
| [ThreadLocal的场景与风险](#threadlocal-scenarios-risks) | 1 | Java 并发与 JVM |

<a id="jvm-runtime-memory-areas"></a>

## jvm-runtime-memory-areas · JVM运行时内存区域

**次数**：3；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：按JVM规范可说明程序计数器、虚拟机栈、本地方法栈、堆和方法区。计数器与栈随线程组织，堆和方法区通常在线程间共享；栈帧包含局部变量表、操作数栈等，堆主要存放对象和数组。方法区是规范概念，HotSpot在Java8后主要以元空间承载类元数据，不能把元空间当作堆内老年代。直接内存也不能简单列成规范规定的第六块运行时区域。

版本口径：JVM规范概念与HotSpot Java 8实现分开说明。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [唯智信息技术 Java开发实习生 一面面经 2026.9.16](https://www.nowcoder.com/feed/main/detail/e00abf3b34e94e4398194442a9a826fb)（采集日 2026-10-21，唯智信息技术）
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））

<a id="mysql-query-tuning-workflow"></a>

## mysql-query-tuning-workflow · 数据库查询如何调优

**次数**：3；**领域**：MySQL。

**A（AI参考答案）**：先从慢查询日志和监控定位高耗时、高调用量SQL，再用EXPLAIN检查访问路径、扫描行数、连接顺序和索引使用，结合真实数据分布判断瓶颈。常见改进包括减少返回列与数据量、设计匹配过滤和排序条件的联合索引、避免不必要回表及优化分页。修改后验证结果一致性、实际延迟和写入成本；没有实测就说明方法，不编造优化百分比或个人成果。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））

<a id="thread-pool-submit-rejection"></a>

## thread-pool-submit-rejection · 线程池提交任务流程与拒绝策略

**次数**：3；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：提交任务时，若工作线程少于核心数就尝试创建核心线程；否则尝试入队。入队成功后还会复查运行状态与工作线程情况；入队失败则尝试创建非核心线程，达到上限或无法接收时执行拒绝策略。Java内置Abort、CallerRuns、Discard和DiscardOldest。选择要结合业务是否允许丢任务，不能默认静默丢弃；关闭中的线程池也可能拒绝任务。

版本口径：Java 8 ThreadPoolExecutor。

**🔍 面试追问（AI生成）**：
- CallerRuns一定适合吗？ **简答**：它可能让调用线程执行任务从而施加反压，但会占用请求线程；线程池关闭时也不是可靠持久化机制。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））

<a id="business-request-idempotency"></a>

## business-request-idempotency · 如何避免重复下单或重复预约

**次数**：2；**领域**：项目设计与技术选型。

**A（AI参考答案）**：先明确哪些请求属于同一次业务操作，为它们分配稳定的业务请求号，在数据库建立唯一约束，并让业务写入与幂等记录在同一事务内完成。重复请求应查询并返回原结果，处理中则返回明确状态。Redis SET NX、短期令牌或前端按钮防抖可以减少重复流量，但锁过期、请求超时后重试仍可能发生，不能代替持久化约束。预约还要明确取消后能否再次预约，避免唯一键把合法操作一起拦住。

**项目结合（AI）**：采云台的 OrderController.submit 用员工ID设置5秒 SET NX 键，实际只拦短窗口重复提交，不能说已实现请求级幂等；增加稳定请求号和数据库唯一约束属于建议。研约通的迁移SQL则用 user_id、batch_id、active_flag 唯一键约束非取消预约，取消时生成列为 NULL，允许重约。这是代码及SQL设计证据，本轮没有连接数据库验证迁移已执行。

代码依据：[OrderController.submit](https://github.com/rys888/caiyuntai/blob/6845e8b3e421b8b7504a93ccb3421c56ecff7b0e/backend/cai-yun-tai/caiyuntai-server/src/main/java/com/caiyuntai/controller/user/OrderController.java#L55)；[active_flag/uk_user_batch_active](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/resources/db/phase9_reservation_lifecycle.sql#L5)。

**🔍 面试追问（AI生成）**：
- 为什么不能直接把用户ID和商品ID设为订单唯一键？ **简答**：同一用户可能合法地再次购买；唯一键应表示同一次业务请求，而不是永久禁止重复购买。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）

<a id="cache-database-consistency"></a>

## cache-database-consistency · 如何保证缓存与数据库的一致性

**次数**：2；**领域**：Redis。

**A（AI参考答案）**：常见 Cache-Aside 方案以数据库为准：读取先查缓存，未命中再查库并回填；写入先提交数据库事务，再删除缓存，后续读取重建。删除失败需要可靠重试或消息补偿，并以 TTL 限制陈旧时间。并发读写仍可能出现旧值回填，所以它通常提供最终一致性，不能直接保证强一致；更高要求可结合版本校验、串行化更新，或对关键读取直接访问数据库，再根据延迟和业务容忍度选择方案。

**项目结合（AI）**：研约通 EquipmentServiceImpl.updateEquipment 先 updateById，再调用 deleteEquipmentCache；设备状态变更和删除也会删缓存，符合数据库为准的失效思路。实际代码没有给删除失败增加可靠补偿，也存在并发回填边界，因此应表述为缓存失效策略，不能说已实现数据库与缓存强一致。可靠补偿或版本控制是后续优化建议。

代码依据：[queryEquipmentById/deleteEquipmentCache](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/service/impl/EquipmentServiceImpl.java#L54)。

**🔍 面试追问（AI生成）**：
- 延迟双删能否保证所有并发场景都不出现旧缓存？ **简答**：不能，延迟选择、失败和执行顺序仍可能出问题；它只是降低风险，不能代替一致性边界和可靠补偿。

**实际来源**：
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）
- [南京车300 Java 实习面经](https://www.nowcoder.com/feed/main/detail/8b78085106ae45a4bada11cb75141d8f)（采集日 2026-10-24，南京车300）

<a id="java-object-oriented-basics"></a>

## java-object-oriented-basics · 面向对象的理解与价值

**次数**：2；**领域**：Java 基础与集合。

**A（AI参考答案）**：面向对象把数据与操作数据的行为组织到对象中，通过封装隐藏实现细节，通过抽象和接口表达稳定契约，通过多态在调用方不依赖具体实现的情况下替换行为。它有助于控制复杂业务的职责与变化，但不是类越多越好；继承应满足合理的类型关系，复用行为也可优先组合。设计时围绕业务边界划分职责，避免所有逻辑集中在一个大类中。

**实际来源**：
- [终于找到实习了！](https://www.nowcoder.com/feed/main/detail/067e9a7c702a4c2eb87ac95c952bdea2)（采集日 2026-10-22，匿名小厂（作者自述））
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））

<a id="java-version-features"></a>

## java-version-features · Java常用版本与Java 17特性

**次数**：2；**领域**：Java 基础与集合。

**A（AI参考答案）**：应先如实说明使用版本。Java 8常见特性包括Lambda、Stream和新的日期时间API；升级到17可使用已正式发布的record、文本块、switch表达式和密封类，但这些特性并非都首次出现在17。Java 17是LTS版本，虚拟线程则到Java 21才正式发布。项目是否用到某项特性应以构建配置和源码为证，不能把可用特性说成已经使用。

**实际来源**：
- [终于找到实习了！](https://www.nowcoder.com/feed/main/detail/067e9a7c702a4c2eb87ac95c952bdea2)（采集日 2026-10-22，匿名小厂（作者自述））
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））

<a id="jvm-basic-responsibility"></a>

## jvm-basic-responsibility · JVM的职责

**次数**：2；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：JVM负责执行Java字节码，提供类加载、运行时内存管理、解释与即时编译以及垃圾回收等能力。通常先由javac把源码编译为class文件，再由具体JVM实现加载和执行；跨平台来自统一字节码规范与各平台的JVM实现。回答时区分JDK开发工具、运行环境和JVM，也不要把Java内存模型JMM与JVM运行时内存区域混为一谈。

**实际来源**：
- [终于找到实习了！](https://www.nowcoder.com/feed/main/detail/067e9a7c702a4c2eb87ac95c952bdea2)（采集日 2026-10-22，匿名小厂（作者自述））
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）

<a id="mq-consumer-idempotence"></a>

## mq-consumer-idempotence · 如何保证消息消费幂等

**次数**：2；**领域**：RabbitMQ / 消息队列。

**A（AI参考答案）**：消息可能因确认丢失或故障重试被重复投递，消费者应根据业务唯一标识判断是否已产生效果。常见做法是在同一数据库事务中写业务记录与去重记录，配合唯一约束、条件状态更新及冲突处理，事务成功后再确认消息。只在Redis写一个已消费标记会遇到标记与业务提交不同步的问题；分布式锁也不能代替持久化幂等，更不能据此声称消息只会投递一次。

**项目结合（AI）**：研约通的ReservationPersistenceServiceImpl.persist先核对预约ID对应的用户与批次，再检查是否已有占用预约；事务内条件扣MySQL名额后插入记录。消费者对成功或业务重复ACK，异常按代码NACK处理。数据库提交后、ACK前仍可能故障，因此依赖幂等兜底，不能把Redisson锁说成实现了消息只消费一次。

代码依据：[onReservationMessage/persistWithLock](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/mq/ReservationMessageConsumer.java#L40)。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））

<a id="spring-declarative-transaction"></a>

## spring-declarative-transaction · Spring如何使用声明式事务

**次数**：2；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：在Spring管理的业务Bean上使用Transactional，配置适用的事务管理器，再通过代理调用让多个数据库操作处于同一事务。需要明确传播行为、隔离级别与回滚规则；默认通常对RuntimeException和Error回滚，受检异常要按需要配置rollbackFor。数据库事务只能协调它管理的资源，不能因为同方法里也写了Redis或发MQ就认为它们会一起回滚。

版本口径：Spring代理事务，结合项目Spring Boot2.x；不扩展到未经核实的分布式事务框架。

**项目结合（AI）**：采云台submitOrder在事务内预扣预算、写主单明细并清空申领车，Redis防重键和单号序列不跟随回滚；研约通把MySQL名额扣减与预约插入放在独立持久化Service事务内，随后消费者再ACK。可分别说明本地原子性和数据库提交到消息确认之间的失败窗口。

代码依据：[OrderController.submit](https://github.com/rys888/caiyuntai/blob/6845e8b3e421b8b7504a93ccb3421c56ecff7b0e/backend/cai-yun-tai/caiyuntai-server/src/main/java/com/caiyuntai/controller/user/OrderController.java#L50)；[onReservationMessage/persistWithLock](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/mq/ReservationMessageConsumer.java#L40)。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [终于找到实习了！](https://www.nowcoder.com/feed/main/detail/067e9a7c702a4c2eb87ac95c952bdea2)（采集日 2026-10-22，匿名小厂（作者自述））

<a id="strategy-pattern-benefits"></a>

## strategy-pattern-benefits · 策略模式的好处与边界

**次数**：2；**领域**：项目设计与技术选型。

**A（AI参考答案）**：策略模式把一组可替换算法或规则封装为实现同一接口的对象，由调用方根据上下文选择策略，适合计费、校验等存在稳定调用契约而规则多变的场景。它能减少把所有分支堆在一个大方法中的耦合，方便单独测试，但会增加类和选择逻辑，并不消除分支本身。规则很少且变化不大时不必强行抽象；项目是否已使用需看实际代码，不能仅凭有接口就认定采用了策略模式。

**实际来源**：
- [广东某公司java实习生面经](https://www.nowcoder.com/feed/main/detail/6fe8d56b45144d4b81f0082cb0f35572)（采集日 2026-10-23，匿名广东公司）
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）

<a id="thread-pool-configuration"></a>

## thread-pool-configuration · 自定义线程池与七个核心参数

**次数**：2；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：ThreadPoolExecutor常见七个参数是corePoolSize、maximumPoolSize、keepAliveTime、时间单位、任务队列、ThreadFactory和拒绝处理器。配置需结合CPU或IO特征、下游容量、允许排队时间和资源限制，不能只套公式。优先使用有界队列，并给线程命名、监控活跃数和拒绝次数；长队列可能延迟扩容，最大线程数也不能超出系统可承受范围。

版本口径：Java 8 ThreadPoolExecutor。

**🔍 面试追问（AI生成）**：
- 无界队列有什么影响？ **简答**：在核心线程繁忙后通常持续入队，maximumPoolSize难以发挥预期扩容作用，还可能积压内存和延迟。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）

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

<a id="api-error-response"></a>

## api-error-response · 后端错误如何返回并在前端展示

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：后端应统一约定错误码、可读消息和请求追踪号，并用合适的 HTTP 状态表达参数错误、权限问题或服务异常。Spring 项目可以通过全局异常处理统一转换业务异常和校验异常；完整堆栈记录在服务端，前端根据稳定错误码展示提示或引导重试，不直接显示数据库语句、内部路径等细节。对可能已成功的写请求，要提供结果查询或幂等重试，避免前端收到报错后重复执行。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）

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

**项目结合（AI）**：采云台的预算与订单属于同库事务；研约通虽使用Redis和MQ，仍是单体应用。可以用这两个真实项目解释为什么先保留清晰的业务分层，而不是声称已经拆成微服务。若未来拆分，预算与订单的数据边界及预约补偿链路都需重新设计，属于演进建议。

代码依据：[OrderController.submit](https://github.com/rys888/caiyuntai/blob/6845e8b3e421b8b7504a93ccb3421c56ecff7b0e/backend/cai-yun-tai/caiyuntai-server/src/main/java/com/caiyuntai/controller/user/OrderController.java#L50)；[ReservationServiceImpl.submit](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/service/impl/ReservationServiceImpl.java#L80)。

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

<a id="class-loading-process"></a>

## class-loading-process · 类加载、链接与初始化

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：通常按加载、链接和初始化说明，链接又包括验证、准备和解析。加载得到类的二进制表示；验证检查合法性；准备为类变量分配空间并设置初始值，解析把符号引用转换为直接引用；初始化再按规则执行类初始化逻辑。各阶段未必严格一次性完成，例如解析可延迟。类加载与对象实例化不同，静态字段赋值也不能都笼统说在加载阶段执行。

版本口径：Java 8/JVM规范基础口径。

**实际来源**：
- [唯智信息技术 Java开发实习生 一面面经 2026.9.16](https://www.nowcoder.com/feed/main/detail/e00abf3b34e94e4398194442a9a826fb)（采集日 2026-10-21，唯智信息技术）

<a id="distributed-lock-project-usage"></a>

## distributed-lock-project-usage · 项目中分布式锁的实际用法

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：先说明锁保护的资源、粒度、获取方式、超时与释放，再解释为什么还需要数据库兜底。分布式锁可能因租期到期、进程暂停或网络问题失去互斥，不能把它当作业务幂等和数据库约束的替代。若锁有所有者标识，应比较后再释放，避免删除别人的锁；若给出显式租期，就必须说明超过租期的边界，不能把计划实现的锁写成已经使用。

**项目结合（AI）**：研约通消费者按用户ID获取Redisson锁，tryLock最多等待2秒、显式租期10秒，finally只在当前线程仍持有时解锁；锁内调用事务持久化。这里不能声称消费者采用默认watchdog无限续期，且数据库条件扣名额、唯一约束和幂等判断仍负责兜底。

代码依据：[onReservationMessage/persistWithLock](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/mq/ReservationMessageConsumer.java#L40)。

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

<a id="es-bm25-knn-retrieval"></a>

## es-bm25-knn-retrieval · BM25与KNN检索原理

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：BM25属于关键词相关性评分，综合词频饱和、逆文档频率和文档长度归一化，适合精确术语和文本匹配。KNN根据向量距离或相似度寻找语义相近的内容，ES可用近似向量检索降低搜索成本，但召回率与延迟受索引和候选参数影响。两者可做混合检索，但分数不能不经处理就直接相加；要根据真实查询集评估效果，不虚构项目已使用ES。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））

<a id="gc-basic-algorithms"></a>

## gc-basic-algorithms · 常见垃圾回收算法

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：常见算法有标记清除、复制和标记整理。标记清除思路直接但可能留下碎片；复制把存活对象转移到另一块区域，分配简单但需要预留空间；整理在标记后移动对象，减少碎片但增加移动成本。分代思想根据对象存活特征选择策略，不是独立的第四种基本回收算法。算法与具体收集器不同，暂停时间也受对象存活量、堆规模和实现影响。

版本口径：基础算法口径，不编造项目GC调优结果。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="gc-collection-mechanism"></a>

## gc-collection-mechanism · 垃圾判活与回收的基本机制

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：Java通常通过从GC Roots出发的可达性分析判断对象是否仍被使用，不能只看引用计数，否则循环引用难以处理。确定可回收对象后，由具体收集器选择复制、清除或整理等方式处理；不同阶段可能需要暂停应用或并发执行。垃圾回收主要管理堆内存，不替代文件、网络连接等外部资源的显式关闭，也不能保证某个对象在指定时刻马上被回收。

版本口径：JVM基础机制；与“算法有哪些”相关但不是同一原题，不合并虚增同题次数。

**实际来源**：
- [唯智信息技术 Java开发实习生 一面面经 2026.9.16](https://www.nowcoder.com/feed/main/detail/e00abf3b34e94e4398194442a9a826fb)（采集日 2026-10-21，唯智信息技术）

<a id="git-revert-versus-reset"></a>

## git-revert-versus-reset · Git 版本回退如何选择 revert 与 reset

**次数**：1；**领域**：其他问题。

**A（AI参考答案）**：已经推送并由多人共享的提交，通常用 git revert 生成一个抵消目标改动的新提交，保留历史，便于协作审查。git reset 会移动当前分支指针：soft 保留暂存和工作区，mixed 重置暂存区但保留工作区，hard 还会覆盖受影响的已跟踪文件。reset 更适合整理尚未共享的本地提交，不能把两者理解成习惯不同的等价操作；操作前应确认未提交改动和团队分支状态。

**🔍 面试追问（AI生成）**：
- revert 一定不需要处理冲突吗？ **简答**：不一定；目标提交之后的修改可能与反向补丁冲突，需要正常解决，合并提交还要明确主线父提交。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）

<a id="hashmap-core-mechanism"></a>

## hashmap-core-mechanism · HashMap 的存储与查找原理

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：HashMap 根据键的哈希值定位桶，再通过 equals 区分发生冲突的键。JDK 8 中桶采用链表或红黑树，链较长且数组容量足够时才树化，容量不足时优先扩容；元素数量超过容量与负载因子的乘积也会触发扩容。哈希分布均匀时查询平均接近 O(1)，但不能保证所有场景都为常数时间。它允许 null 键和值，不保证遍历顺序，也不适合并发修改。

**🔍 面试追问（AI生成）**：
- 为什么不能修改已经作为键的对象的判等字段？ **简答**：修改后计算出的哈希位置或 equals 结果可能与插入时不同，导致原有映射难以正常查找和删除。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）

<a id="hashmap-versus-hashtable"></a>

## hashmap-versus-hashtable · HashMap与Hashtable的区别

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：HashMap通常不提供并发安全保证，允许一个null键和多个null值；Hashtable是较早的同步容器，通常通过方法级同步保护访问，不允许null键和值。两者都通过哈希组织映射，但不能把Hashtable的方法同步理解成多个调用组成的业务操作必然原子。现代并发场景常考虑ConcurrentHashMap及其原子API，选择时还要看遍历、一致性和复合操作要求，而不是只记线程安全与否。

**实际来源**：
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））

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

<a id="java-equals-versus-reference"></a>

## java-equals-versus-reference · == 与 equals 的区别

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：== 对基本类型比较数值，对引用类型比较是否指向同一对象；equals 是对象的方法，默认实现也比较引用，但 String 等类重写后按内容判断。业务对象需要按关键字段判等时，应同时重写 equals 和 hashCode，保证相等对象具有相同哈希值，否则放入 HashMap、HashSet 可能出现查找或去重异常。比较字符串内容通常用 equals，并注意接收者为 null 时的空指针问题。

**🔍 面试追问（AI生成）**：
- 两个对象 hashCode 相同就一定相等吗？ **简答**：不一定，哈希冲突允许存在，还要通过 equals 判断；equals 相等则必须具有相同 hashCode。

**实际来源**：
- [益普科技 Java开发实习生 面经](https://www.nowcoder.com/discuss/926599685232422912)（采集日 2026-10-24，益普科技）

<a id="java-generics-bounds"></a>

## java-generics-bounds · Java泛型的T、问号与extends

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：T通常是声明时命名的类型参数，问号表示未知类型，? extends X表示某个X或其子类型，适合从中按X读取，但通常不能安全加入具体的非null值。? super X可接收X及其子类对象，读取时一般只能保证Object。Java泛型不具有协变继承关系，List<Integer>不是List<Number>的子类型；多数泛型信息经擦除，运行时也不能直接new T或使用基本类型作为类型实参。

**实际来源**：
- [昆山java后端小厂面经](https://www.nowcoder.com/feed/main/detail/bcf78a7db16f4d22a7ce33aca1358876)（采集日 2026-10-22，匿名昆山小厂（标题自述））

<a id="java-jdk-selection"></a>

## java-jdk-selection · 项目为何选择某个JDK版本

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：JDK选型先看框架最低要求、依赖兼容性、部署平台和维护周期，再评估语言特性、GC及监控工具带来的收益。Java 17是LTS版本，但长期支持期限取决于具体发行商；升级还需验证编译目标、第三方库、反射访问和回归测试。原题作者使用17不代表用户项目使用17，不能为了回答选型题把两项目已声明的Java 8写成Java 17。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））

<a id="java-polymorphism-method-dispatch"></a>

## java-polymorphism-method-dispatch · Java多态的实现

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：常见做法是通过父类或接口引用指向具体实现对象，调用被重写的实例方法时由实际对象类型决定执行实现，从而让调用方依赖稳定契约。方法重载主要在编译期根据声明类型和参数选择，不能与运行时重写混为一谈；字段、静态方法和私有方法也不能直接套用同样的动态分派结论。多态有助于扩展，但仍需控制接口职责，避免为变化很少的逻辑增加无谓层次。

**实际来源**：
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））

<a id="java-primitive-wrappers"></a>

## java-primitive-wrappers · Java基本类型与包装类

**次数**：1；**领域**：Java 基础与集合。

**A（AI参考答案）**：Java有byte、short、int、long、float、double、char、boolean八种基本类型，对应包装类为Byte、Short、Integer、Long、Float、Double、Character、Boolean。包装类可用于泛型和允许null的对象场景，自动装箱拆箱提供便利，但拆箱null会抛空指针异常。比较包装数值应关注equals语义，不能依赖引用相等或缓存范围；金额通常用BigDecimal并明确精度与舍入。

版本口径：Java 8基础口径；不把包装类缓存范围等同于所有数值都能用==比较。

**实际来源**：
- [唯智信息技术 Java开发实习生 一面面经 2026.9.16](https://www.nowcoder.com/feed/main/detail/e00abf3b34e94e4398194442a9a826fb)（采集日 2026-10-21，唯智信息技术）

<a id="java-thread-creation"></a>

## java-thread-creation · Java创建和执行线程任务的方式

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：可继承Thread重写run，或把Runnable交给Thread后调用start；需要返回值时可用Callable配合FutureTask或提交给ExecutorService。Runnable、Callable描述任务，本身不是操作系统线程；调用run只是当前线程普通方法调用，start才请求启动新线程。实际工程常使用受控线程池复用线程，并处理任务异常、超时和关闭流程，不能无界地为每个请求新建线程。

版本口径：Java 8口径，不把后续JDK虚拟线程写成两个项目已使用的实现。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="jvm-heap-generations"></a>

## jvm-heap-generations · 堆的分代与不同收集器布局

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：在常见Java8分代收集器中，堆可按年轻代和老年代讨论，年轻代通常包含Eden及两个Survivor区，对象经存活和年龄判断等规则进入老年代，但并非所有对象都必须依次走完固定路线。G1使用Region组织内存，年轻与老年代是逻辑集合，布局不能直接套成连续的三块。元空间存类元数据，不是堆内分代；回答时先说明JDK与收集器。

版本口径：Java 8常见分代收集器与G1的概念比较；不假定项目实际GC参数。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="jvm-oom-gc-troubleshooting"></a>

## jvm-oom-gc-troubleshooting · OOM 与频繁 GC 如何排查

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：先结合异常类型、GC 日志和监控区分堆不足、元空间、直接内存或线程资源耗尽，不能看到 OOM 就只调大堆。堆问题可分析堆转储中的大对象、支配关系和 GC Roots，判断是正常容量需求、分配过快还是对象被长期持有；频繁 GC 还需看回收后占用、停顿时间和分配速率。优先修复泄漏、无界队列等根因，再通过压测决定容量或收集器参数，抓取诊断数据也要控制线上开销。

**实际来源**：
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）

<a id="load-test-order-invariants"></a>

## load-test-order-invariants · 如何用 JMeter 验证一人一单和不超卖

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：先准备可回滚的测试数据，分别构造同一用户重复提交、多用户竞争有限库存、超时重试等场景，并通过并发线程与同步启动制造竞争。响应码和成功率只是过程指标，还应在测试后核对数据库：同一业务唯一键的有效订单不重复、库存不为负、成功订单数量与库存扣减一致，失败请求没有残留扣减。测试账号和请求号要参数化，避免把测试脚本重复数据造成的错误当成服务端问题；这些属于验证方案，不代表项目已做过压测。

**实际来源**：
- [南京车300 Java 实习面经](https://www.nowcoder.com/feed/main/detail/8b78085106ae45a4bada11cb75141d8f)（采集日 2026-10-24，南京车300）

<a id="mq-business-use-cases"></a>

## mq-business-use-cases · 为什么使用消息队列

**次数**：1；**领域**：RabbitMQ / 消息队列。

**A（AI参考答案）**：消息队列常用于异步处理、服务解耦和削峰，让请求先完成必要的准入与落账，再由消费者处理后续任务。它会引入重复投递、积压、顺序和一致性问题，不能只说性能更高；要说明确认机制、失败重试、幂等、监控与补偿。用户必须立即得到最终结果或强事务提交时，不能把仅已入队解释为业务成功，需设计处理中状态或改用合适的同步链路。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））

<a id="mybatis-multiple-parameters"></a>

## mybatis-multiple-parameters · MyBatis如何传递多个参数

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：Mapper可接收单个DTO或Map，也可在多个方法参数上用@Param声明稳定名称，再在XML中通过#{}绑定对应属性。多个复杂参数要明确引用路径，批量集合可配合foreach，不应依赖编译参数名或不同版本的默认命名碰巧生效。#{}处理值参数，表名、列名等结构性内容不能随意作为值绑定；必须动态选择时用白名单，避免用${}直接拼接用户输入。

**实际来源**：
- [成都小厂java面经](https://www.nowcoder.com/feed/main/detail/1f64e96cac1d4e29a6a8481b732f153a)（采集日 2026-10-23，匿名成都小厂（标题自述））

<a id="mybatis-plus-versus-mybatis"></a>

## mybatis-plus-versus-mybatis · MyBatis与MyBatis-Plus的区别

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：MyBatis负责SQL映射与结果封装，复杂查询通常通过XML或注解显式编写；MyBatis-Plus是在其基础上的增强，提供通用CRUD、条件构造器和分页等能力，减少重复代码，但不会让SQL设计、索引和事务问题自动消失。简单单表操作可用通用Mapper，复杂业务仍可写自定义SQL。应按项目依赖版本说明API，不把starter版本直接当作MyBatis核心版本。

版本口径：采云台MyBatis starter 2.2.0；研约通MyBatis-Plus 3.4.3。

**项目结合（AI）**：采云台通过Mapper接口和XML写预算条件更新；研约通在持久化Service中用LambdaUpdateWrapper表达剩余名额大于零并原子递减，复杂分页也保留Mapper XML。两者都需要明确数据库条件与事务边界，不能把用了MyBatis-Plus说成无需关注SQL。

代码依据：[BudgetMapper.deduct/release](https://github.com/rys888/caiyuntai/blob/6845e8b3e421b8b7504a93ccb3421c56ecff7b0e/backend/cai-yun-tai/caiyuntai-server/src/main/resources/mapper/BudgetMapper.xml#L31)；[onReservationMessage/persistWithLock](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/mq/ReservationMessageConsumer.java#L40)。

**实际来源**：
- [28届Java后端实习面试](https://www.nowcoder.com/discuss/941324379416166400)（采集日 2026-10-21，百川云璟）

<a id="mysql-composite-equality-range"></a>

## mysql-composite-equality-range · 联合索引中的等值、范围与条件书写顺序

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：对联合索引(a,b,c,d)，条件a=1、b=2、c=5、d>6可形成前三列等值加最后一列范围的连续索引范围，WHERE里把d写在c前面通常不改变这一逻辑。关键是索引列顺序和谓词性质，而非文本先后。“范围后不能用”也不能理解成范围列本身失效；范围后列能否用于过滤、覆盖或ICP还需区分。最终是否选择该索引及扫描多少行，要结合EXPLAIN验证。

版本口径：MySQL 8.x / InnoDB；不把优化器一定选用某索引当作保证。

**🔍 面试追问（AI生成）**：
- 范围列后还有列就完全没用了吗？ **简答**：不一定能继续缩小连续扫描区间，但仍可能用于索引条件下推或覆盖查询；需区分访问范围与过滤。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="mysql-group-by-class-count"></a>

## mysql-group-by-class-count · 如何统计每个年级各班的学生数

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：假设 student 表中每行代表一名学生，字段为 id、grade、class，可以写 SELECT grade, class, COUNT(*) AS student_count FROM student GROUP BY grade, class。把年级一起分组，是为了避免不同年级的同名班级合并。COUNT(*) 统计行数，COUNT(字段) 会忽略该字段为 NULL 的行。若还要展示没有学生的班级，应从班级表 LEFT JOIN 学生表，并统计学生ID，不能对连接后的空行直接用 COUNT(*)。

**实际来源**：
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）

<a id="mysql-index-benefits-costs"></a>

## mysql-index-benefits-costs · 索引的优点与代价

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：索引可减少满足过滤、连接或排序条件时的扫描范围，但收益取决于选择性、查询条件和执行计划。索引需要占用存储，并让插入、删除及修改相关字段承担维护成本；数量越多不一定越快。设计时围绕高频查询确定联合索引顺序，检查回表、排序及覆盖情况，再用真实数据验证。仅为低选择性字段单独建索引，或为每个字段建索引，都可能得不偿失。

**实际来源**：
- [广东某公司java实习生面经](https://www.nowcoder.com/feed/main/detail/6fe8d56b45144d4b81f0082cb0f35572)（采集日 2026-10-23，匿名广东公司）

<a id="mysql-index-types"></a>

## mysql-index-types · MySQL索引的分类与使用

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：索引可从不同维度分类：约束上有主键、唯一和普通索引，列数上有单列与联合索引；InnoDB常用B+树，主键索引组织完整行，二级索引叶子保存主键值，必要时回表。不能把这些分类并排当成互斥选项。选索引要结合过滤、关联、排序和覆盖需求，既看查询收益，也考虑写放大与空间成本；是否实际使用需看执行计划和数据分布。

版本口径：MySQL 8.x / InnoDB常用B+树场景，其他引擎能力需另行区分。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="mysql-transaction-acid"></a>

## mysql-transaction-acid · 事务的ACID特性

**次数**：1；**领域**：MySQL。

**A（AI参考答案）**：ACID指原子性、一致性、隔离性和持久性。原子性要求事务操作整体提交或回滚；一致性要求满足业务规则和数据库约束，不能只靠开启事务自动得到。隔离性控制并发事务间的相互影响，强度取决于隔离级别；持久性要求提交后的结果能够按配置保障恢复。以InnoDB为例，可从undo、redo、锁和MVCC解释实现分工，避免把每项特性归因于单一日志。

**实际来源**：
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））

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

<a id="project-role-model"></a>

## project-role-model · 项目角色数量与权限模型设计

**次数**：1；**领域**：项目设计与技术选型。

**A（AI参考答案）**：先列出真实角色及各自允许的操作，再区分身份认证、角色授权和具体资源归属。角色决定能否进入某类接口，资源校验决定能否操作这条数据，二者不能互相替代。角色数量要按自己的代码回答，避免套用原面经作者的系统。设计时可把稳定的角色与可变的权限分离；若代码仅实现固定角色注解，就如实说明没有完整的动态RBAC管理。

**项目结合（AI）**：采云台定义EMPLOYEE、PURCHASER、ADMIN，JWT拦截器写入上下文后由RoleAspect核验注解；研约通则有USER、LAB_ADMIN，角色通过后还要检查实验室归属。因此可以分别解释三角色办公采购和两角色实验室管理，不能混说成同一套权限系统。

代码依据：[UserController.login/logout](https://github.com/rys888/caiyuntai/blob/6845e8b3e421b8b7504a93ccb3421c56ecff7b0e/backend/cai-yun-tai/caiyuntai-server/src/main/java/com/caiyuntai/controller/user/UserController.java#L59)；[MvcConfig.addInterceptors](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/config/MvcConfig.java#L20)。

**实际来源**：
- [28届Java后端实习面试](https://www.nowcoder.com/discuss/941324379416166400)（采集日 2026-10-21，百川云璟）

<a id="redis-cache-breakdown"></a>

## redis-cache-breakdown · 缓存删除后大量请求回源怎么办

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：这是热点 key 失效造成的缓存击穿，区别于访问不存在数据的缓存穿透和大量 key 同时失效的雪崩。可以为同一热点 key 做互斥重建：获得锁后再次检查缓存，只有必要时才查库回填，其他请求有限等待或降级；锁必须有过期时间并校验持有者后释放。允许短暂旧数据时可用逻辑过期和异步刷新。还需限制数据库并发，因为锁超时、等待耗尽或缓存故障仍可能导致并发回源。

**项目结合（AI）**：研约通设备详情实际调用 CacheClient.queryWithMutex：未命中后尝试按 key 加锁，持锁后双检再回源，最后按 UUID 标识通过 Lua 释放锁。源码还设置了有限重试，耗尽后直接查库，因此不能说任何情况下都只有一个请求回源。queryWithLogicalExpire 虽存在于工具类，但设备详情并未调用，不能当作已启用的优化。

代码依据：[queryEquipmentById/deleteEquipmentCache](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/service/impl/EquipmentServiceImpl.java#L54)。

**🔍 面试追问（AI生成）**：
- 为什么拿到重建锁后还要再次查询缓存？ **简答**：等待期间前一个持锁请求可能已经完成回填，双重检查可以避免再次查询数据库和重复重建。

**实际来源**：
- [南京车300 Java 实习面经](https://www.nowcoder.com/feed/main/detail/8b78085106ae45a4bada11cb75141d8f)（采集日 2026-10-24，南京车300）

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

**项目结合（AI）**：研约通消费者按用户ID获取Redisson锁，tryLock最多等待2秒、显式租期10秒；锁内调用独立事务Service，finally在当前线程仍持锁时释放。这个配置不能说成默认watchdog无限续期；超过租期仍可能失去互斥，数据库幂等判断与条件扣名额继续负责兜底。

代码依据：[onReservationMessage/persistWithLock](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/mq/ReservationMessageConsumer.java#L40)。

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

<a id="redis-lua-cluster-safety"></a>

## redis-lua-cluster-safety · Lua在Redis Cluster中的约束

**次数**：1；**领域**：Redis。

**A（AI参考答案）**：Lua可把多个Redis操作放在一次脚本执行中，减少往返并避免其他命令穿插，但原子执行不等于出错时自动回滚已做修改。脚本应显式传入所访问的键，避免长时间阻塞服务；在Cluster中，相关键需满足同槽要求，可按业务设计hash tag。脚本不能把数据库和消息队列也纳入原子范围，更不能只因单机测试通过就宣称已经适配集群。

**项目结合（AI）**：研约通的预约Lua同时访问名额键与用户集合键，校验时间、余量及重复预约后执行DECR、SADD和EXPIRE。ReservationQuotaExecutor传入两个键，现有拼接未使用Cluster hash tag；因此不能声称这段代码已适配跨槽。若部署Cluster，应先设计同批次同槽键并验证，这属于待实施建议。

代码依据：[ReservationServiceImpl.submit](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/service/impl/ReservationServiceImpl.java#L80)。

**实际来源**：
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））

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

**项目结合（AI）**：采云台把JWT登录状态放Redis白名单，并缓存物资列表；研约通使用Redis Hash会话滑动续期、设备详情互斥重建，以及Lua执行批次名额和用户去重。两份代码里用途和认证形式不同，适合选一个最贴近原题的场景展开，而不是混成同一种实现。

代码依据：[UserController.login/logout](https://github.com/rys888/caiyuntai/blob/6845e8b3e421b8b7504a93ccb3421c56ecff7b0e/backend/cai-yun-tai/caiyuntai-server/src/main/java/com/caiyuntai/controller/user/UserController.java#L59)；[GoodsController.list](https://github.com/rys888/caiyuntai/blob/6845e8b3e421b8b7504a93ccb3421c56ecff7b0e/backend/cai-yun-tai/caiyuntai-server/src/main/java/com/caiyuntai/controller/user/GoodsController.java#L40)；[MvcConfig.addInterceptors](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/config/MvcConfig.java#L20)；[queryEquipmentById/deleteEquipmentCache](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/service/impl/EquipmentServiceImpl.java#L54)；[ReservationServiceImpl.submit](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/service/impl/ReservationServiceImpl.java#L80)。

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

<a id="server-periodic-push"></a>

## server-periodic-push · 后端如何每15秒向前端推送消息

**次数**：1；**领域**：计算机网络与操作系统。

**A（AI参考答案）**：如果只是前端定期取最新状态，15秒轮询最简单，但这属于前端主动请求；需要后端主动推送时，单向通知可选 SSE，双向交互可选 WebSocket。服务端用调度器生成事件，再推送给已建立的连接，不应为每个连接长期占用一个独立业务线程。还要处理连接认证、断线重连、心跳、慢客户端和发送失败，关闭连接时释放资源；消息需要补发时可带事件序号和有限历史。

**实际来源**：
- [广电数科 Java开发实习生 面经](https://www.nowcoder.com/discuss/926952182883053568)（采集日 2026-10-24，广电数科）

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

<a id="spring-aop-concept"></a>

## spring-aop-concept · Spring AOP的作用与实现

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：AOP把事务、日志或权限等横切逻辑从业务代码中分离，通过切点选择连接点并织入通知。Spring AOP通常基于JDK动态代理或CGLIB代理，在代理调用处增强方法，因此对象是否由容器管理、调用是否经过代理会影响增强生效。它不是修改所有类的任意代码位置，也不等同于完整的AspectJ编织；项目中的声明式事务可作为有代码依据的典型应用。

**实际来源**：
- [昆山java后端小厂面经](https://www.nowcoder.com/feed/main/detail/bcf78a7db16f4d22a7ce33aca1358876)（采集日 2026-10-22，匿名昆山小厂（标题自述））

<a id="spring-boot-auto-configuration"></a>

## spring-boot-auto-configuration · Spring Boot自动配置原理

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：SpringBootApplication组合了配置、组件扫描和启用自动配置等能力。自动配置导入机制发现候选配置，再根据类路径、属性和已有Bean等条件决定是否装配；例如ConditionalOnMissingBean允许用户配置覆盖默认实现。它不是无条件扫描所有依赖里的类。Boot2.x不同小版本的候选注册方式有演进，2.7支持AutoConfiguration.imports，不能把Boot3机制直接套到所有Boot2项目。

版本口径：采云台Boot2.7.3；研约通Boot2.3.12。区别2.7新候选文件与早期spring.factories机制。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

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

**项目结合（AI）**：研约通RabbitMQConfig.init使用PostConstruct配置RabbitTemplate的confirm与return回调，并打开mandatory。它设置的是消息投递反馈机制，不是此时自动提交业务预约，也不保证消费者已完成落库。可以据此说明依赖注入后做轻量初始化的真实用例。

代码依据：[publishReservationMessage/markPublishedWithRetry](https://github.com/rys888/yanyuetong/blob/0170f0c1f0f94216ba111c1d5e7ea771be4d77ce/src/main/java/com/yanyuetong/service/impl/ReservationServiceImpl.java#L236)。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="spring-startup-runner"></a>

## spring-startup-runner · 应用启动后执行初始化逻辑

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：应先明确逻辑需要运行到哪个生命周期阶段。Bean自己的初始化可用PostConstruct；需要应用上下文准备后执行一次启动逻辑，可考虑ApplicationRunner或CommandLineRunner，并控制顺序与失败策略。扫描整表等重任务会延长启动，宜分页、有界执行或转后台，避免阻塞就绪。多实例部署时“每进程一次”不等于“全系统一次”，仍需幂等、锁或单独任务协调。

版本口径：Spring Boot2.x生命周期；未声称项目已实现启动扫描整表。

**实际来源**：
- [北京小厂Java一面](https://www.nowcoder.com/feed/main/detail/85836bc50a5947f8b8f788471838c08a)（采集日 2026-10-21，匿名北京小厂（作者自述））

<a id="spring-transaction-proxy-failure"></a>

## spring-transaction-proxy-failure · Spring事务不生效与不回滚的场景

**次数**：1；**领域**：Spring / Spring Boot / MyBatis。

**A（AI参考答案）**：先区分没有进入事务与进入后没有回滚。代理模式下，同类内部直接调用、对象不是Spring管理的Bean等会绕开事务代理；方法可见性和代理类型也要结合版本判断。已进入事务时，异常被业务捕获不再抛出，或受检异常未匹配回滚规则，可能不会按预期回滚。新线程不会自动继承当前线程事务。排查要看调用链、管理器与实际SQL，不能只看方法上有注解。

版本口径：项目Spring Boot2.x代理式事务；方法可见性规则不泛化为所有Spring新版本。

**🔍 面试追问（AI生成）**：
- 把注解加在private方法上就能修复吗？ **简答**：项目这种常见代理模式不能靠private方法注解获得预期拦截，应把事务边界放在可被代理调用的业务方法并验证。

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

<a id="thread-pool-benefits"></a>

## thread-pool-benefits · 为什么使用线程池

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：线程池通过复用工作线程减少频繁创建和销毁的成本，并集中管理并发数、任务队列和生命周期。相比每个任务新建线程，它更便于限制资源、监控和实施拒绝策略，但不会让任务自动变快。需要结合CPU或IO特征、下游容量和超时要求选择线程数与有界队列，避免无界排队拖垮内存；任务异常、取消及应用关闭也要有处理策略。

**实际来源**：
- [9.10北京爱学习java开发日常实习面经](https://www.nowcoder.com/feed/main/detail/248055ff78ba49c5ad5dfa1b3ef822dd)（采集日 2026-10-22，爱学习（北京，原文标题））

<a id="threadlocal-scenarios-risks"></a>

## threadlocal-scenarios-risks · ThreadLocal的场景与风险

**次数**：1；**领域**：Java 并发与 JVM。

**A（AI参考答案）**：ThreadLocal为每个线程保存独立变量，常用于请求上下文或事务资源绑定，不负责让同一对象的并发访问自动安全。线程池会复用线程，任务结束后若不remove，旧数据可能串到下个任务；ThreadLocalMap的弱键也不能替代清理，因为值仍可能被线程长期引用。应在finally中清理，异步任务需要显式传递必要上下文，不能假设换线程后原值仍然可见。

**实际来源**：
- [java后端小厂面经](https://www.nowcoder.com/feed/main/detail/b24739216ffb4c62bfee8a06f90810b4)（采集日 2026-10-23，匿名小厂（标题自述））
