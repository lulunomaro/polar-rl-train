/* Resident PE32 numerical worker; one sealed ab3_solve per S frame. */
#define __USE_MINGW_ANSI_STDIO 1
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <float.h>
#include <math.h>
#include <fenv.h>
#include <locale.h>
#include <xmmintrin.h>
#include "active_box_qp.h"
#include "aq_clock.h"
#include "aq_io_build.h"
#if FLT_MANT_DIG!=24 || FLT_RADIX!=2 || !defined(__SSE2__)
#error AQ_requires_binary32_SSE2_host
#endif
typedef char aq_host32[(sizeof(void*)==4u&&sizeof(uint64_t)==8u&&sizeof(float)==4u)?1:-1];
typedef struct {uint32_t n,max_pivots,warm_present;uint64_t budget_us;float tolerance,H[256],f[16],lo[16],hi[16],warm[16];} aq_request;
typedef struct {unsigned valid;float estimate,upper;} aq_diagnostic;
static int fp_environment(void){unsigned csr;if(fesetround(FE_TONEAREST)!=0||fegetround()!=FE_TONEAREST){return 0;}csr=_mm_getcsr();csr&=~(0x6000u|0x8000u|0x0040u);_mm_setcsr(csr);return (_mm_getcsr()&(0x6000u|0x8000u|0x0040u))==0u;}
static int read_frame(char *line,size_t capacity){size_t used=0;int c;for(;;){c=fgetc(stdin);if(c==EOF){line[used]='\0';return ferror(stdin)||used?-2:0;}if(c=='\n'){line[used]='\0';return 1;}if(c==0||c>127||(c<32&&c!='\r'&&c!='\t')){line[used]='\0';return -3;}if(used+1>=capacity){line[used]='\0';return -1;}line[used++]=(char)c;}}
static int split(char *line,char **tokens,uint32_t *count){char *p=line;*count=0;while(*p){while(*p==' '||*p=='\t'||*p=='\r'){p++;}if(!*p){break;}if(*count>=AQ_MAX_TOKENS){return 0;}tokens[(*count)++]=p;while(*p&&*p!=' '&&*p!='\t'&&*p!='\r'){p++;}if(*p){*p++='\0';}}return 1;}
static int parse_u64(const char *s,uint64_t *out){uint64_t value=0,digit;size_t i,length=strlen(s);if(!length||length>20u||(length>1u&&s[0]=='0')){return 0;}for(i=0;i<length;i++){if(s[i]<'0'||s[i]>'9'){return 0;}digit=(uint64_t)(s[i]-'0');if(value>(UINT64_MAX-digit)/10u){return 0;}value=value*10u+digit;}*out=value;return 1;}
static int parse_u32(const char *s,uint32_t *out){uint64_t value;if(!parse_u64(s,&value)||value>UINT32_MAX){return 0;}*out=(uint32_t)value;return 1;}
static int parse_float(const char *s,float *out){const char *p=s;char *end;unsigned digits=0;float value;if(strlen(s)>64u){return 0;}if(*p=='+'||*p=='-'){p++;}while(*p>='0'&&*p<='9'){digits++;p++;}if(*p=='.'){p++;while(*p>='0'&&*p<='9'){digits++;p++;}}if(!digits){return 0;}if(*p=='e'||*p=='E'){unsigned exponent_digits=0;p++;if(*p=='+'||*p=='-'){p++;}while(*p>='0'&&*p<='9'){exponent_digits++;p++;}if(!exponent_digits){return 0;}}if(*p){return 0;}value=strtof(s,&end);if(*end||!isfinite(value)){return 0;}*out=value;return 1;}
static uint32_t parse_request(char **tokens,uint32_t count,aq_request *q){uint32_t h_count,v_count,expected,i,at=7u;memset(q,0,sizeof(*q));if(count<7u){return 1002u;}if(!parse_u32(tokens[0],&q->n)||!parse_u32(tokens[1],&q->max_pivots)||!parse_u64(tokens[3],&q->budget_us)||!parse_u32(tokens[4],&q->warm_present)||!parse_u32(tokens[5],&h_count)||!parse_u32(tokens[6],&v_count)){return 1003u;}if(!q->n||q->n>AB3_MAX_N||q->warm_present>1u||h_count!=q->n*q->n||v_count!=q->n){return 1004u;}expected=7u+h_count+3u*q->n+(q->warm_present?q->n:0u);if(count!=expected){return 1002u;}if(!parse_float(tokens[2],&q->tolerance)){return 1006u;}if(q->tolerance<=0){return 1007u;}for(i=0;i<h_count;i++){if(!parse_float(tokens[at++],&q->H[i])){return 1006u;}}for(i=0;i<q->n;i++){if(!parse_float(tokens[at++],&q->f[i])){return 1006u;}}for(i=0;i<q->n;i++){if(!parse_float(tokens[at++],&q->lo[i])){return 1006u;}}for(i=0;i<q->n;i++){if(!parse_float(tokens[at++],&q->hi[i])){return 1006u;}}if(q->warm_present){for(i=0;i<q->n;i++){if(!parse_float(tokens[at++],&q->warm[i])){return 1006u;}}}return 0u;}
static int fatal_status(uint32_t code){return code>=1000u||code==AB3_CLOCK_ERROR||code==AB3_BAD_ARGUMENT||code==AB3_BAD_SHAPE||code==AB3_BAD_OPTIONS||code==AB3_BAD_ALIAS||code==AB3_NONFINITE||code==AB3_ASYMMETRIC||code==AB3_NOT_SPD||code==AB3_NUMERIC||code==AB3_BAD_BOX;}
static int pairwise(float *values,float *out){unsigned stride,i;for(stride=1;stride<32;stride*=2){for(i=0;i<32;i+=2*stride){values[i]+=values[i+stride];if(!isfinite(values[i])){return 0;}}}*out=values[0];return 1;}
static aq_diagnostic private_diagnostic(const aq_request *q,const ab3_workspace *w,const ab3_result *r){
 aq_diagnostic d;uint32_t i,j;float sum[32],magnitude[32],product,g,S,b,residual,upper;memset(&d,0,sizeof(d));
 if(r->valid){d.valid=1;d.estimate=r->kkt_estimate;d.upper=r->kkt_upper;return d;}
 if(r->status!=AB3_MAX_PIVOTS&&r->status!=AB3_DEADLINE&&r->status!=AB3_NO_PROGRESS&&r->status!=AB3_CYCLE&&r->status!=AB3_ROUNDOFF_LIMIT){return d;}
 /* Read-only post-return private-point metric, OUTSIDE solver clock budget.
  * No second solve, no accepted iterate exposure or acceptance modification. */
 for(i=0;i<q->n;i++){
  if(!isfinite(w->z[i])||q->lo[i]>q->hi[i]||w->z[i]<q->lo[i]||w->z[i]>q->hi[i]){memset(&d,0,sizeof(d));return d;}memset(sum,0,sizeof(sum));memset(magnitude,0,sizeof(magnitude));
  for(j=0;j<q->n;j++){product=q->H[i*q->n+j]*w->z[j];if(!isfinite(product)){memset(&d,0,sizeof(d));return d;}sum[j]=product;magnitude[j]=fabsf(product);}sum[q->n]=q->f[i];magnitude[q->n]=fabsf(q->f[i]);
  if(!pairwise(sum,&g)||!pairwise(magnitude,&S)){memset(&d,0,sizeof(d));return d;}b=(4*FLT_EPSILON)*S+32*FLT_MIN;if(!isfinite(b)){memset(&d,0,sizeof(d));return d;}
  if(q->lo[i]==q->hi[i]){residual=upper=0;}else if(w->z[i]==q->lo[i]){residual=-g;upper=-g+b;}else if(w->z[i]==q->hi[i]){residual=g;upper=g+b;}else{residual=fabsf(g);upper=residual+b;}
  if(!isfinite(upper)){memset(&d,0,sizeof(d));return d;}if(residual>d.estimate){d.estimate=residual;}if(upper>d.upper){d.upper=upper;}
 }
 d.valid=1;return d;
}
static int emit_reply(char op,uint64_t sequence,uint32_t status,unsigned fatal,const aq_request *request,const ab3_result *result,unsigned clock_failed,const aq_diagnostic *diagnostic){
 ab3_result zero;aq_diagnostic dzero;const ab3_result *r=result;const aq_diagnostic *d=diagnostic;unsigned i;memset(&zero,0,sizeof(zero));memset(&dzero,0,sizeof(dzero));if(!r){r=&zero;}if(!d){d=&dzero;}
 printf("ABQPIO 1 %c %" PRIu64 " %u %" PRIu32 " %u %u %" PRIu32 " %" PRIu32 " %" PRIu32 " %u %u",op,sequence,AQ_REPLY_FIELDS,status,(unsigned)r->valid,fatal,request?request->n:0u,r->n,request?request->warm_present:0u,clock_failed,d->valid);
 printf(" %.9g %.9g %.9g %.9g %.9g %.9g",(double)r->cost,(double)r->kkt_estimate,(double)r->kkt_upper,(double)r->maximum_gradient_roundoff_bound,(double)d->estimate,(double)d->upper);
 printf(" %" PRIu32 " %" PRIu64 " %" PRIu64 " %" PRIu64 " %" PRIu64 " %" PRIu64 " %" PRIu64 " %u %u %" PRIu64 " %" PRIu64 " %" PRIu64,r->stats.pivots,r->stats.factorizations,r->stats.factor_cells,r->stats.releases,r->stats.bound_hits,r->stats.gradient_evaluations,r->stats.clock_polls,(unsigned)r->stats.last_phase,(unsigned)r->stats.abort_phase,r->stats.start_us,r->stats.last_us,r->stats.elapsed_us);
 for(i=0;i<16;i++){printf(" %.9g",(double)r->z[i]);}printf("\n");return fflush(stdout)==0&&!ferror(stdout);
}
static int protocol_fault(uint64_t sequence,uint32_t code){(void)emit_reply('E',sequence,code,1u,NULL,NULL,0u,NULL);return 2;}
int main(void){
 char line[AQ_MAX_FRAME],*tokens[AQ_MAX_TOKENS];uint32_t count,version,declared,status;uint64_t sequence,last_sequence=0;unsigned seen=0;int read_status;aq_request request;aq_clock_context clock;ab3_workspace workspace;ab3_result result;ab3_options options;ab3_problem problem;aq_diagnostic diagnostic;
 if(!setlocale(LC_NUMERIC,"C")||!fp_environment()){return protocol_fault(0,1012u);}if(!aq_clock_open(&clock)){return protocol_fault(0,1011u);}
 printf("ABQPIO 1 B 0 8 16 %u 64 24 %s RN_NO_FTZ_DAZ %s %s\n",(unsigned)(CHAR_BIT*sizeof(void*)),aq_clock_source(),AQ_CORE_SHA,AQ_HEADER_SHA);if(fflush(stdout)!=0){return 3;}
 for(;;){
  read_status=read_frame(line,sizeof(line));if(!read_status){return 0;}if(read_status<0){return protocol_fault(0,read_status==-1?1009u:(read_status==-2?1008u:1010u));}
  if(!split(line,tokens,&count)){return protocol_fault(0,1002u);}if(count<5u||strcmp(tokens[0],"ABQPIO")||!parse_u32(tokens[1],&version)||version!=1u||strlen(tokens[2])!=1u){return protocol_fault(0,1001u);}
  if(!parse_u64(tokens[3],&sequence)||!parse_u32(tokens[4],&declared)){return protocol_fault(0,1003u);}if(!sequence||(seen&&(last_sequence==UINT64_MAX||sequence!=last_sequence+1u))){return protocol_fault(sequence,1005u);}if(declared!=count-5u){return protocol_fault(sequence,1002u);}
  if(tokens[2][0]=='Q'){if(declared){return protocol_fault(sequence,1002u);}printf("ABQPIO 1 A %" PRIu64 " 0\n",sequence);return fflush(stdout)==0?0:3;}if(tokens[2][0]!='S'){return protocol_fault(sequence,1013u);}
  status=parse_request(tokens+5,declared,&request);if(status){return protocol_fault(sequence,status);}last_sequence=sequence;seen=1u;
  memset(&workspace,0,sizeof(workspace));memset(&result,0,sizeof(result));memset(&options,0,sizeof(options));aq_clock_begin(&clock,request.budget_us);options.max_pivots=request.max_pivots;options.tolerance=request.tolerance;options.clock=aq_clock_poll;options.clock_context=&clock;options.budget_us=request.budget_us;problem=ab3_dense(request.n,request.H,request.f,request.lo,request.hi,request.warm_present?request.warm:NULL);
  status=(uint32_t)ab3_solve(&problem,&options,&workspace,&result);
  if(clock.failed){ab3_stats saved=result.stats;memset(&result,0,sizeof(result));result.status=AB3_CLOCK_ERROR;result.stats=saved;status=AB3_CLOCK_ERROR;}
  diagnostic=private_diagnostic(&request,&workspace,&result);if(!emit_reply('R',sequence,status,(unsigned)fatal_status(status),&request,&result,clock.failed,&diagnostic)){return 3;}if(fatal_status(status)){return 2;}
 }
}
