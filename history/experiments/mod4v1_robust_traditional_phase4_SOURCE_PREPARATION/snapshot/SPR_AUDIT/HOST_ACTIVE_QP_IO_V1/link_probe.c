/* Minimal host linker diagnosis, not solver math. */
#include <stdio.h>
#include <stdlib.h>
#include <fenv.h>
int main(int argc,char **argv){
#ifdef PROBE_FENV
 printf("%d %d\n",fesetround(FE_TONEAREST),fegetround());
#endif
#ifdef PROBE_STRTOF
 if(argc>1){printf("%.9g\n",(double)strtof(argv[1],NULL));}
#endif
 (void)argc;(void)argv;return 0;
}
