"""Read only the actually deployed route-source-reviewed root440."""
from route_GPU_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,hashlib,torch
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_source_reviewed_once as wrapper
own=wrapper.prior;reports={};indices=[]
for p in sorted((D/'reports').glob('*')):
 if not p.is_file():continue
 raw=p.read_bytes();indices.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
 if p.name in ('E1_STATE.json','E1_ATTENTION.json','E1_DISPATCH_STARTED.json','E1_GUARDIAN_STARTED.json','E1_ACTIVE_HEALTH.json','E1_CURRENT_SAVE.json','E1_REVIEW_READY.json') or p.name.endswith(('_PASSED.json','_SAVED_EXIT.json','_PID_RECEIPT.json','ASYNC_PUBLISHED.json')):
  if len(raw)<500000:reports[p.name]=json.loads(raw)
state=reports.get('E1_STATE.json',{});b=own.s.q.base.budget_state();owner=state.get('owner');child=state.get('child');runs=[]
markers=('SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json','E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json','E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json')
for p in (D/'learning_logs').glob('*'):
 if p.is_dir():runs.append(dict(path=str(p),startup_markers={k:json.loads((p/k).read_bytes()) for k in markers if (p/k).exists()},manifest=json.loads((p/'run_manifest.json').read_bytes()) if (p/'run_manifest.json').exists() else None,latest_complete=json.loads((p/'latest_complete.json').read_bytes()) if (p/'latest_complete.json').exists() else None))
logs={p.name:p.read_bytes()[-3500:].decode('utf8','replace') for p in D.glob('*.log')}
print(json.dumps(dict(epoch=time.time(),root=str(D),source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),reports=reports,indices=indices,actual_owner=own.identity(owner['pid']) if owner else None,actual_child=own.identity(child['pid']) if child else None,runs=runs,logs=logs,budget=dict(authorized=b['authorized_training_seconds'],active=b['active_segment'],remaining=b['remaining_training_seconds']),no_GPU_controller_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=save('ROUTE_LIFECYCLE_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(report=str(p),phase=v['reports'].get('E1_STATE.json',{}).get('phase'),attention=v['reports'].get('E1_ATTENTION.json'),owner=v['actual_owner'],child=v['actual_child'],passed=[k for k in v['reports'] if k.endswith('_PASSED.json')],own_formal_runs=len(v['runs']),budget=v['budget'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ROUTE_ACTUAL_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only_no_GPU_replay=True));raise
