#include <stdio.h>
#include <string.h>

/* compare two files until one line diff to others' */
/* argv[0] : prog_name argv[1] : file1 argv[2] : file2 */

int main(int argc, char *argv[])
{
  FILE * fp1, * fp2;
  //  int n=0, max_line=100;
  /* char fn1, fn2; */
  /* fn1, fn2 = argv[1], argv[2]; */
  fp1 = fopen(*(argv+1), "r");
  fp2 = fopen(*(argv+2), "r");
  
  //  FILE *fopen(char *name, char *mode);
  int max_line = 100;
  char l1[max_line], l2[max_line];
  /* l1 = "1"; */
  /* l2 = "1"; */
  int n = 0;
  while (1)
    {
      fgets(l1, max_line, fp1);
      fgets(l2, max_line, fp2);
      if (strcmp(l1, l2) != 0)
  	break;
      n++;
    }

  fclose(fp1);
  fclose(fp2);
  printf("%s\n%s", l1, l2);
  return 0;
}
