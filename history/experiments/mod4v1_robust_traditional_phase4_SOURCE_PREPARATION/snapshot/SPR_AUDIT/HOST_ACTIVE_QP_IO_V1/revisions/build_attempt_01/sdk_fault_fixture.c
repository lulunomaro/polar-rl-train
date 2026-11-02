/* Dedicated SDK lifecycle fixture, NOT the production solver. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <string.h>
#include "aq_io_build.h"
int main(void){char mode[32];DWORD n=GetEnvironmentVariableA("AQ_IO_TEST_MODE",mode,sizeof(mode));if(!n||n>=sizeof(mode)){return 2;}printf("ABQPIO 1 B 0 8 16 32 64 24 QPC RN_NO_FTZ_DAZ %s %s\n",AQ_CORE_SHA,AQ_HEADER_SHA);fflush(stdout);if(!strcmp(mode,"eof")){return 2;}if(!strcmp(mode,"stall")){for(;;){Sleep(1000);}}return 2;}
