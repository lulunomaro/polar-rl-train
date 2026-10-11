from second_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,hashlib
D=Path(ROOT_TOKEN);R=D/'reports';sys.path[:0]=[str(D),str(D/'isaac/mod4')]
import supervise_wave35_second_bounded_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
st=j(R/'E1_STATE.json') if (R/'E1_STATE.json').exists() else None
receipt=j(R/'SECOND_PARENT_DISPATCH_ACTUAL_RECEIPT.json') if (R/'SECOND_PARENT_DISPATCH_ACTUAL_RECEIPT.json').exists() else None
parent=own.identity(receipt['controller']['pid']) if receipt else None
child=own.identity(st['child']['pid']) if st and st.get('child') else None
runs=list((D/'learning_logs').glob('*')) if (D/'learning_logs').exists() else []
run=runs[0] if len(runs)==1 else None;files={}
if run:
 for name in ('run_manifest.json','latest_complete.json','CLOCK_TRAINING_HEALTH.json','RETENTION_COMMAND_ACTUAL.json','SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'):
  p=run/name
  if p.exists():files[name]=dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),value=j(p))
attention=j(R/'E1_ATTENTION.json') if (R/'E1_ATTENTION.json').exists() else None
print(json.dumps(dict(epoch=time.time(),root=str(D),source_count=369,actual_parent=parent,actual_child=child,actual_state=st,dispatch_receipt=receipt,own_run=str(run) if run else None,own_files=files,attention=attention,controller_log_tail=(D/'controller.log').read_text(errors='replace')[-4000:] if attention else None,canonical_active_segment=own.m.s.q.base.budget_state()['active_segment'],supervisor_active=own.read(own.m.s.q.ctl.STATE_PATH).get('active_training'),no_mutation=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=save('SECOND_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),parent=v['actual_parent'],child=v['actual_child'],phase=v['actual_state']['phase'] if v['actual_state'] else None,attention=v['attention'],files=list(v['own_files']),canonical_pid=(v['canonical_active_segment'] or {}).get('pid'))))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
