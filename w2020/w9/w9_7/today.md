# configparse 使用
    类属性中有一个 DEFAULTSECT 默认为 DEFAULT， 当命名了这个section，将会把这个自动加入到其它section后面
    
    configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation()) 为使用扩展插入类，允许以这种 ${user:name} 形式引用变量 