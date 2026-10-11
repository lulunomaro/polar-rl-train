"""Read actual state and receipts only; reusable without replaying any stage."""
from wave_direction_io import *
def main():
 n,w=io.connect_both()
 try:
  result=run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_direction_once as own
rows={};indices=[]
for p in sorted(own.R.glob('*')):
 if not p.is_file():continue
 raw=p.read_bytes();indices.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
 if p.name in ('E1_STATE.json','E1_ATTENTION.json','E1_DISPATCH_STARTED.json','E1_GUARDIAN_STARTED.json','E1_ACTIVE_HEALTH.json','E1_CURRENT_SAVE.json','E1_REVIEW_READY.json') or p.name.endswith(('_PASSED.json','_SAVED_EXIT.json','_PID_RECEIPT.json','ASYNC_PUBLISHED.json','DIRECTION_FULL_TRACE_REVIEW.json')):
  if len(raw)<500000:rows[p.name]=json.loads(raw)
st=rows.get('E1_STATE.json',{});owner=st.get('owner');child=st.get('child');b=own.s.q.base.budget_state();logs={}
for p in sorted(D.glob('*.log')):
 raw=p.read_bytes();logs[p.name]=dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),tail=raw[-2000:].decode('utf8','replace'))
print(json.dumps(dict(epoch=time.time(),root=str(D),source_count=len(own.read(own.R/'SOURCE_FREEZE.json')['sha256']),reports=rows,report_indices=indices,actual_owner=own.identity(owner['pid']) if owner else None,actual_child=own.identity(child['pid']) if child else None,budget=dict(authorized=b['authorized_training_seconds'],active=b['active_segment'],remaining=b['remaining_training_seconds']),logs=logs,no_controller_GPU_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  path=save('DIRECTION_ACTUAL_'+str(time.time_ns())+'.json',result)
  print(json.dumps(dict(path=str(path),phase=result['reports'].get('E1_STATE.json',{}).get('phase'),actual_child=result['actual_child'],attention=result['reports'].get('E1_ATTENTION.json'),PASSED=[x for x in result['reports'] if x.endswith('_PASSED.json')],budget=result['budget'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
