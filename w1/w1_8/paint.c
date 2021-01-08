#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>


struct SCALE{
  // 棋盘大小
  unsigned int x;    // x: 长
  unsigned int y;    // y: 宽
};

//
//


int check_axios(char *, char *);
int read_field(int *arr[]);

int main(int argc, char **argv)
{
  struct SCALE scale;               // 结构体变量声明
  if (argc == 1)
    {
      scale.x = 5, scale.y = 5;
    }
  else if (argc == 3)
    {
      char *x = argv[1], *y = argv[2];
      char* _x = malloc(2*sizeof(char));
      char* _y = malloc(2*sizeof(char));

      check_axios(_x, x);
      check_axios(_y, y);
      scale.x = atoi(_x), scale.y = atoi(_y);
      printf("%d\n", scale.x);
      printf("%d\n", scale.y);
    }
  else
    {
      printf("param error: eg: xxx 5 1\n");
      exit(0);
    }

  // 到这里已经有了棋盘大小,初始化二维数组表示棋盘
  int field[1][2] = {0};
  //  memset(field, 0, 2);
  
  read_field(field);
  // 显示棋盘
}


int check_axios(char *_x, char *x)
{
  // 完成截取两位字符，并赋值_x指针
  // printf("...");
  char axio[2] = "";
  int cnt = 0;
  while (*x)
    {
      // printf("%c", *x);
      if (isdigit(*x) == 0)
	{
	  printf("error input %c\n", *x);
	  break;	      
	}
      else
	{
	  if (cnt < 2)
	    {
	      axio[cnt] = *x;
	      cnt++;
	    }
	  else
	    {
	      printf("truncate\n");
	    }
	}
      x++;
    }
  printf("axio %s\n", axio);
  strcpy(_x, axio);
  return 0;
}
