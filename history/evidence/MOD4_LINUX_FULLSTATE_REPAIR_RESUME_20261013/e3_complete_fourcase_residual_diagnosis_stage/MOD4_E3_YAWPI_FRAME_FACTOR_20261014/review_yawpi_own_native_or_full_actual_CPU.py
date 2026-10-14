"""Own new-factor native120/full1500 admission, CPU-only and failclosed."""
from pathlib import Path
import argparse,json,time,traceback
import yawpi_actual_reader_components as m
def main():
 p=argparse.ArgumentParser();p.add_argument('--collection',required=True);p.add_argument('--steps',type=int,choices=(120,1500),required=True);p.add_argument('--native-admission');p.add_argument('--out',required=True)
 p.add_argument('--baseline-review',default=str(m.W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json'));a=p.parse_args();out=Path(a.out);assert not out.exists(),'Own review output is immutable'
 try:
  report,_=m.review(Path(a.collection),Path(a.baseline_review),a.steps,Path(a.native_admission) if a.native_admission else None)
  report['epoch']=time.time();report['reader_source_SHA']=m.sha(__file__);report['reader_components_SHA']=m.sha(Path(m.__file__));report['Git_pending_root_archive']=True
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(out),passed_actual=True,controls=a.steps,callbacks=a.steps*4,WORLD_forward=report['WORLD_forward_complete'],WORLD_reverse=report['WORLD_reverse_complete'],ordinary=report['ordinary'],qualified50=False)))
 except BaseException:
  err=out.with_name(out.stem+'_ORIGINAL_READER_ERROR_'+str(time.time_ns())+'.json');err.parent.mkdir(parents=True,exist_ok=True);err.write_text(json.dumps(dict(epoch=time.time(),collection=a.collection,controls=a.steps,error=traceback.format_exc(),CPU_only=True,no_new_GPU_PPO_budget=True,original_evidence_not_changed=True,reader_source_SHA=m.sha(__file__),reader_components_SHA=m.sha(Path(m.__file__)),Git_pending_root_archive=True),indent=2),encoding='utf8');raise
if __name__=='__main__':main()
