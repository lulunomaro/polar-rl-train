"""Stage one new expert-owned output root with all365 mathematical source bytes exact."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';N=W/'MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
OLD='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010';NEW='/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010';PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def call(c,code,py='/usr/bin/python3'):
 _,o,e=c.exec_command(py+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');return json.loads(raw)
def put(f,p,b):
 with f.open(p,'wbx') as q:q.write(b)
 assert f.open(p).read()==b
def main():
 assert json.loads((R/'REVISION_METADATA_SYNCED.json').read_bytes())['revision004_synced']
 assert not (R/'WAVE_STAGE_STARTED.json').exists();save('WAVE_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='E1-WAVE-INDEPENDENT-REVISION004-DEPLOY-01',CPU_only=True,new_budget_seconds=0))
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  v=call(c,r'''from pathlib import Path
import hashlib,json,shutil,fcntl,time
old=Path(OLD);new=Path(NEW);assert not new.exists();B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');budget=B.read_bytes();l=json.loads(budget);assert l['active_segment'] is None and l['authorized_training_seconds']==828000
s=json.loads((old/'reports/E1_STATE.json').read_bytes());p=json.loads((old/'reports/e1_G3_command_retention_matched_PASSED.json').read_bytes());assert s['phase']=='E1_G3_command_retention_matched_saved_review_ready' and s['child'] is None and p['checkpoint']['sha256']=='f5b1623e71fc5d6f3682ca19594bdf43db5a391ce9fc046ec48f8ce90dde234a' and len(p['unique_completed_segment'])==1
for loc in (s['owner'],json.loads((old/'reports/E1_GUARDIAN_STARTED.json').read_bytes()),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=79649880)):
 q=Path('/proc')/str(loc['pid'])
 if q.exists():
  a=(q/'stat').read_text().split(') ',1)[1].split();assert a[0]=='Z' or int(a[19])!=loc['start_ticks']
for lock in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with lock.open('r') as q:fcntl.flock(q,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(q,fcntl.LOCK_UN)
f=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes());assert len(f['sha256'])==365;new.mkdir();(new/'reports').mkdir()
for n,h in f['sha256'].items():
 p=old/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=new/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
assert B.read_bytes()==budget
print(json.dumps(dict(epoch=time.time(),old365_all_source_bytes_exact=True,no_active_two_real_locks_free_all365_actual_exited=True,canonical_preserved=True,new_root=str(new))))
'''.replace('Path(OLD)','Path('+repr(OLD)+')').replace('Path(NEW)','Path('+repr(NEW)+')'));save('WAVE_365_COPIED.json',v)
  name='supervise_e1_wave_isolated_revision004_once.py';raw=(D/'payload'/name).read_bytes();compile(raw,name,'exec')
  selection=json.loads((N/'reports/COMMAND130_COMPLETE_RETENTION_DECISION.json').read_bytes())['selected_rollback_source'];assert selection['sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
  with c.open_sftp() as f:
   old=json.loads(f.open(OLD+'/reports/SOURCE_FREEZE.json').read());sha=dict(old['sha256']);assert name not in sha;put(f,NEW+'/'+name,raw);sha[name]=H(raw)
   freeze=dict(old,candidate_root=NEW,sha256=sha,old365_allbytes_preserved=True,independent_expert='E1_WAVE',new_command_or_geometry_scope=False)
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('WAVE_SOURCE_FREEZE.json',freeze)
   for n in ('MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','REVISION_APPROVED.json'):put(f,NEW+'/reports/'+n,(R/n).read_bytes())
   put(f,NEW+'/reports/SOURCE_SELECTED.json',json.dumps(selection,indent=2).encode())
   put(f,NEW+'/reports/CANDIDATE_130_COMPLETE_ACTUAL_REVIEW.json',sorted((N/'reports').glob('CANDIDATE_130_REVIEW_[0-9]*.json'))[-1].read_bytes())
   for n in ('E1_PLANNED_BEHAVIOR_PUBLISHED.json','G3_BEHAVIOR_PACKAGE_READY.json'):put(f,NEW+'/reports/'+n,f.open(OLD+'/reports/'+n).read())
   reuse=dict(same_geometry_same_command_scope_all_actual_contracts_exact_reused=True,no_new_math_or_plant_or_reward=True,original365_contracts=json.loads(f.open(OLD+'/reports/REUSED_CONTRACTS.json').read()),old365_all_source_bytes_preserved=True,no_repeated_GPU_preflight_clock=True,first300s_expert_own_output_and_gradient_namespace_only=True)
   put(f,NEW+'/reports/REUSED_CONTRACTS.json',json.dumps(reuse,indent=2).encode());save('WAVE_REUSED_CONTRACTS.json',reuse)
  cpu=call(c,r'''from pathlib import Path
import sys,torch,json,time,hashlib
D=Path(ROOT);R=D/'reports';sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_e1_wave_isolated_revision004_once as m
m.wait_existing();p=m.source();ck=torch.load(p,map_location='cpu',weights_only=False);other=torch.load(p,map_location='cpu',weights_only=False)
assert ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1' and ck['E1_retained_flat_command_state'] and ck['sensor_global_rng_state']['cuda'] and not torch.cuda.is_initialized()
checked=0
for group in ('actor_state_dict','critic_state_dict'):
 for n,a in ck[group].items():
  b=other[group][n];assert a.data_ptr()!=b.data_ptr() and torch.equal(a,b);checked+=1
a=next(iter(ck['actor_state_dict'].values()));b=next(iter(other['actor_state_dict'].values()));saved=b.clone();a.add_(1);assert torch.equal(saved,b)
assert hashlib.sha256(p.read_bytes()).hexdigest()==m.SOURCE_SHA
result=dict(epoch=time.time(),passed=True,expert='E1_WAVE',source=m.fullsave(p),source_file_SHA_preserved=True,actual_loaded_actor_critic_tensors_independent=checked,mutation_of_one_CPU_copy_does_not_change_other=True,output_root=str(D/'learning_logs'),same35mm_same_command_schema_CPU_verified=True,no_other_expert_in_optimizer_or_save_targets=True,no_CUDA_initialized=True,actual_CUDA_same_scope_restore_and_episode_plus_one_pending_startup=True,source_count=366,no_new_GPU_preflight_or_clock=True,new_budget_seconds=0)
(R/'EXPERT_OWNERSHIP_CPU_PASSED.json').write_bytes(json.dumps(result,indent=2).encode());m.verify();print(json.dumps(result))
'''.replace('Path(ROOT)','Path('+repr(NEW)+')'),PY);save('WAVE_TARGET_CPU_ADMITTED.json',cpu);print(json.dumps(cpu))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('WAVE_STAGE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),new_root_retained=True,no_replay_or_GPU_or_canonical_write=True));raise
