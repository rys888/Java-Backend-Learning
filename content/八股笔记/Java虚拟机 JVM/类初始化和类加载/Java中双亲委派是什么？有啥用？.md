
[[#Q：Java 中的双亲委派模型是什么？有什么作用？]]
[[#Q：双亲委派可以被打破吗？]]


**双亲委派模型（Parents Delegation Model）** 是 Java 类加载机制里的一个核心概念，也是 JVM 面试的高频八股题。先用一句话说清楚它是什么：**类加载器收到类加载请求时，不会立刻自己去加载，而是先委托给父加载器，父加载器加载不了，才轮到自己试。**

它的作用主要两个：**一是避免类被重复加载，二是保护 Java 核心类库，防止应用程序里的同名类冒充核心类。** 下面结合具体例子来看。

## **一、先搞清楚什么是类加载器**

前面学 Java 对象创建过程的时候写过这么一行：

```java
User user = new User();
```

它的第一步就是**类加载检查**。那 JVM 怎么知道 `User` 是什么？靠的就是类加载器（ClassLoader）。

类加载器干的事就是：把 `.class` 文件里的字节码加载进 JVM，生成对应的 `Class` 对象。整个链路是：

```text
User.java
    ↓ javac 编译
User.class
    ↓ 类加载器
JVM
    ↓
User 类对应的 Class 对象
```

⚠️ 这里有个容易搞混的点：**类加载不等于对象创建。** 加载 `User.class` 只是让 JVM 认识这个类，真正创建实例是执行 `new User()` 的时候。

---

## **二、Java 有哪些类加载器？⭐⭐⭐⭐⭐**

以 JDK 8 为例，常见的是三个：

|**类加载器**|**作用**|
|---|---|
|启动类加载器（Bootstrap ClassLoader）|加载 Java 核心类库，例如 `java.lang.String`|
|扩展类加载器（Extension ClassLoader）|加载 Java 扩展类库|
|应用程序类加载器（Application ClassLoader）|加载应用程序 ClassPath 下的类|

它们之间的委派关系（箭头指向父加载器）：

```text
        Bootstrap ClassLoader
              启动类加载器
                   ↑
                   │
         Extension ClassLoader
              扩展类加载器
                   ↑
                   │
        Application ClassLoader
             应用类加载器
                   ↑
                   │
             自定义类加载器
```

⚠️ **JDK 9 及以后，Extension ClassLoader 被 Platform ClassLoader（平台类加载器）取代。** 所以 JDK 17、21 这类现代 Java 上的典型结构是：

```text
        Bootstrap ClassLoader
                   ↑
                   │
         Platform ClassLoader
                   ↑
                   │
       Application ClassLoader
                   ↑
                   │
          自定义类加载器
```

另外要注意，这里的父子关系主要是**委派关系**，不是 Java 类之间的继承关系。

---

## **三、双亲委派的工作过程 ⭐⭐⭐⭐⭐**

假设写了一个类：

```java
public class UserService {

    public void hello() {
        System.out.println("Hello");
    }
}
```

当程序需要加载 `UserService` 时，整个流程是：

```text
需要加载 UserService
         │
         ▼
Application ClassLoader
         │
         │ 先委托父加载器
         ▼
Platform ClassLoader
         │
         │ 继续向上委托
         ▼
Bootstrap ClassLoader
         │
         │ 无法加载 UserService
         ▼
Platform ClassLoader
         │
         │ 无法加载 UserService
         ▼
Application ClassLoader
         │
         │ 自己尝试加载
         ▼
    加载 UserService
```

整个过程概括成一句：**先向上委托，再从上往下尝试加载。** 这里还有个细节，父加载器如果已经加载过某个类，也可以直接返回已有的加载结果，不需要重新加载。

### **对应的源码逻辑**

`ClassLoader` 里有个很重要的方法 `loadClass()`：

```java
protected Class<?> loadClass(String name, boolean resolve)
        throws ClassNotFoundException {

    synchronized (getClassLoadingLock(name)) {

        // 1. 检查当前加载器是否已经加载过
        Class<?> c = findLoadedClass(name);

        if (c == null) {

            try {
                // 2. 优先委托父类加载器
                if (parent != null) {
                    c = parent.loadClass(name);
                } else {
                    c = findBootstrapClassOrNull(name);
                }

            } catch (ClassNotFoundException e) {
                // 父加载器找不到
            }

            // 3. 父加载器无法加载，自己再尝试
            if (c == null) {
                c = findClass(name);
            }
        }

        return c;
    }
}
```

这是简化过的源码，看三处就够了：`findLoadedClass(name)` 先查当前加载器有没有加载过这个类；没加载过就交给 `parent.loadClass(name)` 向上委托，parent 为 null 说明已经到顶了，改用 `findBootstrapClassOrNull(name)`；父加载器一路都抛 `ClassNotFoundException` 的话，最后才由 `findClass(name)` 自己加载。

所以这条链路就是 **loadClass() → findLoadedClass() → parent.loadClass() → findClass()**。

---

## **四、双亲委派有什么作用？⭐⭐⭐⭐⭐**

### **1. 避免类重复加载**

假设有两个类加载器，Application ClassLoader 和 Custom ClassLoader，它们都要加载 `java.lang.String`。如果没有双亲委派，各个加载器可能各自尝试定义同名类；有了双亲委派，请求会一路往上走：**Custom ClassLoader → Application ClassLoader → Platform ClassLoader → Bootstrap ClassLoader**，最终复用启动类加载器定义的 `String`。

⚠️ 但有个细节不能忽略：**双亲委派不能保证 JVM 中绝对不存在同名类。** JVM 里一个类的身份由 **类的全限定名 + 定义它的类加载器** 共同决定，`com.example.User + ClassLoader A` 和 `com.example.User + ClassLoader B` 虽然类名一样，只要定义它们的加载器不同，JVM 就当成两个不同的类型。所以更准确的说法是：**双亲委派减少的是父子加载器之间重复定义类的问题，保证常规类加载体系中的类一致性。**

### **2. 保护 Java 核心类库**

这是最重要的作用。假设自己写了一个类：

```java
package java.lang;

public class String {
    // 自己编写的 String
}
```

如果 JVM 随意加载应用程序里的同名类，核心类就可能被替换掉，程序的安全性和稳定性都没了。有了双亲委派，请求会一路走到启动类加载器：**应用程序想加载 java.lang.String → Application ClassLoader → Platform ClassLoader → Bootstrap ClassLoader → 找到 JDK 自带的 String → 加载成功**，应用程序里的同名类替换不了它。

另外，现代 JDK 还通过包名限制、模块机制等方式保护核心类库。所以这条作用可以概括为：**优先加载可信的核心类库，降低核心类被应用程序中同名类冒充的风险。**

---

## **五、为什么叫“双亲委派”，而不是“单亲委派”？**

可能会觉得奇怪：每个 ClassLoader 不是只有一个 parent 吗，为什么叫双亲？其实“双亲委派”是 Java 里的习惯译法，英文是 **Parents Delegation Model**，并不代表每个类加载器都有两个父加载器，可以理解成 **父加载器优先的委派机制**。

---

## Q：双亲委派可以被打破吗？

**可以。**

双亲委派是 Java 类加载器常用的设计机制，并不是所有类加载器都必须严格遵守的规则，比如 Tomcat 的类加载机制。

### **Tomcat 的类加载机制**

学过 Spring Boot 的话，这里可以联系 Web 容器来理解。假设 Tomcat 上部署了两个 Web 应用：

```text
Tomcat
│
├── Web应用 A
│   └── commons-lang3 版本 A
│
└── Web应用 B
    └── commons-lang3 版本 B
```

两个应用可能依赖同一个第三方库的不同版本，如果所有类都只能由统一的父加载器加载，就容易发生依赖冲突。所以 Tomcat 给不同 Web 应用提供独立的类加载环境，在一定范围内采用不同于标准父优先委派的加载策略：

```text
Tomcat
│
├── WebAppClassLoader A
│   └── 加载应用 A 的依赖
│
└── WebAppClassLoader B
    └── 加载应用 B 的依赖
```

这样就能实现应用之间的类隔离。不过 Tomcat 也不是对所有类都简单地子优先加载，Java 核心类这些仍然受到保护。**所以双亲委派不是不能被打破，而是可以按具体场景调整。**

---

## Q：Java 中的双亲委派模型是什么？有什么作用？

双亲委派是 Java 类加载器的一种工作机制。类加载器收到加载请求时，先检查这个类是否已经被加载；没加载就优先委托给父加载器，父加载器也会继续向上委托，直到启动类加载器。父加载器能加载就直接返回结果，加载不了当前加载器才自己尝试。

作用主要有两个。**第一是避免重复加载**，通过优先委托父加载器，减少不同加载器重复定义同一个类的问题；**第二是保证核心类库的安全性和一致性**，例如 `java.lang.String` 会优先由启动类加载器加载，避免应用程序里的同名类替换 JDK 核心类。

不过双亲委派并不是强制要求，像 Tomcat 的 Web 应用类加载机制就会根据类隔离需求调整委派策略。


**① 双亲委派是什么？** 收到类加载请求 → 检查是否已经加载 → 优先委托父加载器 → 父加载器无法加载 → 自己尝试加载。

**② 有什么作用？** 避免父子加载器重复定义类；保护 Java 核心类库的安全性和一致性。

**③ 能不能打破？** 可以，例如 Tomcat 为了实现 Web 应用之间的类隔离，会采用特殊的类加载策略。

双亲委派就是“先找爸爸加载，爸爸不行才自己上”，主要用于避免重复加载和保护核心类库。
