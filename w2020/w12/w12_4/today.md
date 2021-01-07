# commonlisp
  ## blocks 区块
  progn 依序求值，返回最后一个（说明它有副作用）

  # let 初始值为nil， let* 可以创建 后一变量依赖前一变量
  (let ((x 1) (y (+ x 1)))
       (+ x y))
  # destructuring-bind 宏可以代替let 进行变量赋值

  # 条件
  ## if
  ## when unless 语义相反
  ## cond 简洁

  # 迭代
  ## do do* dolist dotimes

  # 多值
  ## lisp返回多值，如果只有一个值接收，其它值会被舍弃。如果接收的值多于返回的值，多于的值为nil
  ## 接收多个数值，使用 multiple-value-bind
  ## 可以将返回值直接传给另一函数 (multiple-value-call #'+ (values 1 2 3))  # values 返回参数本身

  # catch throw

  # 文档
  ## (defun foo (x)
      "return self"
      x)
      作为函数文档保存下来， (documentation 'foo 'function) 可以获取
      
  # rest &rest 后都为剩余参数 &optional 后为选择性参数 &key 后为关键字参数
  &optional 之后的参数都是 选择性的
  (defun philsopg (thing &optional property)
        (list thing 'is property))
  (philsopg 'death)
  > DEATH is NIL

  (defun keylist (a &key x y z)
        (list a x y z))

  (keylist 1 :y 2)
  > (1 NIL 2 NIL)
  (keylist 1 :y 2 :z 3)
  > (1 NIL 2 3)


# tip
  # FP functional Programming
  # 闭包是 传入参数后，返回函数或将函数保存。
  ## 闭包结合了函数与环境；无论何时，当一个函数引用到周围词法环境的某个东西是，闭包就被隐式的创建出来了。
  