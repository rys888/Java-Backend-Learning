CopyOnWriteArrayList 底层也是通过一个数组保存数据，使用 volatile 关键字修饰数组，保证当前线程对数组对象重新赋值后，其他线程可以及时感知到。

```
private transient volatile Object[] array;
```

在写入操作时，加了一把互斥锁 ReentrantLock 以保证线程安全。

[[synchronized和reentrantlock工作原理和应用场景是什么]]

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

CopyOnWriteArrayList 是线程安全的 ArrayList 变体。
当执行修改操作时，不直接修改原数组，而是先复制一个新数组，在新数组上进行修改，然后将内部数组引用指向新数组。读操作不加锁，直接读取原数组。

- 线程安全：写操作通过 ReentrantLock 加锁，保证同一时刻只有一个线程进行写操作，复制过程对读线程无影响。
- 适用场景：适合读多写少的并发场景，比如说缓存、监听器列表。因为写操作涉及数组复制，开销较大，不适合频繁写。同时，数据最终一致性，读操作是可能读取到旧数据的。