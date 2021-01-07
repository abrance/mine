#include <stdio.h>


int power(int x, int y)
{
  // 只支持整型运算，y值不能为负数，不能超出int 范围
  int ret = 1;
  int i;
  for (i = 0; i < y; i++)
    {
      ret = ret * x;
    }
  return ret;
}

int main()
{
  int r = power(2, 3);
  printf("%d \n", r);
}
