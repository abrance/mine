# solidity
  ## bool true or false; default false
     test exp 支持 &&(and) ||(or)  ==(equal) !=(not equal)

  ## int(integer) uint(unsigned integer)
     支持 + - * /
     支持 位运算 &(位与) |(位或) ~(取反) ^(异或) <<1(左移) >>(右移)

  ## 匹配这么多类型的原因是 "节约gas"
     带来一个问题，出现溢出

  ## 异常

  ## uint a = 2/4    <a 会为0，但是 uint a = 2/4 *8  <a 为4，默认会计算结果，中间值不会进行类型转换

  ## bytes1  字节 类型 bytes8 指8bit 的byte
  bytes1 public num1 = 0x7a;
  加上public 限定词，会自动生成 get方法
  bytes 类型 有.length 属性
  
  
  