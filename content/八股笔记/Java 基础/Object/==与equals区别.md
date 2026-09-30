## ==

== 大多情况下比较的是 地址
如果比较的是基本数据类型，是比较数值
如果比较的是对象（引用类型），比较的是是不是指向内存中同一个对象，也就是地址

```
String a = new String("hello");
String b = new String("hello");

System.out.println(a == b);  // 输出 false
```

用了两次 new，内存堆中两个独立的对象


## equals

equals 是 Object 类里定义的一个方法，所有的 Java 对象都继承了它。它的默认行为其实和 == 一模一样，也是比地址。
但关键在于，很多常用的类（比如 String、Integer）都把这个方法给重写了。重写之后，equals 就不再比地址了，而是去比较对象里面实际存储的内容是否相等。

上面的示例代码改为 equals 判断返回 true

但是如果这个类没有重写 equals 的话就和== 一模一样

这里有个经典的面试陷阱，就是字符串常量池的问题。

```
String c = "hello";
String d = "hello";

System.out.println(c == d); // 输出 true
```

这里为什么 `==` 比较也是 true 呢？因为当你直接用双引号创建字符串的时候，JVM 会把它扔到一个叫 "**字符串常量池**" 的地方。如果池子里已经有了 "hello"，那 d 就直接复用 c 指向的那个对象，所以它俩地址是一样的，`==` 自然就返回 true 了。