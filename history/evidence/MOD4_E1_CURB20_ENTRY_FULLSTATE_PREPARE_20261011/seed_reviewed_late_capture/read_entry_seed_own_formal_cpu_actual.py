from pathlib import Path
import sys,json,time,shlex
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io

def main():
 n,w=io.connect_both()
 try:
  code=r'''from pathlib import Path
import sys,json,time,hashlib,torch
D=Path(ROOT);R=D/'reports';sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
p=R/'e1_CURB20_entry_repair_observation_PASSED.json'
if not p.exists():print(json.dumps(dict(epoch=time.time(),pending=True,formal_own_PASSED_not_yet_generated=True,no_mutation=True)));raise SystemExit(0)
j=lambda p:json.loads(p.read_bytes());v=j(p);ck=Path(v['checkpoint']['path']);run=Path(v['run']);pid=v['own_PID_bound_receipt']['pid']
assert ck.is_relative_to(D/'learning_logs') and ck.parent==run and v['source_sha256']==SOURCE_SHA and not v['discarded_preflight']
from curb20_entry_fullsave_cpu import fullsave
info=fullsave(ck);assert info['sha256']==v['checkpoint']['sha256'] and info['finite_tensors']==102
assert j(run/'latest_complete.json')['pid']==pid and j(run/'latest_complete.json')['checkpoint']==str(ck)
m=j(run/'run_manifest.json');freeze=j(R/'SOURCE_FREEZE.json');assert m['source_map']==freeze['sha256'] and m['init_checkpoint_sha256']==SOURCE_SHA
for name,h in m['src_sha256'].items():assert hashlib.sha256((run/'src_snapshot'/name).read_bytes()).hexdigest()==h
b=j(Path(BUDGET));seg=[s for s in b['completed_segments'] if s['pid']==pid];assert len(seg)==1 and seg==v['unique_completed_segment']
health=v['health'];assert health['actual_physics_callbacks']==health['expected_physics_callbacks']==health['control_steps']*4
assert v['actual_environment_steps']==health['control_steps']*20000 and v['actual_updates']*24==health['control_steps']
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,pending=False,source_SHA=SOURCE_SHA,own_checkpoint=info,CPU102_noCUDA=True,own_PID=pid,actual_source_count=len(freeze['sha256']),actual_snapshot_file_count=sum(p.is_file() for p in (run/'src_snapshot').rglob('*')),own_manifest_receipt_snapshot_exact=True,own_unique_completed_segment=seg,health=health,entry_scope_new_transition_disclosed=True,not_PhysX_exactresume=True,no_mutation=True)))
'''.replace('ROOT',repr(NEW)).replace('SOURCE_SHA',repr(io.SHA)).replace('BUDGET',repr(io.B))
  _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:
   save('ENTRY_SEED_OWN_CPU_READER_REJECTED_'+str(time.time_ns())+'.json',dict(epoch=time.time(),returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),no_mutation=True));raise RuntimeError('Own formal CPU read refused')
  v=json.loads(raw);p=save('ENTRY_SEED_OWN_FORMAL_CPU_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),passed=v.get('passed',False),pending=v.get('pending',False),checkpoint=v.get('own_checkpoint'),actual_source_count=v.get('actual_source_count'),actual_snapshot_file_count=v.get('actual_snapshot_file_count'))))
 finally:io.cleanup(n,w)

if __name__=='__main__':main()
