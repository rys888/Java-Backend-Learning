
[[#Q：SpringBoot 核心原理是什么]]

Spring Boot 的核心原理可以概括为：**自动配置、Starter 依赖管理、内嵌 Web 服务器和 SpringApplication 启动机制。**

其中，**自动配置是 Spring Boot 最核心的原理，也是 Java 后端面试最常考的部分。**

## **一、Spring Boot 的四大核心机制**

|**核心机制**|**作用**|**底层实现**|
|---|---|---|
|**自动配置** ⭐⭐⭐⭐⭐|根据依赖和配置自动创建 Bean| `@EnableAutoConfiguration` + `@Conditional` |
|**Starter 启动依赖**|简化依赖管理|Maven 依赖传递|
|**内嵌 Web 服务器**|无需单独部署 Tomcat|内嵌 Tomcat、Jetty 等|
|**启动机制**|自动初始化 Spring 容器及运行环境| `SpringApplication.run()` |

### **1. 自动配置：Spring Boot 最核心的机制**

例如，我们引入 Redis Starter：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

Spring Boot 就可以根据当前环境自动配置 `RedisTemplate` 等组件。

**底层执行流程：**

```text
@SpringBootApplication
         ↓
@EnableAutoConfiguration
         ↓
AutoConfigurationImportSelector
         ↓
读取自动配置类
         ↓
@Conditional 判断是否满足条件
         ↓
向 Spring 容器注册 Bean
```

这里需要理解三个关键点：

- `@EnableAutoConfiguration`：开启自动配置。
- `AutoConfigurationImportSelector`：查找并筛选自动配置类。一般是读取依赖 JAR 包中预先注册的自动配置类。
- `@Conditional`：根据依赖、配置属性以及容器中已有的 Bean，决定是否装配。

例如：

```java
@Configuration
@ConditionalOnClass(RedisOperations.class)
public class RedisAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public RedisTemplate<Object, Object> redisTemplate(
            RedisConnectionFactory factory) {

        RedisTemplate<Object, Object> template =
                new RedisTemplate<>();

        template.setConnectionFactory(factory);
        return template;
    }
}
```

这是简化的示例。

其中：

- `@ConditionalOnClass`：存在指定类才满足配置条件。
- `@ConditionalOnMissingBean`：没有对应 Bean 才创建，允许用户自定义配置覆盖默认配置。

**自动配置的本质就是按需装配 Bean。**

### **2. Starter：简化依赖管理**

例如：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

这个 Starter 会引入 Spring MVC、内嵌 Tomcat 等相关依赖。

因此：

**Starter 负责整合依赖，自动配置负责创建和配置 Bean。**

两者相互配合，但不是同一个概念。

### **3. 内嵌 Web 服务器**

传统 Spring Web 项目通常需要将应用打包成 WAR，再部署到外部 Tomcat。

Spring Boot 可以直接运行：

```java
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

Spring Boot 在启动过程中创建 Web 应用上下文，并初始化内嵌 Tomcat。

因此，我们可以直接通过 `java -jar` 启动应用。

### **4. SpringApplication.run()：启动机制**

Spring Boot 启动流程可以简化为：

```text
SpringApplication.run()
         ↓
准备运行环境
         ↓
读取 application.yml 等配置
         ↓
创建 ApplicationContext
         ↓
加载 Bean 定义
         ↓
刷新 Spring 容器
         ↓
实例化和初始化 Bean
         ↓
启动内嵌 Tomcat
         ↓
执行 CommandLineRunner 等
         ↓
应用启动完成
```

需要注意，自动配置类的加载和 Bean 的创建主要发生在 Spring 容器初始化、刷新过程中。

---

## **二、Spring Boot 和 Spring 的区别**

这是面试经常追问的问题。

|**Spring**|**Spring Boot**|
|---|---|
|提供 IoC、AOP、事务管理等核心能力|基于 Spring，简化项目搭建与配置|
|通常需要开发者进行更多配置|提供自动配置|
|需要自行管理和组合依赖|提供 Starter|
|Web 项目可以部署到外部 Tomcat|默认支持内嵌 Web 服务器|

**Spring Boot 并没有替代 Spring，而是在 Spring 的基础上实现了约定优于配置。**

例如，Spring Boot 的事务管理底层仍然依赖 Spring AOP 和 `PlatformTransactionManager`。

---

## Q：SpringBoot 核心原理是什么

Spring Boot 的核心原理主要包括自动配置、Starter 依赖管理、内嵌 Web 服务器以及启动机制。

其中最核心的是自动配置。

Spring Boot 通过 `@SpringBootApplication` 中的 `@EnableAutoConfiguration` 开启自动配置，再通过 `AutoConfigurationImportSelector` 加载候选自动配置类。

随后根据 `@ConditionalOnClass`、`@ConditionalOnMissingBean` 等条件注解，判断是否需要向 Spring 容器注册 Bean，从而实现按需装配。

Starter 则通过 Maven 依赖传递整合相关技术栈，配合自动配置减少手动配置。

另外，Spring Boot 通过 `SpringApplication.run()` 完成环境准备、容器初始化和内嵌 Web 服务器启动，使应用可以独立运行。

所以，Spring Boot 的本质是在 Spring IoC 和 AOP 等核心能力的基础上，通过自动配置和约定优于配置的思想，简化 Spring 应用开发。