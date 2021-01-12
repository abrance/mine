#include <stdio.h>
#include <math.h>


/*
  先定义一个整型二维数组，作为原始数据存放
*/

// typedef sudoku
int data[9][9];
typedef unsigned int SUDOKU[9][9];     // 二维数组typedef
typedef unsigned int LITTLE_SUDOKU[3][3];
struct Axis
{
  int x;
  int y;
} AXIS;

SUDOKU a = {{0}};    // 二维数组赋固定值
/* 打印数组 */
int print_sudoku(SUDOKU);
/* 倒转数组 */
int invert_arr(SUDOKU, SUDOKU);
/* 数组赋值 */
int giving_sudoku(SUDOKU);
/* 获取3*3数组 */
int get_little_sudoku(LITTLE_SUDOKU,struct Axis, SUDOKU);
/* 获取某一坐标下候选值的集合 */
int get_candidate(struct Axis, SUDOKU);
int get_fixed_set(unsigned int[], unsigned int[]);

int main()
{
  SUDOKU vert_a;
  LITTLE_SUDOKU li;
  struct Axis axis = {2, 3};

  giving_sudoku(a);
  print_sudoku(a);
  invert_arr(vert_a, a);
  print_sudoku(vert_a);
  get_little_sudoku(li, axis, a);
}

int print_sudoku(SUDOKU sudoku)
{
  int j, i, cnt;
  cnt = 0;
  for (j=0;j<9;j++)
    {
      for (i=0;i<9;i++)
	{
	  //	  if (*(sudoku+i)[j] == 0)          // 二维数组取值，a保存的是第二层数组的地址 **a 才能取到值
	  //	  if (sudoku[i][j] == 0)
	  if (*(*(sudoku+i)+j))
	    {
	      cnt ++;
	    }
	  printf("%d", *(*(sudoku+j)+i));
	}
    }
  printf("%d\n", cnt);
  return 0;
}

int invert_arr(SUDOKU new, SUDOKU sudoku)
{
  int i, j, cnt;
  cnt = 0;
  for (i=0;i<9;i++)
    {
      for (j=0;j<9;j++)
	{
	  new[j][i] = sudoku[i][j];
	  cnt++;
	}
    }
  return 0;
}

int giving_sudoku(SUDOKU sudoku)
{
  int i, j, cnt;
  cnt = 0;
  for (i=0;i<9;i++)
    {
      for (j=0;j<9;j++)
	{
          sudoku[i][j] = j+1;
	  cnt++;
	}
    }
  return 0;
}

/* axis 这里是 (1, 2) 表示第一行第二列的宫，第一行一共三个宫 */
int get_little_sudoku(LITTLE_SUDOKU li, struct Axis axis, SUDOKU sudoku)
{
  int i, j, cnt, x, y, a, b;
  x = axis.x;
  y = axis.y;
  cnt = 0;
  for (i=(x-1)*3, a=0;i<x*3;i++, a++)
    {
      for (j=(y-1)*3, b=0;j<y*3;j++, b++)
	{
          li[a][b] = sudoku[i][j];
	  cnt++;
	  printf("%d\n", li[a][b]);
	}
    }
  return 0;
}

/* axis 这里是9*9里面的坐标，(1, 2)是指第一行第二列的值（而非宫） */
int get_candidate(struct Axis axis, SUDOKU sudoku)
{
  int j, k, i, m;
  int x = axis.x;
  int y = axis.y;
  j = ceil(x/3);
  k = ceil(y/3);
  struct Axis _axis = {j, k};

  if (sudoku[x-1][y-1] != 0)
    return -1;
  else
    {
      unsigned int filled_space_x[] = {};
      unsigned int filled_space_y[] = {}, filled_space_x_y[] = {};
      unsigned int fixed_x[] = {}, fixed_y[] = {}, fixed_x_y[] = {};
      unsigned int *p;
      SUDOKU invert_sudoku;
      LITTLE_SUDOKU li;

      /* 分别获取三个集合 */
      for (i=0;i<9;i++)
	{
	  p = filled_space_x;
	  if ((sudoku[x-1][i] != 0))
	    {
	      /* TODO 不定长数组如何初始化 */
	      *++p = sudoku[x-1][i];
	    }
	}

      invert_arr(invert_sudoku, sudoku);
      for (i=0;i<9;i++)
	{
	  p = filled_space_y;
	  if ((invert_sudoku[y-1][i] != 0))
	    {
	      /* TODO 不定长数组如何初始化 */
	      *++p = invert_sudoku[y-1][i];
	    }	  
	}

      get_little_sudoku(li, _axis, sudoku);
      for (i=0;i<3;i++)
	{
	  for (m=0;m<3;m++)
	    {
	      p = filled_space_x_y;
	      if (li[i][m]!=0)
		{
		  *++p = li[i][m];
		}
	    }
	}

      get_fixed_set(fixed_x, filled_space_x);
      get_fixed_set(fixed_y, filled_space_y);
      get_fixed_set(fixed_x_y, filled_space_x_y);
    }
  return 0;
}

int get_fixed_set(unsigned int* fixed, unsigned int* unfilled)
{
  unsigned int full[9] = {1, 2, 3, 4, 5, 6, 7, 8, 9};
  unsigned int i, *p;
  p = full;
  while (*unfilled)
    {
      for (i=0;i<9;i++)
	{
	  if (full[i] == *unfilled)
	    full[i] = 0;
	}
    }
  while (*p)
    {
      if (*p!=0)
	{
	  *fixed = *p;
	  ++p;
	  ++fixed;
	}
    }
  return 0;
}
