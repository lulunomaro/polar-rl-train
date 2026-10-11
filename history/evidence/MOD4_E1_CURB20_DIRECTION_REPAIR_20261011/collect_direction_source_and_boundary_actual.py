"""Read actual closed410 and source files; no stage/main or GPU replay."""
from direction_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import json,time,hashlib,fcntl
D=Path(OLDROOT);B=Path(BUDGET);E=Path(CENTRAL);j=lambda p:json.loads(p.read_bytes());s=j(D/'reports/E1_STATE.json');assert s['child'] is None and s['phase']=='E1_CURB20_entry_repair_saved_review_ready'
p=j(D/'reports/e1_CURB20_entry_repair_observation_PASSED.json');assert p['checkpoint']['sha256']=='2fe67400d4119b94dbf33d7770b7fec44a9c73c568256e8161c3d8298ad73a04' and len(p['unique_completed_segment'])==1
exits=[]
for loc in (s['owner'],j(D/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=86034491)):
 q=Path('/proc')/str(loc['pid']);a=None
 if q.exists():
  f=(q/'stat').read_text().split(') ',1)[1].split();a=dict(state=f[0],start_ticks=int(f[19]));assert a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 exits.append(dict(locator=loc,actual=a))
b=j(B);assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and 36000+sum(x['additional_training_seconds'] for x in b['budget_extensions'])==1188000
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(q))
c=j(E/'reports/MOE_PLAN_EXECUTION_CURRENT.json');assert c['terrain_subexpert_revision004']['curb20_entry_seed_reviewed_scope']['actual_139_review_complete'] and c['budget_retrain_revision005']['approved']
freeze=j(D/'reports/SOURCE_FREEZE.json');assert len(freeze['sha256'])==410
print(json.dumps(dict(epoch=time.time(),own410_fullsave=p['checkpoint'],own410_exits=exits,OS_locks_free=locks,active_segment=None,authorized_seconds=1188000,remaining_seconds=b['authorized_training_seconds']-b['charged_training_seconds'],canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),source_freeze=freeze,complete139_review_verified=True,no_GPU_or_PPO_or_budget_write=True)))
'''.replace('OLDROOT',repr(OLD)).replace('BUDGET',repr(io.B)).replace('CENTRAL',repr(io.E)))
  save('DIRECTION_ACTUAL_AUTHORITY_BOUNDARY.json',v)
  names=['isaac/mod4/e1_terrain_runtime.py','isaac/mod4/curb20_command_migration_environment_view.py','isaac/mod4/curb20_entry_target_cpu.py','isaac/mod4/train_curb20_entry_fresh_preflight_ppo.py','isaac/mod4/train_curb20_entry_resume_ppo.py','isaac/mod4/probe_curb20_entry_fresh_process_full_resume.py','supervise_curb20_entry_fullstate_once.py','native_curb20_entry_origin_bound_sdk_probe.py','isaac/mod4/retention_flat_runtime.py','isaac/mod4/curb20_entry_full_checkpoint.py','isaac/mod4/curb20_entry_v3_full_pose_reset.py','isaac/mod4/curb20_entry_v3_runtime.py','isaac/mod4/curb20_entry_v2_math.py','isaac/mod4/curb20_entry_current_state.py','isaac/mod4/curb20_entry_fullsave_cpu.py']
  rows=[]
  with n.open_sftp() as f:
   for name in names:
    with f.open(OLD+'/'+name,'rb') as q:b=q.read()
    assert H(b)==v['source_freeze']['sha256'][name];p=D/'inherited_source'/name;assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);rows.append(dict(path=str(p),remote_path=OLD+'/'+name,bytes=len(b),sha256=H(b)))
  save('DIRECTION_INHERITED_SOURCE_COLLECTION.json',dict(epoch=time.time(),files=rows,exact=True))
  print(json.dumps(dict(source_files=len(rows),old410_closed=True,locks_free=True,remaining_seconds=v['remaining_seconds'],no_GPU_launch=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
