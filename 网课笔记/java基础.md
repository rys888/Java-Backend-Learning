
# Java 基础

声明，这些笔记只是主包听《黑马程序员 java 基础上》网课觉得没见过的随手记然后后期让 ai 优化的，《下》部分主包没看，直接跳了去看《JavaWeb 了》
## 目录

- [一、字符串](#一字符串)
- [二、面向对象](#二面向对象)
- [三、GUI 与事件](#三gui-与事件)
- [四、常用 API](#四常用-api)
- [五、Lambda](#五lambda)
- [六、集合](#六集合)
- [七、查找与排序](#七查找与排序)

---

## 一、字符串

### StringBuilder

字符串拼接如果放在循环里，用 `String` 会不停创建新对象，改用 `StringBuilder`。

```java
StringBuilder sb = new StringBuilder();
sb.append("张三");
sb.append(",");
sb.append(20);
String res = sb.toString();
System.out.println(res); // 张三,20
```

### StringJoiner

`StringJoiner` 用来拼带分隔符的字符串，比自己判断「是不是第一个元素」省事。

```java
StringJoiner sj = new StringJoiner(",", "[", "]");
sj.add("张三").add("李四").add("王五");
System.out.println(sj); // [张三,李四,王五]
```

> 待补充：`String` / `StringBuffer` / `StringBuilder` 三者的区别。

---

## 二、面向对象

### static

```java
static String teacherName;
```

- 静态方法只能访问静态变量和静态方法
- 非静态方法什么都能访问
- 静态方法里没有 `this`——静态成员属于类，不依赖某个对象，`this` 没有意义

### 工具类

构造函数私有（`private`），方法全部 `static`，让外界直接用类名调，不用创建对象。

### 继承

`extends`。Java 类只支持单继承，不支持多继承；但可以多层继承（A extends B，B extends C）。

```java
// Fu.java
public class Fu {
    String name;
    int age;
}

// Zi.java
public class Zi extends Fu {
    String game;
}

// TestStudent.java
public class TestStudent {
    public static void main(String[] args) {
        Zi z = new Zi();
        z.name = "dd";
        z.age = 22;
        z.game = "dd";
        System.out.println(z.name + ", " + z.age + ", " + z.game);
    }
}
```

一个 `.java` 文件里只能有一个 `public` 类，所以上面三个类要分别放三个文件。

### this 和 super

`super.name` 拿的是父类的属性，调方法同理。

子类构造方法的第一行会隐式调用 `super()`，也就是父类的无参构造。

```java
public class Person {
    String name;
    int age;

    public Person() {
        System.out.println("父类的无参构造");
    }

    public Person(String name, int age) {
        this.name = name;   // 原稿写成 int.name，应为 this.name
        this.age = age;
    }
}

public class Student extends Person {
    public Student() {
        // 这里隐藏着 super()，访问父类的无参构造
        super();
        System.out.println("子类的无参构造");
    }

    public Student(String name, int age) {
        super(name, age);   // 想调父类带参构造，必须自己写在第一行
        System.out.println("子类的带参构造");
    }
}
```

> 父类如果没有无参构造，子类构造方法就必须手动写 `super(参数)`，否则编译不过。

### 方法重写

用 `@Override`（不是 `@Overwrite`）。

它的作用是让编译器帮你检查：这个方法是不是真的重写了父类方法。名字拼错、参数写错，编译期就报错。`@Override` 的保留级别是 `SOURCE`，只存在于源码里，编译成 `.class` 后就没了，所以跟虚拟机没关系——原稿写「给程序员还有虚拟机看的」不准确。

### 多态

父类型作为参数，可以接收所有子类对象。编译看左边，运行看右边。

子类特有功能父类引用调不到，要先强转：

```java
Dog d = (Dog) a;
d.lookHome();

// Java 16+ 可以用模式匹配，省掉强转
if (a instanceof Dog d) {
    d.lookHome();
}
```

```java
// 形参写父类型，实参可以传任意子类
public void register(Person p) {
    p.show();
}

register(s); // Student s
register(a); // Administrator a
```

```java
class Animal {
    public void speak() {
        System.out.println("动物叫");
    }
}

class Dog extends Animal {
    @Override
    public void speak() {
        System.out.println("汪汪汪");
    }
}

class Cat extends Animal {
    @Override
    public void speak() {
        System.out.println("喵喵喵");
    }
}

public class Test {
    public static void main(String[] args) {
        // 父类引用指向子类对象
        Animal a1 = new Dog();
        Animal a2 = new Cat();

        a1.speak(); // 汪汪汪，执行的是 Dog 重写的方法
        a2.speak(); // 喵喵喵
    }
}
```

写法就是：`父类 引用变量 = new 子类();`

### final

- 修饰方法：最终方法，子类不能重写
- 修饰类：不能被继承
- 修饰变量：常量，只能赋值一次

修饰引用类型变量时，地址值不能改，但对象内部可以改：

```java
final Student s = new Student("zhangsan", 23);
s.setName("lisi");   // 可以，改的是对象内部
s.setAge(24);

// s = new Student("lisi", 24);   // 报错，地址值不能改
```

### 权限修饰符

![截屏2026-08-31 13.59.27](../%E9%99%84%E4%BB%B6/Java%E5%9F%BA%E7%A1%80/%E6%88%AA%E5%B1%8F2026-08-31%2013.59.27.png)

| 修饰符 | 本类 | 同包其他类 | 其他包的子类 | 任意位置 |
|---|---|---|---|---|
| `private` | ✅ | ❌ | ❌ | ❌ |
| 不写（默认） | ✅ | ✅ | ❌ | ❌ |
| `protected` | ✅ | ✅ | ✅ | ❌ |
| `public` | ✅ | ✅ | ✅ | ✅ |

重点是「默认」这一行：不写修饰符时同一个包里的其他类能访问，出了包就不行。

### 代码块

构造代码块写在成员位置，把多个构造方法里的重复代码抽出来，先执行构造代码块再执行构造方法。实际项目里不如直接抽成一个方法，用得少。

静态代码块随着类加载执行，只执行一次，适合做数据初始化。

> 区别：静态代码块类加载时执行一次；构造代码块每创建一次对象就执行一次。

### 抽象类

```java
public abstract class Person {
    public abstract void work(); // 抽象方法，没有方法体
}
```

抽象类不能实例化，但有构造方法，是给子类 `super()` 用的。

抽象类不一定有抽象方法；有抽象方法的类一定是抽象类。

抽象类的子类：要么重写全部抽象方法，要么自己也是抽象类。

### 接口

这点原稿写反了，正确的说法是：

- 抽象类的子类必须实现全部抽象方法，否则子类也得声明成 `abstract`
- 接口的实现类必须实现全部抽象方法，否则实现类也得是抽象类
- 接口里的 `default` 方法自带默认实现，实现类**可以不重写**——「可以选择」说的是这个

```java
public interface Swim {
    void swim();   // 接口方法默认就是 public abstract
}

public class Frog extends Animal implements Swim {
    @Override
    public void swim() {
        // 具体实现
    }
}
```

一个类可以一次实现多个接口：`class Frog extends Animal implements Swim, Jump`。

接口里的 `default` 方法：

```java
interface Usb {
    // 抽象方法，实现类必须重写
    void work();

    // default 方法有方法体，实现类可以不重写，直接用接口的默认逻辑
    default void showInfo() {
        System.out.println("这是 USB 设备，默认输出信息");
    }
}
```

加 `default` 的好处是给接口加新方法时，旧的实现类不用改代码。

适配器模式：先写一个类空实现接口里所有方法，真正要用的类去继承它，只重写自己关心的那几个。这样不用被迫实现一堆用不到的方法。Java 8 之后接口有了 `default`，这个模式用得少了。

### 内部类

成员内部类可以直接访问外部类的成员，包括私有的。

```java
public class Car {
    String carName;
    int carAge;
    String carColor;

    public void show() {
        System.out.println(this.carName);
        Engine e = new Engine();
        System.out.println(e.engineName);
    }

    class Engine {
        String engineName;
        int engineAge;

        public void show() {
            System.out.println(engineName);
            System.out.println(carName); // 直接访问外部类成员
        }
    }
}
```

实例化成员内部类，必须先有外部类对象，语法是 `外部类对象.new 内部类()`：

```java
Car car = new Car();
Car.Engine engine = car.new Engine();   // 原稿写的 new car.engine() 是错的
```

局部内部类定义在方法里，想用就得在方法内创建它的对象。

### 匿名内部类

格式是「定义类」和「创建对象」合在一起写，本质是匿名内部类的对象：

```java
public interface Swim {
    void swim();
}

Swim s = new Swim() {
    @Override
    public void swim() {
        System.out.println("重写的游泳方法");
    }
};
s.swim();
```

注意接口本身不能 `new`，这里 `new Swim() { ... }` 是在创建匿名内部类的对象，不是实例化接口。

匿名内部类最常用来当方法参数，省掉专门写一个实现类：

```java
method(new Swim() {
    @Override
    public void swim() {
        System.out.println("重写的游泳方法");
    }
});
```

---

## 三、GUI 与事件

GUI 部分用的是 `JFrame` 那一套 Swing 组件。这部分内容比较老，实际开发基本用不到。

事件监听：键盘监听 `KeyListener`、鼠标监听 `MouseListener`、动作监听 `ActionListener`。

> 待补充：如果课上有具体要求再补代码。

---

## 四、常用 API

- `Math`：数学运算
- `System`：`currentTimeMillis()`、`arraycopy()`、`exit()`
- `Runtime`：运行时对象
- `Object`：所有类的父类，`toString()`、`equals()`、`clone()`
- `Objects`：工具类，常用 `equals()`、`isNull()`、`nonNull()`
- 深克隆 / 浅克隆
- `BigInteger`：超大整数
- `BigDecimal`：精确小数。**不要用 `new BigDecimal(0.1)`**，二进制浮点本身就存不准；用字符串构造，或者 `BigDecimal.valueOf(0.1)`——`valueOf` 内部等价于 `new BigDecimal(Double.toString(val))`，能避开这个坑。（原稿写成 `BigDecima`，且「valueOf 已经创建好静态对象」的说法只对 `valueOf(long)` 的 0~10 成立。）
- 正则：捕获分组 `( )` 和非捕获分组 `(?: )`。爬虫部分课程去掉了。
- 日期时间
  - JDK 7：`Date`（`java.util`）、`SimpleDateFormat`、`Calendar`
  - JDK 8：`LocalDate` / `LocalTime` / `LocalDateTime` / `DateTimeFormatter`（不可变、线程安全，推荐）
- 包装类：`Byte`、`Short`、`Character`、`Integer`、`Long`、`Float`、`Double`、`Boolean`

### Arrays

工具类，方法全是 `static`，直接用类名调。

```java
int[] arr = {3, 1, 2};
System.out.println(Arrays.toString(arr)); // [3, 1, 2]
Arrays.sort(arr);
```

---

## 五、Lambda

只能在**函数式接口**（只有一个抽象方法的接口）上用。

```java
// 对比匿名内部类
Arrays.sort(arr, (a, b) -> a - b);
```

个人看法：匿名内部类虽然啰嗦，但一眼能看出「创建了什么对象、重写了哪个方法」，初学阶段更好懂。Lambda 等用熟了再上。

---

## 六、集合

### 体系

单列集合的顶层接口是 `Collection`（原稿写的「单例」是笔误），`Map` 是双列集合的顶层接口，两者没有继承关系。

- `List`：有序、可重复、有索引。`ArrayList` 是实现类之一。
- `Set`：无序、不重复、无索引。

泛型里只能写引用类型，`ArrayList<int>` 不合法，要写 `ArrayList<Integer>`。

### 迭代器

```java
Iterator<String> it = list.iterator(); // 游标停在第一个元素之前
while (it.hasNext()) {
    String str = it.next();            // next() 返回当前元素，并把游标后移一位
}
```

- `iterator()` 返回的迭代器初始并不指向任何元素，是「第一个元素之前」，第一次 `next()` 才拿到第一个
- 迭代完游标不复位，想再遍历一次得重新 `list.iterator()`
- 遍历过程中要删除元素，只能用迭代器自己的 `remove()`

```java
it.remove();          // ✅ 删掉 next() 刚返回的那个元素
// it.remove("bbb");  // ❌ Iterator.remove() 不带参数
list.remove("bbb");   // ❌ 遍历中直接改集合会抛 ConcurrentModificationException
```

> 原稿把 `it.remove("bbb")` 标成了对的，这里是个真错误：`Iterator.remove()` 没有参数。

### List

```java
List<Integer> list = new ArrayList<>();
list.add(100);
list.add(200);

list.remove(100);                  // ❗传 int，匹配的是 remove(int index)，删下标 100 → 越界
list.remove(Integer.valueOf(100)); // ✔传对象，按值删除元素 100
```

这个坑很典型：`List` 有 `remove(int index)` 和 `remove(Object o)` 两个重载，传基本类型 `int` 会优先匹配按下标删。

### ListIterator

只有 `List` 有 `listIterator()`，`Set` 没有。

```java
ListIterator<String> it = list.listIterator();
while (it.hasNext()) {
    String str = it.next();
}
it.add("qqq");   // 列表迭代器支持遍历中新增、修改
```

### ArrayList 和 LinkedList 源码分析

> 待补充。要点可以记：`ArrayList` 底层数组、查快增删慢（要扩容和搬元素）；`LinkedList` 底层双向链表、增删快查慢。

### 泛型

泛型类：

```java
public class MyArrayList<E> {
    Object[] obj = new Object[10];   // 数组不支持泛型，内部先用 Object 存
    int size;

    public boolean add(E e) {
        obj[size] = e;
        size++;
        return true;
    }

    public E get(int index) {
        return (E) obj[index];       // 取出来再强转
    }

    @Override
    public String toString() {
        return Arrays.toString(obj);
    }
}
```

泛型方法：

```java
public static <E> void addAll(ArrayList<E> list, E e1, E e2, E e3) {
    // ...
}
```

泛型接口同理，`interface Xxx<T>`。

### 泛型通配符

- `?`：表示不确定的类型，本身不等于 `E`（原稿写「等于 E」不对）
- `? extends E`：上限，能接收 `E` 或 `E` 的子类
- `? super E`：下限，能接收 `E` 或 `E` 的父类

### 各种数据结构

> 待补充。

### HashSet 和 LinkedHashSet

存自定义对象一定要重写 `equals()` 和 `hashCode()`，否则去重不生效。

`LinkedHashSet` 比 `HashSet` 多了一条双向链表来记录元素的插入顺序，所以遍历时是有序的。

![截屏2026-09-07 15.58.43](../%E9%99%84%E4%BB%B6/Java%E5%9F%BA%E7%A1%80/%E6%88%AA%E5%B1%8F2026-09-07%2015.58.43.png)

### TreeSet

第一种：让元素自身可比较，实现 `Comparable<T>` 接口。

```java
public class User implements Comparable<User> {
    private Integer age;
    private String name;

    // 按年龄升序
    @Override
    public int compareTo(User o) {
        // this 是当前对象，o 是传入的对比对象
        return Integer.compare(this.age, o.age);
    }

    @Override
    public String toString() {
        return "User{age=" + age + ", name='" + name + "'}";
    }

    // 构造、getter setter 省略
}
```

原稿写的是 `return this.age - o.age;`，功能上等价，但两数相减可能溢出，`Integer.compare()` 更稳妥。

第二种：不改 `User`，创建 `TreeSet` 时传入外部比较器 `Comparator`。

```java
User u1 = new User(20, "张三");
User u2 = new User(18, "李四");

// o1 - o2 升序，o2 - o1 降序
TreeSet<User> set = new TreeSet<>(new Comparator<User>() {
    @Override
    public int compare(User o1, User o2) {
        return o2.getAge() - o1.getAge(); // 年龄降序
    }
});

// Java 8 用 lambda 简写
TreeSet<User> set2 = new TreeSet<>((o1, o2) -> o2.getAge() - o1.getAge());
```

> `TreeSet` 判断「重复」看的是 `compareTo` / `compare` 返回是不是 0，不是 `equals`。所以按年龄排序时，两个年龄相同的 `User` 会被当成重复，只能进一个。

---

## 七、查找与排序

原稿把插入排序和查找算法混在一起了，分开记：

查找

- 基本查找
- 二分查找
- 插值查找
- 斐波那契查找
- 分块查找、分块拓展
- 哈希查找

排序

- 冒泡排序
- 选择排序
- 插入排序
- 快速排序

递归算法单独一类，是很多分治类算法的基础，不是排序。
