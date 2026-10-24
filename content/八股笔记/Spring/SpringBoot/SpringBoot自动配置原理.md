
Spring Boot 自动配置的核心原理：通过 `@EnableAutoConfiguration` 加载自动配置类，再结合 `@Conditional` 条件注解，按需向 Spring 容器注册 Bean。

简单来说：Spring Boot 根据你引入的依赖和配置文件，自动判断需要创建哪些 Bean，减少手动配置。

## 一、先举个例子理解

假设你在 Spring Boot 项目中引入：

```
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

然后配置：

```
spring:
  redis:
    host: localhost
    port: 6379
```

这里使用 Spring Boot 2.x 的配置格式。

之后就可以直接注入：

```
@Autowired
private StringRedisTemplate redisTemplate;
```

为什么我们没有手动创建 `StringRedisTemplate`，却可以直接使用？

因为 Spring Boot 的 `RedisAutoConfiguration` 帮我们完成了 Bean 的自动创建。

## 二、自动配置的完整流程 

① `@SpringBootApplication`

启动类上的核心注解

② `@EnableAutoConfiguration`

开启自动配置

③ `AutoConfigurationImportSelector`

查找并筛选候选自动配置类

④ 加载自动配置类

Spring Boot 2.3：spring.factories

Spring Boot 3：AutoConfiguration.imports

⑤ `@Conditional` 条件判断

依赖存在吗？配置启用吗？Bean 已存在吗？

⑥ 满足条件，注册 Bean

业务代码可以直接通过依赖注入使用

## 三、核心源码怎么理解？

### 1. `@SpringBootApplication`

```
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

它主要组合了三个注解：

```
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan
```

其中：

- `@SpringBootConfiguration`：标识配置类。
    
- `@ComponentScan`：扫描业务组件。
    
- `@EnableAutoConfiguration`：开启自动配置。
    

### 2. `@EnableAutoConfiguration`

它通过 `@Import` 导入 `AutoConfigurationImportSelector`，由后者查找、筛选需要加载的自动配置类。

例如：

```
RedisAutoConfiguration
DataSourceAutoConfiguration
WebMvcAutoConfiguration
...
```

但并不是这些自动配置类都会无条件创建 Bean。

### 3. `@Conditional`：按条件装配

以简化的 Redis 自动配置为例：

```
@Configuration
@ConditionalOnClass(RedisOperations.class)
public class RedisAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public StringRedisTemplate stringRedisTemplate(
            RedisConnectionFactory factory) {

        return new StringRedisTemplate(factory);
    }
}
```

这里最关键的是两个注解：

|注解|作用|
|---|---|
| `@ConditionalOnClass` |类路径存在指定类，才满足配置条件|
| `@ConditionalOnMissingBean` |容器没有对应 Bean，才创建默认 Bean|
| `@ConditionalOnProperty` |配置属性满足要求时生效|
| `@ConditionalOnBean` |容器存在指定 Bean 时生效|

例如，如果你自己定义了 `StringRedisTemplate` Bean，自动配置通常会让步，避免重复注册。

这就是 Spring Boot 自动配置的 按需装配、用户配置优先 思想。

## 四、Starter 和自动配置有什么关系？

这两个概念容易混淆。

Starter 负责整合依赖，AutoConfiguration 负责自动创建 Bean。

例如：

```
spring-boot-starter-data-redis
           │
           ▼
引入 Redis 相关依赖
           │
           ▼
Spring Boot 发现 Redis 自动配置类
           │
           ▼
判断 @Conditional 条件
           │
           ▼
创建 RedisConnectionFactory、
RedisTemplate 等 Bean
```

所以，并不是 Starter 自己在创建 Bean，而是它提供依赖，使对应自动配置有机会生效。

## 五、面试怎么回答？⭐⭐⭐⭐⭐

Spring Boot 自动配置的核心是 `@EnableAutoConfiguration` 和条件装配机制。

首先，启动类上的 `@SpringBootApplication` 包含 `@EnableAutoConfiguration`，它通过 `@Import` 引入 `AutoConfigurationImportSelector`。

然后，Spring Boot 会读取预先注册的自动配置类。

接着，Spring Boot 根据 `@ConditionalOnClass`、`@ConditionalOnBean`、`@ConditionalOnMissingBean` 等条件注解，判断当前环境是否满足配置要求。

如果条件满足，就通过配置类中的 `@Bean` 方法向 Spring 容器注册对应组件。

例如引入 Redis Starter 后，Spring Boot 可以自动创建 RedisTemplate 等 Bean，我们直接注入使用即可。

因此，自动配置的本质就是根据类路径、配置属性和容器中已有的 Bean，动态决定需要注册哪些 Bean。