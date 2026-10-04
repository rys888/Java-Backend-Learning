直接这样说：

Lambda 表达式是 Java 8 引入的一个重要特性，主要用于**简化函数式接口的实现**，可以减少匿名内部类的样板代码。

它的基本语法是 `(参数) -> {方法体}`。比如以前创建线程需要写 `Runnable` 匿名内部类，Java 8 之后可以直接写 `new Thread(() -> System.out.println("执行任务")).start()`。

Lambda 一般和**函数式接口**配合使用，也就是只有一个抽象方法的接口，比如 `Runnable`，以及 Java 8 提供的 `Function`、`Consumer`、`Supplier`、`Predicate`。

实际开发中 Lambda 经常和 **Stream API** 一起使用，比如通过 `filter` 过滤、`map` 转换集合中的数据，让代码更加简洁。

如果面试官继续问，你重点准备下面这几个追问：

- **Lambda 能用于任何接口吗？** → 不能，主要用于**函数式接口**。
- **什么是函数式接口？** → **只有一个抽象方法的接口**，通常可以用 `@FunctionalInterface` 标注。
- **Lambda 和匿名内部类完全一样吗？** → 不完全一样，例如 `this` 的语义就不同；Lambda 中的 `this` 指向外围实例，而匿名内部类中的 `this` 指向匿名内部类对象本身。
- **Lambda 常见使用场景？** → 集合/Stream 处理、排序 Comparator、线程任务、回调等。

面试时最核心的一句话可以记成：

**Lambda 是 Java 8 引入的语法特性，用简洁的方式为函数式接口提供实现，常用于 Stream、集合处理以及异步/线程任务等场景。**

