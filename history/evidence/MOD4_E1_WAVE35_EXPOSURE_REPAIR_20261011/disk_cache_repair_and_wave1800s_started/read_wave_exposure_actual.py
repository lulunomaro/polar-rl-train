"""Read only current actual root/receipt/own startup/health, not old366 state."""
from wave_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import json,time,sys,hashlib
D=Path(ROOT_TOKEN);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'))
import supervise_wave35_exposure_005_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
st=j(D/'reports/E1_STATE.json') if (D/'reports/E1_STATE.json').exists() else None
dispatch=j(D/'reports/WAVE_PARENT_DISPATCH_ACTUAL_RECEIPT.json');loc=dispatch['controller'];parent=own.identity(loc['pid']);child=own.identity(st['child']['pid']) if st and st.get('child') else None
roots=list((D/'learning_logs').glob('*')) if (D/'learning_logs').exists() else [];runs=[]
for run in roots:
 row=dict(path=str(run),own_receipts={})
 for name in ('run_manifest.json','latest_complete.json','CLOCK_TRAINING_HEALTH.json','SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'):
  p=run/name
  if p.exists():row['own_receipts'][name]=dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),value=j(p))
 runs.append(row)
v=dict(epoch=time.time(),root=str(D),source_count=368,actual_state=st,actual_parent=parent,actual_child=child,own_runs=runs,
 attention=j(D/'reports/E1_ATTENTION.json') if (D/'reports/E1_ATTENTION.json').exists() else None,
 canonical=own.m.s.q.base.budget_state(),final_PASSED=j(D/'reports/e1_WAVE35_exposure_005_observation_PASSED.json') if (D/'reports/e1_WAVE35_exposure_005_observation_PASSED.json').exists() else None,
 old_states_not_used=True,no_GPU_mutation_or_budget_accounting=True)
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=save('WAVE_EXPOSURE_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),state=v['actual_state'],parent=v['actual_parent'],child=v['actual_child'],attention=v['attention'],own_files=[list(x['own_receipts']) for x in v['own_runs']],final_PASSED=bool(v['final_PASSED']))))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
