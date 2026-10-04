**Stream API 是 Java 8 引入的一套用于数据处理的 API，它本身不存储数据，而是对集合等数据源进行流水线式处理。**

Stream 常见操作包括 `filter` 过滤、`map` 转换、`sorted` 排序、`distinct` 去重，以及 `collect`、`count`、`reduce` 等聚合操作。

Stream 的操作可以分成**中间操作和终止操作**。像 `filter`、`map` 属于中间操作，可以进行链式调用，并且具有惰性；`collect`、`count`、`forEach` 等属于终止操作，会触发整个流水线执行。

相比 Collection，**Collection 更关注数据的存储，而 Stream 更关注数据的计算和处理**。另外 Stream 还支持 `parallelStream` 进行并行处理，但需要根据实际场景使用。