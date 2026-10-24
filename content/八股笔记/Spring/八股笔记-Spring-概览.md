---
aliases:
  - "Spring"
title: "Spring"
---

- **IOC 和 AOP**：IOC 的底层实现原理、三种依赖注入方式的区别，AOP 的动态代理机制（JDK 动态代理 vs CGLIB），以及 AOP 的实际应用场景，这两块是 Spring 面试的绝对核心。
- **循环依赖和三级缓存**：为什么需要三级缓存、二级缓存为什么不够，这个问题在面试里被问得越来越频繁，而且很容易被追问到细节。
- **Spring 事务**：事务什么时候会失效（绕过代理、方法无法被代理、异常不符合回滚规则），这是一道经典坑题，答起来很容易只说表面。
- **SpringBoot 自动装配原理**：`@SpringBootApplication` 背后的逻辑、自动配置类是怎么被发现和筛选的，这块是 SpringBoot 的核心，面试里问的很多。
- **Bean 的生命周期**：从实例化到销毁经历了哪些步骤、各个扩展点在哪里介入，这块答好了能体现对 Spring 底层的理解深度。

[[Spring-Spring-概览|Spring]]
[[SpringBoot-概览|SpringBoot]]
[[SpringMVC-概览|SpringMVC]]
[[Mybatis-概览|Mybatis]]


重点：
[[Mybatis里的]]

[[IOC和AOP通过什么机制来实现]]
[[SpringAOP的原理]]
[[@Transactional注解在什么情况下会失效]]
[[事务的隔离级别有哪些]]
[[Spring的start如何定义]]  （记不住）
SpringBoot 自动配置原理是什么，如何按需加载
[[Bean的生命周期]] 🌟
[[Spring三级缓存]]




