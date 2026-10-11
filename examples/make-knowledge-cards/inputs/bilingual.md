# Cache 是怎么工作的

缓存（cache）的基本思路，是把"常用的数据"放在更快的地方，避免每次都去慢速存储里取。

以 CPU 为例：CPU 访问内存（RAM）的速度远慢于访问自身寄存器，于是引入多级 cache——L1、L2、L3，越靠近 CPU 的容量越小、速度越快。数据第一次被读取时，会被复制一份到 cache 里；下一次再访问同样的数据，就能直接从 cache 命中（cache hit），不必再去 RAM。

这里有个关键概念叫 locality（局部性），它有两种：temporal locality（时间局部性）——刚被访问过的数据很可能马上又被访问；spatial locality（空间局部性）——访问了某个地址，往往也会访问它附近的地址。cache 之所以有效，正是因为程序通常具备这两种局部性。

如果访问的数据不在 cache 里，就称为 cache miss；此时需要从 RAM 取数据，并把这一块替换进 cache。替换时用到的规则叫替换策略（replacement policy），常见的如 LRU（least recently used，最近最少使用）。
