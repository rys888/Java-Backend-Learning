long 范围比 int 大，所以可以将 int 转换为 long，反之可能会导致数据丢失或者溢出
int intValue=10;
long longValue=intValue;

long longValue=100 L;
int intValue=(int) longValue;