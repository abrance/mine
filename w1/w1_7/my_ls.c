#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <dirent.h>
#include <stdio.h>

/* 定制自己的ls */
/* 函数 opendir(char * dirname) */

// opendir
void _opendir(char *);

int main(int argc, char **argv)
{
  char* dirname;
  if (argc == 1)
    {
      dirname = ".";
    }
  else if (argc == 2)
    {
      dirname = argv[1];
      // 遍历 dirname
      _opendir(dirname);
    }
  else
    {
      ;
    }
  
}


void _opendir(char* dirname)
{
  // check dirname;
  struct stat stbuf;
  if (stat(dirname, &stbuf) == -1)
    return;
  if ((stbuf.st_mode & S_IFMT) == S_IFDIR)
    // 遍历
    {
      struct dirent *dp;
      DIR *dfd;
      dfd = opendir(dirname);
      while ((dp = readdir(dfd)) != NULL)
	{
	  if (strcmp(dp->d_name, ".") == 0 || strcmp(dp->d_name, "..") == 0)
	    continue;
	  else
	    {
	      printf("\n%s/%s\n", dirname, dp->d_name);
	    }
	}
    }
    
}
