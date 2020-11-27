# solidity
  ## view pure 限定词
      view 只读取数据，不修改状态
      pure 既不修改数据，也不读取数据

  ## bytes 类型
    没有 view 和 pure 视为 修改了数据；
    创建动态数组 bytes name = new bytes(2);
    调用name.length = 5 时，会变成 bytes5 ，如果已经有了数据，那么往右加0
    bytes取第n字节 bytes[]

  ## string 类型
    string 使用 '' or "";
    string 使用 utf-8;  使用中文时，占用3个字节
    string 截断的时候会从前面开始截断
    bytes2 类型不可以直接转string
    需要 bytes2 -> bytes -> string

  ## array 数组
    保存相同类型的数据，连续的区域，存储相同的类型
    uint[5] arr; // 建立一个5 uint 类型的固定数组
    uint[] arr; // 建立 可变长度数组，length初始为0
    array 有length属性
    固定array 的长度不能 通过修改属性 length 修改，可变可以，截断后面的
    二维数组 uint[2][3] arr; //建立二维数组

  ## memory
    函数中使用 new时，需要声明加上 memory。

  ## address 以太坊 中拥有 address的概念
    address account; // 创建地址，默认为0么uint160 等价

  ## payable
    payable 关键字声明，合约地址可以充值;
    任何转账操作都需要 payable 关键字

  ## this
    this 表示合约地址，balance是address的属性

  ## transfer
    account.transfer(msg.value) // 表示 当前账户转账到 account 输入的金额。
    msg.value 表示 输入框填入的值
    this.transfer 需要加上一个回调函数 function () payable {}

  ## 