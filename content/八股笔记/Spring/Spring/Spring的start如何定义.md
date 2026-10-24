
Spring Boot Starter 的核心作用是：**把某个功能需要的依赖、配置和 Bean 封装起来，让其他项目引入一个依赖就能使用。**

例如，你想封装一个 Redis 工具 Starter，让其他 Spring Boot 项目只需要引入依赖、配置 Redis 地址，就能直接注入工具类。

### **一、自定义 Starter 的基本步骤**

以 Spring Boot 3 为例：

**1. 创建 Starter 模块**

例如：

```text
my-redis-spring-boot-starter
├── pom.xml
├── src/main/java
│   └── com.example
│       ├── RedisProperties.java
│       ├── RedisAutoConfiguration.java
│       └── RedisHelper.java
└── src/main/resources
    └── META-INF/spring
        └── org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

**2. 定义配置属性**

```java
@ConfigurationProperties(prefix = "my.redis")
public class RedisProperties {

    private String prefix = "app";

    public String getPrefix() {
        return prefix;
    }

    public void setPrefix(String prefix) {
        this.prefix = prefix;
    }
}
```

**3. 编写需要自动注入的组件**

```java
public class RedisHelper {

    private final StringRedisTemplate redisTemplate;
    private final RedisProperties properties;

    public RedisHelper(
            StringRedisTemplate redisTemplate,
            RedisProperties properties) {
        this.redisTemplate = redisTemplate;
        this.properties = properties;
    }

    public void set(String key, String value) {
        redisTemplate.opsForValue().set(
            properties.getPrefix() + ":" + key,
            value
        );
    }
}
```

**4. 编写自动配置类（最关键）**

```java
@AutoConfiguration
@EnableConfigurationProperties(RedisProperties.class)
@ConditionalOnClass(StringRedisTemplate.class)
public class RedisAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    @ConditionalOnBean(StringRedisTemplate.class)
    public RedisHelper redisHelper(
            StringRedisTemplate redisTemplate,
            RedisProperties properties) {

        return new RedisHelper(redisTemplate, properties);
    }
}
```

这里有三个重要注解：

|**注解**|**作用**|
|---|---|
| `@AutoConfiguration` |声明自动配置类|
| `@ConditionalOnClass` |类路径存在指定类时才启用配置|
| `@ConditionalOnMissingBean` |容器没有对应 Bean 时才创建，允许用户自定义覆盖|

**5. 注册自动配置类**

在以下文件中：

```text
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

写入：

```text
com.example.RedisAutoConfiguration
```

Spring Boot 启动时就能发现这个自动配置类。

**6. 在其他项目中使用**

引入 Starter 依赖：

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>my-redis-spring-boot-starter</artifactId>
    <version>1.0.0</version>
</dependency>
```

这个 Starter 还需要在 Maven 中声明 Spring Boot 自动配置及 Redis 相关依赖，并发布到本地或远程 Maven 仓库。

然后在 `application.yml` 中配置：

```yaml
my:
  redis:
    prefix: user
```

直接注入：

```java
@Autowired
private RedisHelper redisHelper;
```

不需要再手动声明 `RedisHelper` Bean。

---

### **二、Starter 为什么能够自动生效？**

这实际上涉及 Spring Boot 的**自动配置原理**。

```text
Spring Boot 启动
       ↓
@SpringBootApplication
       ↓
@EnableAutoConfiguration
       ↓
AutoConfigurationImportSelector
       ↓
读取 AutoConfiguration.imports
       ↓
加载 RedisAutoConfiguration
       ↓
判断 @Conditional 条件
       ↓
满足条件，注册 RedisHelper Bean
       ↓
业务代码直接 @Autowired 使用
```

注意：**Starter 本身不是自动配置机制，而是用于组织依赖和自动配置的模块。** 实际开发中还可以将 Starter 和 AutoConfigure 拆成两个 Maven 模块。

另外，如果你使用的是 **Spring Boot 2.3（你之前黑马点评项目的版本）**，注册方式不同，需要在 `META-INF/spring.factories` 中配置：

```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
com.example.RedisAutoConfiguration
```

配置类通常使用 `@Configuration`，而不是 Spring Boot 3 示例中的 `@AutoConfiguration`。

### **三、面试怎么回答？**

自定义 Spring Boot Starter 主要分为四步。

首先，创建一个 Maven 模块，引入功能所需的依赖。

其次，通过 `@ConfigurationProperties` 定义配置属性，通过 `@Bean` 和 `@Conditional` 系列注解实现按条件注册 Bean。

然后，编写自动配置类，并通过 Spring Boot 2 的 `spring.factories` 或 Spring Boot 3 的 `AutoConfiguration.imports` 注册。

最后，将 Starter 打包发布，其他项目引入依赖后，Spring Boot 就会在启动时自动加载配置类并注册相关 Bean。

其核心原理是 Spring Boot 的自动配置机制，能够实现**开箱即用、按需加载、允许用户覆盖默认配置**。

**一句话记忆：Starter = 依赖封装 + 自动配置 + 条件装配。**

如果你问的是 **Spring Boot Starter 的实现原理**，以上就是面试重点；如果是 **Spring Boot 项目的启动流程（**** `SpringApplication.run()` ****）**，那是另一个知识点。