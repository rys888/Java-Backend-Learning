
[[#Q：Java 中的双亲委派模型是什么？有什么作用？]]
[[#Q：双亲委派可以被打破吗？]]


**双亲委派模型（Parents Delegation Model）** 是 Java 类加载机制中的一个重要概念，也是 JVM 面试的高频八股题。

先记住一句话：

**双亲委派：当一个类加载器收到类加载请求时，不会立即自己加载，而是先委托给父类加载器。如果父类加载器无法加载，才尝试自己加载。**

它主要有两个作用：

1. **避免类被重复加载。**
2. **保护 Java 核心类库，防止应用程序中的同名类冒充核心类。**

下面结合具体例子理解。

## **一、首先理解什么是类加载器**

我们之前学习过 Java 对象的创建过程：

```java
User user = new User();
```

第一步就是**类加载检查**。

但是，JVM 怎么知道 `User` 类是什么？

这就需要类加载器（ClassLoader）。

类加载器的主要作用是：

将 `.class` 文件中的字节码加载到 JVM 中，生成对应的 `Class` 对象。

例如：

```text
User.java
    ↓ javac 编译
User.class
    ↓ 类加载器
JVM
    ↓
User 类对应的 Class 对象
```

注意，类加载不等于对象创建。

加载 `User.class` 是为了让 JVM 认识这个类，而执行 `new User()` 才是在创建它的实例。

---

## **二、Java 有哪些类加载器？⭐⭐⭐⭐⭐**

以 JDK 8 为例，常见的类加载器有三个：

|**类加载器**|**作用**|
|---|---|
|启动类加载器（Bootstrap ClassLoader）|加载 Java 核心类库，例如 `java.lang.String` |
|扩展类加载器（Extension ClassLoader）|加载 Java 扩展类库|
|应用程序类加载器（Application ClassLoader）|加载应用程序 ClassPath 下的类|

它们之间的委派关系可以表示为：

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

**注意：JDK 9 及以后，Extension ClassLoader 被 Platform ClassLoader（平台类加载器）取代。**

因此，现代 Java（例如 JDK 17、21）中的典型结构是：

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

另外，这里的父子关系主要是**委派关系**，不是 Java 类之间的继承关系。

---

## **三、双亲委派的工作过程 ⭐⭐⭐⭐⭐**

假设我们编写了一个类：

```java
public class UserService {

    public void hello() {
        System.out.println("Hello");
    }
}
```

当程序需要加载 `UserService` 时：

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

整个过程可以概括为：

**先向上委托，再从上往下尝试加载。**

这里有个细节：父加载器如果已经加载过某个类，也可以直接返回已有的类加载结果，不需要重新加载。

### **对应的源码逻辑**

`ClassLoader` 中有一个重要方法：

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

这是经过简化的源码，主要为了说明双亲委派的执行逻辑。

你只需要记住：

```text
loadClass()
    │
    ▼
findLoadedClass()
    │
    │ 没加载过
    ▼
parent.loadClass()
    │
    │ 父加载器无法加载
    ▼
findClass()
    │
    ▼
当前加载器自己加载
```

---

## **四、双亲委派有什么作用？⭐⭐⭐⭐⭐**

### **1. 避免类重复加载**

假设有两个类加载器：

```text
Application ClassLoader

Custom ClassLoader
```

它们都需要加载：

```java
java.lang.String
```

如果没有双亲委派，各个加载器可能尝试自行定义同名类。

而采用双亲委派后：

```text
Custom ClassLoader
       ↓
Application ClassLoader
       ↓
Platform ClassLoader
       ↓
Bootstrap ClassLoader
       ↓
加载 java.lang.String
```

最终可以复用启动类加载器定义的 `String` 类。

这里要注意一个细节：

**双亲委派不能保证 JVM 中绝对不存在同名类。**

在 JVM 中，一个类的身份由以下两个因素共同决定：

```text
类的全限定名 + 定义它的类加载器
```

例如：

```text
com.example.User + ClassLoader A

com.example.User + ClassLoader B
```

即使类名相同，只要定义它们的类加载器不同，JVM 也会将它们视为不同的类型。

因此，双亲委派更准确的作用是：

**减少父子加载器之间重复定义类的问题，保证常规类加载体系中的类一致性。**

### **2. 保护 Java 核心类库**

这是最重要的作用。

假设你自己创建了一个类：

```java
package java.lang;

public class String {
    // 自己编写的 String
}
```

如果 JVM 随意加载应用程序中的同名类，就可能导致核心类被替换，影响程序的安全性和稳定性。

有了双亲委派：

```text
应用程序想加载 java.lang.String
              ↓
       Application ClassLoader
              ↓
       Platform ClassLoader
              ↓
       Bootstrap ClassLoader
              ↓
       找到 JDK 自带的 String
              ↓
          加载成功
```

应用程序中的同名类不会因此替换 JDK 自带的 `String`。

此外，现代 JDK 还通过包名限制、模块机制等方式保护核心类库。

所以：

**双亲委派通过优先加载可信的核心类库，降低了核心类被应用程序中的同名类冒充的风险。**

---

## **五、为什么叫“双亲委派”，而不是“单亲委派”？**

你可能会觉得奇怪：

每个 ClassLoader 不是只有一个 parent 吗？为什么叫双亲？

实际上，“双亲委派”是 Java 中的习惯译法。

英文叫：

**Parents Delegation Model**

并不代表每个类加载器都有两个父加载器。

你只需要理解成：

**父加载器优先的委派机制。**

---

## Q：双亲委派可以被打破吗？

**可以。**

双亲委派是 Java 类加载器常用的设计机制，并不是所有类加载器都必须严格遵守的规则。

例如：

### **Tomcat 的类加载机制**

你之前学过 Spring Boot，可以联系 Web 容器来理解。

假设 Tomcat 部署了两个 Web 应用：

```text
Tomcat
│
├── Web应用 A
│   └── commons-lang3 版本 A
│
└── Web应用 B
    └── commons-lang3 版本 B
```

两个应用可能依赖同一个第三方库的不同版本。

如果所有类都只能由统一的父加载器加载，就容易发生依赖冲突。

因此，Tomcat 为不同 Web 应用提供独立的类加载环境，并在一定范围内采用不同于标准父优先委派的加载策略。

```text
Tomcat
│
├── WebAppClassLoader A
│   └── 加载应用 A 的依赖
│
└── WebAppClassLoader B
    └── 加载应用 B 的依赖
```

这样可以实现应用之间的类隔离。

不过，Tomcat 并不是对所有类都简单地采用子优先加载，Java 核心类等仍然受到相应的保护。

**所以双亲委派并不是不能打破，而是可以根据具体场景调整。**

---

## Q：Java 中的双亲委派模型是什么？有什么作用？


双亲委派是 Java 类加载器的一种工作机制。

当一个类加载器收到类加载请求时，首先会检查这个类是否已经被加载。如果没有加载，就优先委托给父类加载器，父类加载器也会继续向上委托，直到启动类加载器。

如果父类加载器能够加载这个类，就直接返回加载结果；如果父类加载器无法加载，当前类加载器才会尝试自己加载。

双亲委派主要有两个作用。

**第一是避免重复加载。** 通过优先委托父加载器，减少不同加载器重复定义同一个类的问题。

**第二是保证核心类库的安全性和一致性。** 例如 `java.lang.String` 会优先由启动类加载器加载，避免应用程序中的同名类替换 JDK 核心类。

不过双亲委派并不是强制要求，像 Tomcat 的 Web 应用类加载机制就会根据类隔离需求调整委派策略。

### **最后记住三个结论**

**① 双亲委派是什么？**

```text
收到类加载请求
      ↓
检查是否已经加载
      ↓
优先委托父加载器
      ↓
父加载器无法加载
      ↓
自己尝试加载
```

**② 有什么作用？**

- 避免父子加载器重复定义类。
- 保护 Java 核心类库的安全性和一致性。

**③ 能不能打破？**

可以，例如 Tomcat 为了实现 Web 应用之间的类隔离，会采用特殊的类加载策略。

**一句话记忆：双亲委派就是“先找爸爸加载，爸爸不行我再上”，主要用于避免重复加载和保护核心类库。**