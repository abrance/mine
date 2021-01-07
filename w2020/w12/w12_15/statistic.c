#include <stdio.h>

main ()
{
  /* char _s = "9"; */
  /* char __s = _s; */
  int cnt_squar;
  int c;
  cnt_squar = 0;
  while ((c = getchar()) != EOF)
    {
      if (c == '(')
	{
	  cnt_squar += 1;
	}
      else if (c == ')')
	cnt_squar -= 1;
    }
  printf("%d \n", c);
}
