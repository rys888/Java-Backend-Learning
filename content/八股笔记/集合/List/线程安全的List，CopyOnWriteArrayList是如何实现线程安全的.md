CopyOnWriteArrayList 底层也是通过一个数组保存数据，使用 volatile 关键字修饰数组，保证当前线程对数组对象重新赋值后，其他线程可以及时感知到。

```
private transient volatile Object[] array;
```

在写入操作时，加了一把互斥锁 ReentrantLock 以保证线程安全。

```
public boolean add(E e) {
    //获取锁
    final ReentrantLock lock = this.lock;
    //加锁
    lock.lock();
    try {
        //获取到当前List集合保存数据的数组
        Object[] elements = getArray();
        //获取该数组的长度（这是一个伏笔，同时len也是新数组的最后一个元素的索引值）
        int len = elements.length;
        //将当前数组拷贝一份的同时，让其长度加1
        Object[] newElements = Arrays.copyOf(elements, len + 1);
        //将加入的元素放在新数组最后一位
        setArray(newElements);
        return true;
    } finally {
        //释放锁
        lock.unlock();
    }
}
```

```
Arrays.copyOf(elements,len+1);
```

它复制数组的核心目的不是“预留容量”，而是实现 **Copy-On-Write 写时复制**。

所以也正因为如此：

**CopyOnWriteArrayList 写操作成本很高，每次 add 都可能复制整个数组，因此特别适合读多写少，而不适合频繁写入。**


### Q：CopyOnWriteArrayList 是如何实现线程安全的

CopyOnWriteArrayList 内部通过 volatile 的 Object 数组保存数据。读操作通常直接读取当前数组，不加写锁；写操作首先通过 ReentrantLock 保证多个写线程互斥，然后使用 Arrays.copyOf 复制当前数组，在新数组上完成修改，最后通过 setArray 将 volatile 数组引用指向新数组，并在 finally 中释放锁。因此它实现了写时复制，读写之间干扰较少，但写操作需要复制整个数组，所以适合读多写少的场景。