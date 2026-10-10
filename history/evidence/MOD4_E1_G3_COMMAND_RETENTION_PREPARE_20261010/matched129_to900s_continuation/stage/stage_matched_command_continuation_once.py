"""Stage365 byteexact old364 plus one controller; verify ownreviewed102 source on CPU."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
OLD='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_EPISODE_REVIEWED_20261010';NEW='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010';PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,indent=2).encode())
def call(c,code,py='/usr/bin/python3'):
 _,o,e=c.exec_command(py+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');return json.loads(raw)
def put(f,p,b):
 with f.open(p,'wbx') as q:q.write(b)
 assert f.open(p).read()==b
def main():
 assert json.loads((R/'COMMAND129_COMPLETE_METADATA_SYNCED.json').read_bytes())['complete129_decision_synced']
 save('COMMAND_MATCHED_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-COMMAND-MATCHED-900S-DEPLOY-01',CPU_only=True,new_budget_seconds=0))
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  v=call(c,r'''from pathlib import Path
import hashlib,json,shutil,fcntl,time,os
old=Path(OLD);new=Path(NEW);assert not new.exists()
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');before=B.read_bytes();ledger=json.loads(before);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
state=json.loads((old/'reports/E1_STATE.json').read_bytes());assert state['child'] is None and state['phase']=='E1_G3_command_retention_saved_review_ready'
passed=json.loads((old/'reports/e1_G3_command_retention_observation_PASSED.json').read_bytes());assert passed['checkpoint']['sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
for locator in (state['owner'],json.loads((old/'reports/E1_GUARDIAN_STARTED.json').read_bytes()),dict(pid=passed['own_PID_bound_receipt']['pid'],start_ticks=79446206)):
 p=Path('/proc')/str(locator['pid'])
 if p.exists():
  tail=(p/'stat').read_text().split(') ',1)[1].split();assert tail[0]=='Z' or int(tail[19])!=locator['start_ticks']
for lock in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with lock.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
source=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes());assert len(source['sha256'])==364
new.mkdir();(new/'reports').mkdir()
for n,h in source['sha256'].items():
 p=old/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=new/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
assert B.read_bytes()==before
print(json.dumps(dict(epoch=time.time(),old364_source_all_bytes_exact=True,no_active_two_original_locksfree_and_all_actual_exited=True,canonical_bytes_preserved=True,new_root=str(new))))
'''.replace('Path(OLD)','Path('+repr(OLD)+')').replace('Path(NEW)','Path('+repr(NEW)+')'));save('COMMAND_MATCHED_364_COPIED.json',v)
  build=json.loads((R/'COMMAND_MATCHED_PREPARED.json').read_bytes())
  with c.open_sftp() as f:
   old=json.loads(f.open(OLD+'/reports/SOURCE_FREEZE.json').read());sha=dict(old['sha256'])
   for n,h in build['sha256'].items():
    raw=(D/'matched_continuation_payload'/n).read_bytes();assert H(raw)==h and n not in sha;put(f,NEW+'/'+n,raw);sha[n]=h
   freeze=dict(old,candidate_root=NEW,sha256=sha,old364_allbytes_preserved=True,same_command_same_G3_matched_continuation=True)
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('COMMAND_MATCHED_SOURCE_FREEZE.json',freeze)
   names={'COMMAND129_COMPLETE_RETENTION_DECISION.json':R/'COMMAND129_COMPLETE_RETENTION_DECISION.json','COMMAND129_COMPLETE_ACTUAL_REVIEW.json':sorted(R.glob('CANDIDATE_129_REVIEW_[0-9]*.json'))[-1],'COMMAND129_SELECTED_SOURCE_MATCHED_REVIEW.json':sorted(R.glob('CANDIDATE_129_SELECTED_SOURCE_REVIEW_[0-9]*.json'))[-1],'NEXT_COMMAND_RETENTION_MATCHED_CONTINUATION_WORK_ORDER.json':R/'NEXT_COMMAND_RETENTION_MATCHED_CONTINUATION_WORK_ORDER.json'}
   for n,p in names.items():put(f,NEW+'/reports/'+n,p.read_bytes())
   for n in ('E1_PLANNED_BEHAVIOR_PUBLISHED.json','G3_BEHAVIOR_PACKAGE_READY.json'):
    put(f,NEW+'/reports/'+n,f.open(OLD+'/reports/'+n).read())
   reused=dict(same_scope_CPU_SDK_native_complete_PPO_clock_D0_D7_reused_exact=True,SDK_native_small_scope='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_ASSIGNMENT_REVIEWED_20261010',complete20k_scope=OLD,no_new_geometry_or_command_profile=True,source365_only_controller_new=True,no_GPU_preflight_replay=True)
   put(f,NEW+'/reports/REUSED_CONTRACTS.json',json.dumps(reused,indent=2).encode())
   for name in ('isaac/mod4/g3_terrain_checkpoint.py','isaac/mod4/retention_command_state.py'):
    raw=f.open(OLD+'/'+name).read();p=D/'matched_readonly_contracts'/Path(name).name;p.parent.mkdir(exist_ok=True);assert not p.exists();p.write_bytes(raw)
  cpu=call(c,r'''from pathlib import Path
import sys,json,torch,time,hashlib
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_e1_command_retention_matched_once as m
from retention_command_state import PROFILE
m.verify();m.wait_existing();p=m.source();ck=torch.load(p,map_location='cpu',weights_only=False)
assert ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1' and ck['E1_current_command_profile']==PROFILE
assert 'E1_retained_flat_command_state' in ck and ck['sensor_global_rng_state']['cuda'] and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,source=m.fullsave(p),source_count=365,actual129_complete_same_geometry_same_command_source_CPU_schema_verified=True,actual_cuda_same_scope_restore_and_episode_increment_pending_startup=True,no_CUDA_initialized=True,no_GPU_SDK_native_PPO_preflight_launched=True,new_budget_seconds=0)))
'''.replace('Path(ROOT)','Path('+repr(NEW)+')'),PY);save('COMMAND_MATCHED_TARGET_CPU_ADMITTED.json',cpu);print(json.dumps(cpu))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('COMMAND_MATCHED_STAGE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),new_root_retained=True,no_GPU_or_canonical_mutation_or_blind_retry=True));raise
