final 的作用主要有三个方面：

- 修饰类：当 final 修饰一个类时，表示这个类不能被继承，是类继承体系中的最终形态。例如，Java 中的 String 类就是用 final 修饰的，这保证了 String 类的不可变性和安全性，防止其他类通过继承来改变 String 类的行为和特性。
- 修饰方法：用 final 修饰的方法不能在子类中被重写。比如，java.lang.Object 类中的 getClass 方法就是 final 的，因为这个方法的行为是由 Java 虚拟机底层实现来保证的，不应该被子类修改。
- 修饰变量：当 final 修饰基本数据类型的变量时，该变量一旦被赋值就不能再改变。例如，`final int num = 10;`，这里的 num 就是一个常量，不能再对其进行重新赋值操作，否则会导致编译错误。对于引用数据类型，final 修饰意味着这个引用变量不能再指向其他对象，但对象本身的内容是可以改变的。例如，`final StringBuilder sb = new StringBuilder("Hello");`，不能让 sb 再指向其他 StringBuilder 对象，但可以通过 `sb.append(" World");` 来修改字符串的内容。

不可改变总之！