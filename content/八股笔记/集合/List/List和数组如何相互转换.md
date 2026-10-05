主要有两种方式，核心是用 List 的 `toArray()` 方法，重点注意「泛型和类型匹配」：

- **无参 `toArray()`（返回 Object []，不推荐）**

```
List<String> strList = new ArrayList<>();
strList.add("a");
strList.add("b");
// 返回Object[]，强转可能报错
Object[] objArr = strList.toArray();
```

这种方式返回的是 Object 数组，若强转成 String [] 会抛 `ClassCastException`，仅适合不确定数组类型的场景，基本不用。

- **带参 `toArray(T [] a)`（推荐，指定类型）**

```
List<String> strList = new ArrayList<>();
strList.add("a");
strList.add("b");
// 方式1：传入指定长度的数组
String[] strArr1 = strList.toArray(new String[strList.size()]);
// 方式2：传入空数组（JDK1.8+更高效）
String[] strArr2 = strList.toArray(new String[0]);

// 自定义对象List转数组
List<User> userList = new ArrayList<>();
userList.add(new User("张三", 20));
User[] userArr = userList.toArray(new User[0]);
```

这是最常用的方式，传入对应类型的数组，List 会把元素复制到该数组中，若传入的数组长度不足，会自动创建新数组，推荐传空数组（JDK 会优化长度）。

---

## 数组转 List

核心是用 `Arrays.asList()`，但要注意「返回的 List 不可变」和「基本类型数组的坑」：

- **普通对象数组转 List（常用）**

```
String[] strArr = {"a", "b", "c"};
// 返回固定大小的List（属于Arrays内部类，不可add/remove）
List<String> strList1 = Arrays.asList(strArr);

// 若需要可变List，包装一层ArrayList
List<String> strList2 = new ArrayList<>(Arrays.asList(strArr));
strList2.add("d"); // 正常执行
```

`Arrays.asList()` 返回的 List **不是 ArrayList**，而是 Arrays 的内部类，不支持添加 / 删除操作，想修改就套一层 ArrayList。

- **基本类型数组转 List（避坑）**

```
// 错误示例：int[]转List会变成List<int[]>, 而非List<Integer>
int[] numArr = {1, 2, 3};
List<int[]> wrongList = Arrays.asList(numArr);

// 正确方式1：手动装箱（JDK8-）
List<Integer> numList1 = new ArrayList<>();
for (int num : numArr) {
    numList1.add(num);
}

// 正确方式2：Stream流（JDK8+）
List<Integer> numList2 = Arrays.stream(numArr).boxed().collect(Collectors.toList());
```

基本类型数组（`int[]`、`long[]`）直接用 `Arrays.asList()` 会把**整个数组当成一个元素**，必须手动装箱或用 Stream 流转换为包装类（Integer）的 List。