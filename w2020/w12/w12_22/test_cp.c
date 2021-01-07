#include <stdio.h>


void str_copy(char *p, char *t)
{
  /* while (*p++ = *t++) */
  /*   printf("%s", p); */
  char *i = "haaaa";
  p = i;
  printf("%s\n", p);
}

int main()
{
  char *mes = "hello";
  char *_t;
  str_copy(_t, mes);
  printf("%s\n", _t);
}
