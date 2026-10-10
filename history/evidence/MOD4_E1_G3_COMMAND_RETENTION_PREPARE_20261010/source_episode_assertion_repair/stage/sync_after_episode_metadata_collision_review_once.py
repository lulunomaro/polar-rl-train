"""New command ownership scope metadata only; no training, ledger or replay action."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';NEW='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_EPISODE_REVIEWED_20261010'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,indent=2).encode())
def main():
 save('COMMAND_EPISODE_COLLISION_REVIEW_SYNC_STARTED.json',dict(epoch=time.time(),new_metadata_only=True,no_canonical_GPU_queue_write=True))
 files={
 'E1_G3_COMMAND_RETENTION_364_TARGET_CPU_ADMITTED.json':R/'EPISODE_REPAIR_TARGET_CPU_ADMITTED.json',
 'E1_G3_COMMAND_RETENTION_360_SOURCE_EPISODE_REFUSAL.json':R/'SOURCE_EPISODE_WRAPPER_REFUSAL_ACTUAL_DECISION.json',
 'E1_G3_COMMAND_RETENTION_364_DISPATCH_ACTUAL.json':R/'EPISODE_REPAIR_DISPATCH_ACTUAL.json',
 'E1_G3_COMMAND_RETENTION_364_CURRENT_ACTUAL.json':sorted(R.glob('EPISODE_REPAIR_ACTUAL_*.json'))[-1],
 'NEXT_E1_G3_COMMAND_RETENTION_EPISODE_REVIEW_WORK_ORDER.json':R/'NEXT_E1_G3_COMMAND_RETENTION_EPISODE_REVIEW_WORK_ORDER.json',
 'NEXT_E1_G3_COMMAND_RETENTION_EPISODE_REVIEW_WORK_ORDER.md':R/'NEXT_E1_G3_COMMAND_RETENTION_EPISODE_REVIEW_WORK_ORDER.md',
 'E1_G3_COMMAND_RETENTION_364_IMPLEMENTATION_REPORT.md':D/'REPORT.md'}
 secret,_=recover('RM_SSH_PASSWORD');os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:
   for n,p in files.items():
    raw=p.read_bytes()
    path=E+'/reports/'+n
    try:existing=f.open(path).read()
    except FileNotFoundError:existing=None
    if existing is None:
     with f.open(path,'wbx') as out:out.write(raw)
    else:assert existing==raw,('Different existing report preserved',n)
    assert f.open(path).read()==raw
  code=r"""from pathlib import Path
import hashlib,json,os,time
R=Path(REPORTS);D=Path(CURRENT_ROOT);H=lambda b:hashlib.sha256(b).hexdigest();j=lambda p:json.loads(p.read_bytes())
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
s=j(D/'reports/E1_STATE.json');assert j(D/'reports/RETENTION_TARGET_CPU_PASSED.json')['private_named_generator_ownership_exact'] and j(D/'reports/RETENTION_TARGET_CPU_PASSED.json')['saved_source_episode_baseline_CPU_verified']
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);assert 'E1_G3_command_retention_364_execution_event' not in v
v['E1_G3_command_retention_364_execution_event']=dict(epoch=time.time(),actual_root=str(D),source_files=364,actual_parent_owned_state=s,actual_reader='read_episode_reviewed_actual.py',SCUT_complete_previous_detailed_review=str(R/'SCUT_E1_RETENTION_DETAILED_REVIEW.md'),actual_360_episode_wrapper_refusal=str(R/'E1_G3_COMMAND_RETENTION_360_SOURCE_EPISODE_REFUSAL.json'),native10_native20k_small128_valid_exact_reuse=True,new_owned_private_generator_keeps_legacy_named_set_exact=True,new_scope_only_full20k_restore_and300s_if_actual_PASSED=True,work_order=str(R/'NEXT_E1_G3_COMMAND_RETENTION_EPISODE_REVIEW_WORK_ORDER.json'),actual129_fourcase_required_before_more_learning=True,no_forgetting_cure_or_50mm_or_RM70mm_graduation=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.CommandOwnership-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='E1 G3 command retention source364 savedepisode20261010:';assert marker.encode() not in old
message=chr(10)*2+marker+' Actual355 native10x300/20k24+120 and128x2PPO passed; original348signature/353actualassignment/355legacy named RNG strict refusals and charged costs retained. Original360 private named ownership and full old D1-D7/G3 CUDA restore passed; new outer wrapper used initial instead of saved source episode baseline and was refused before learning.364 is360byteexact+4 separate saved-source episode assertion/entry/controller/CPU files; target CPU actual source episode range5to10 and3 contract checks passed, prior CPU14/named5 reused; exactnative/small/clock/geometry/D0D7 reuse, no repeats. Actual state and own receipts override cached active snapshots. Controller sole canonical accounting, full20kx4 actualresume/PPO complete then only300sload-learn-save-exit, fullsave and129 terrain-flat-spin-world frozen review. Pending healthy silent; do not claim retention fixed or35mm/50mm/RM70mm graduation. Read new ownership workorder, no oldonce/main/resume/native/SDK/PPO/record/sync/budgettail replay; nohotpatch/kill/dual20k/clearactive/extension/S7/S8/teacher. All new saved reports/errors/results/monitor/sync requireGit. ACTIVEevery2h unchanged.'+chr(10)
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.CommandOwnership-'+str(time.time_ns()));tmp.write_bytes(old+message.encode());os.replace(tmp,hp)
assert all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),current_before_SHA=H(before),current_after_SHA=H(raw),master_approval_tracks_RM_bytes_preserved=True,no_canonical_GPU_queue_or_active_learning_field_write=True,parent_normal_accounting_not_compared_as_immutable_ledger=True,actual_parent_state=s)))
""".replace('REPORTS',repr(E+'/reports')).replace('CURRENT_ROOT',repr(NEW))
  compile(code,'<commandOwnershipMetadata>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
  v['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];save('COMMAND_EPISODE_COLLISION_REVIEW_SYNCED.json',v)
  with c.open_sftp() as f:
   raw=(R/'COMMAND_EPISODE_COLLISION_REVIEW_SYNCED.json').read_bytes()
   with f.open(E+'/reports/E1_G3_COMMAND_RETENTION_364_METADATA_SYNCED.json','wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_COMMAND_RETENTION_364_METADATA_SYNCED.json').read()==raw
  print(json.dumps(dict(metadata_synced=True,phase=v['actual_parent_state']['phase'],new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('COMMAND_EPISODE_COLLISION_REVIEW_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_repeat_completed_metadata=True));raise
