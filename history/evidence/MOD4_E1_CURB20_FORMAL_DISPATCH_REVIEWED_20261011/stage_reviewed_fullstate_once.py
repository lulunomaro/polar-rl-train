"""New reviewed root preserves378; two independent validation additions, no GPU."""
from stage_fullstate_once import D,R,E,B,PY,connect_both,cleanup,linux_json,H,save,put
from pathlib import Path
import json,shlex,time,traceback
OLD='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FULL_STATE_20261011'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FULL_STATE_REVIEWED_20261011'
def main():
 save('REVIEWED_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='CURB-FULLSTATE-REVIEWED-CPU-DEPLOY-01',once=True,no_GPU=True))
 n,w=connect_both()
 try:
  copy=linux_json(n,r'''from pathlib import Path
import json,hashlib,shutil,fcntl,time
old=Path(OLD);new=Path(NEW);B=Path(BUDGET);budget=B.read_bytes();assert not new.exists()
assert json.loads(budget)['active_segment'] is None and not (old/'reports/E1_DISPATCH_STARTED.json').exists()
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
f=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes());assert len(f['sha256'])==378
new.mkdir();(new/'reports').mkdir()
for name,h in f['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('SOURCE_SELECTED.json','CURB132_COMPLETE_ACTUAL_REVIEW.json','CURB_REUSED_NATIVE.json','CURB_FOUR_CASE_TEMPLATES.json'):
 shutil.copy2(old/'reports'/name,new/'reports'/name)
assert B.read_bytes()==budget
print(json.dumps(dict(epoch=time.time(),old378_all_bytes_preserved=True,first378_no_GPU_or_learning_dispatched=True,canonical_SHA=hashlib.sha256(budget).hexdigest(),source_freeze=f,new_root=str(new))))
'''.replace('Path(OLD)','Path('+repr(OLD)+')').replace('Path(NEW)','Path('+repr(NEW)+')').replace('BUDGET',repr(B)))
  save('REVIEWED_378_COPIED.json',copy)
  with n.open_sftp() as f:
   freeze=copy['source_freeze'];hashes=dict(freeze['sha256'])
   for p in sorted((D/'reviewed_payload').rglob('*')):
    if not p.is_file():continue
    name=p.relative_to(D/'reviewed_payload').as_posix();raw=p.read_bytes();compile(raw,name,'exec');assert name not in hashes
    put(f,NEW+'/'+name,raw);hashes[name]=H(raw)
   assert len(hashes)==380
   freeze=dict(freeze,candidate_root=NEW,sha256=hashes,all378_predecessor_bytes_preserved=True,predeployment_CPU_validation_adapter_reviewed=True)
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('REVIEWED_SOURCE_FREEZE.json',freeze)
   put(f,NEW+'/reports/PREDEPLOY_VALIDATOR_SOURCE_REVIEW.json',(R/'PREDEPLOY_VALIDATOR_SOURCE_REVIEW.json').read_bytes())
  code=r'''from pathlib import Path
import contextlib,io,json,sys,tempfile,time,torch,hashlib
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
from test_curb_fullstate_cpu import main
source=json.loads((D/'reports/SOURCE_SELECTED.json').read_bytes());p=Path(source['path']);out=io.StringIO()
with contextlib.redirect_stdout(out):main(p)
cpu=json.loads(out.getvalue());assert cpu['passed']
ck=torch.load(p,map_location='cpu',weights_only=False)
native=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_INDEPENDENT_20261011/CURB_NATIVE20K.json')
reuse=json.loads((D/'reports/CURB_REUSED_NATIVE.json').read_bytes());assert hashlib.sha256(native.read_bytes()).hexdigest()==reuse['results']['CURB_NATIVE20K']['sha256']
v=json.loads(native.read_bytes());state=ck['E1_terrain_state']
for k in tuple(state):
 if k.startswith('G3_'):state.pop(k)
state.update(v['E1_terrain_identity']);ck['E1_retained_flat_command_state']['assignment_sha256']=v['command_retention']['assignment_sha256']
ck['independent_terrain_expert']='E1_CURB';ck['E1_CURB_initial_source_sha256']=source['sha256']
import supervise_curb20_fullstate_reviewed_once as own
with tempfile.TemporaryDirectory() as tmp:
 q=Path(tmp)/'CPU_schema_fixture_not_physical.pt';torch.save(ck,q);info=own.fullsave(q)
 assert info['finite_tensors']==102
cpu.update(epoch=time.time(),source_count=380,corrected_CURB_fullschema_CPU_fixture_passed=True,
 all_original_D0_D7_validators_retained=True,fixture_uses_actual_native_CURB_identity_no_CUDA_or_physical_resume_claim=True,
 actual_CURB_CUDA_PPO_pending=True,new_root=str(D))
(D/'reports/CURB_TARGET_FULLSTATE_CPU_PASSED.json').write_text(json.dumps(cpu,indent=2))
own.prior.verify();own.prior.wait_existing();assert not torch.cuda.is_initialized()
print(json.dumps(cpu))
'''.replace('ROOT',repr(NEW))
  compile(code,'<reviewed-fullstate-cpu>','exec');_,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('REVIEWED_TARGET_CPU_ERROR.json',dict(epoch=time.time(),returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),no_GPU_or_budget_transaction=True));raise RuntimeError('Reviewed CPU admission rejected; original retained')
  cpu=json.loads(raw);save('REVIEWED_TARGET_CPU_PASSED.json',cpu)
  save('REVIEWED_STAGE_VERIFIED.json',dict(epoch=time.time(),root=NEW,source_count=380,CPU_passed=True,original378_preserved=True,native_no_replay=True,CUDA_fullresume_PPO_formal_pending=True))
  print(json.dumps(dict(root=NEW,source_count=380,CPU_passed=True,original372_and378_preserved=True,no_GPU_started=True)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('REVIEWED_STAGE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_stage=True,all_sources_retained=True));raise
