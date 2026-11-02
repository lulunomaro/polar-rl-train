"""Derive NEW source from the immutable C1 text with bounded exact replacements.
Never edits C1. Runtime solver itself is ordinary reviewed C, no generation on use.
"""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'portable_mpc_qp_v1/boxqp.c'
EXPECTED='53ad5bf9f447ea7a7a500a809f0fcdcca8973ffeb8afc4a16a2574ed05c2cdff'
helper=r'''
static int free_candidate(bqp_workspace *w,uint32_t n,float tolerance,bqp_fast_info *info) {
 uint32_t i,j;float value,term,cost=0.0f,residual=0.0f;
 info->free_tried=1u;
 /* L*y=-f using gradient scratch, then L^T*z=y. No input/warm is destroyed. */
 for(i=0;i<n;i++){
  value=-w->f[i];
  for(j=0;j<i;j++){
   term=w->L[i*BQP_MAX_N+j]*w->gradient[j];value-=term;
   if(!isfinite(term)||!isfinite(value)){return 0;}
  }
  w->gradient[i]=value/w->L[i*BQP_MAX_N+i];
  if(!isfinite(w->gradient[i])){return 0;}
 }
 for(i=n;i>0u;i--){
  uint32_t row=i-1u;value=w->gradient[row];
  for(j=row+1u;j<n;j++){
   term=w->L[j*BQP_MAX_N+row]*w->z[j];value-=term;
   if(!isfinite(term)||!isfinite(value)){return 0;}
  }
  w->z[row]=value/w->L[row*BQP_MAX_N+row];
  if(!isfinite(w->z[row])){return 0;}
 }
 info->free_solve_finite=1u;
 for(i=0;i<n;i++){if(w->z[i]<w->lo[i]||w->z[i]>w->hi[i]){return 0;}}
 info->free_feasible=1u;
 if(metrics(w,n,&cost,&residual)!=BQP_RUNNING){return 0;}
 info->free_metrics_valid=1u;info->free_projected_kkt_inf=residual;
 if(residual>tolerance){return 0;}
 info->free_kkt_met=1u;info->free_selected=1u;return 1;
}
'''
branch=r''' w->clock_initialized=0u;w->last_clock=0;
 if(enable_free){
  status=clock_poll(&o,w,&now,&expired);
  if(status==BQP_CLOCK_ERROR){return invalid(out,status);}
  if(!expired){
   if(!free_candidate(w,n,o.tolerance,fast_info)){
    /* Infeasible, inaccurate or overflowing optional free solve: original warm
     * CCD remains authoritative; never clip a free solution into fake success. */
    for(i=0;i<n;i++){w->z[i]=project(w->warm[i],w->lo[i],w->hi[i]);}
   }
   status=clock_poll(&o,w,&now,&expired);
   if(status==BQP_CLOCK_ERROR){return invalid(out,status);}
  }
 }
 for(;;){'''
wrappers=r'''
/* Existing ABI remains explicitly CCD-only, including its original clock path. */
bqp_status bqp_solve(const bqp_problem *p,const bqp_options *o,bqp_workspace *w,bqp_result *out) {
 return solve_impl(p,o,w,out,0u,NULL);
}
bqp_status bqp_solve_fast(const bqp_problem *p,const bqp_options *o,bqp_workspace *w,bqp_result *out,uint8_t enabled,bqp_fast_info *info) {
 bqp_fast_info local;uint32_t required=0u;bqp_status status;
 memset(&local,0,sizeof(local));
 if(p&&p->n>0u&&p->n<=BQP_MAX_N&&p->h_stride>=p->n&&p->h_stride<=BQP_MAX_N){required=(p->n-1u)*p->h_stride+p->n;}
 if(info){
  if(overlap(info,sizeof(*info),w,w?sizeof(*w):0u)||overlap(info,sizeof(*info),out,out?sizeof(*out):0u)
   ||overlap(info,sizeof(*info),p,p?sizeof(*p):0u)||overlap(info,sizeof(*info),o,o?sizeof(*o):0u)
   ||(p&&required&&(overlap(info,sizeof(*info),p->H,required*sizeof(float))
    ||overlap(info,sizeof(*info),p->f,p->n*sizeof(float))||overlap(info,sizeof(*info),p->lo,p->n*sizeof(float))
    ||overlap(info,sizeof(*info),p->hi,p->n*sizeof(float))||overlap(info,sizeof(*info),p->warm_start,p->warm_start?p->n*sizeof(float):0u)))){
   return invalid(out,BQP_BAD_ALIAS);
  }
 }
 if(enabled>1u){if(info){*info=local;}return invalid(out,BQP_BAD_OPTIONS);}
 local.enabled=enabled;status=solve_impl(p,o,w,out,enabled,&local);
 if(info){*info=local;}
 return status;
}
'''

def replace_once(s,old,new):
 assert s.count(old)==1,old
 return s.replace(old,new,1)

def main():
 data=BASE.read_bytes();assert hashlib.sha256(data).hexdigest()==EXPECTED
 out=HERE/'boxqp_fast.c';assert not out.exists(),'Preserve already generated source rather than overwrite it'
 source=data.decode('utf-8')
 source=replace_once(source,'#include "boxqp.h"','#include "boxqp_fast.h"')
 marker='static bqp_status sweep(bqp_workspace *w,uint32_t n) {'
 source=replace_once(source,marker,helper+'\n'+marker)
 old='bqp_status bqp_solve(const bqp_problem *problem,const bqp_options *options,bqp_workspace *w,bqp_result *out) {'
 new='static bqp_status solve_impl(const bqp_problem *problem,const bqp_options *options,bqp_workspace *w,bqp_result *out,uint8_t enable_free,bqp_fast_info *fast_info) {'
 source=replace_once(source,old,new)
 source=replace_once(source,' w->clock_initialized=0u;w->last_clock=0;\n for(;;){',branch)
 source+=wrappers
 out.write_text(source,encoding='utf-8')
 provenance={'base':str(BASE),'base_sha256':EXPECTED,'new':str(out),'new_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
             'method':'bounded exact replacements + new helper/wrappers; original core never edited','base_CCD_path_retained':True}
 (HERE/'DERIVATION.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8');print(json.dumps(provenance))
if __name__=='__main__':main()
