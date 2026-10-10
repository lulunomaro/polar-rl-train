"""Once: synchronize actual formal closure and current129 collection, preserve original files."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';NEW='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_EPISODE_REVIEWED_20261010'
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 actual=json.loads(sorted(R.glob('EPISODE_REPAIR_ACTUAL_*.json'))[-1].read_bytes());own=json.loads(sorted(R.glob('COMMAND_OWN_SAVE_ACTUAL_*.json'))[-1].read_bytes())
 assert own['formal_saved'] and not own['pending'] and actual['reports']['E1_STATE.json']['phase']=='E1_G3_command_retention_saved_review_ready' and actual['canonical']['active'] is None and actual['actual']==[None,None,None]
 saved=actual['reports']['e1_G3_command_retention_observation_PASSED.json'];assert len(saved['unique_completed_segment'])==1 and not saved['discarded_preflight']
 save('COMMAND_FORMAL_CLOSEOUT_SYNC_STARTED.json',dict(epoch=time.time(),metadata_only=True,no_old_formal_replay_or_accounting=True))
 files={
 'E1_G3_COMMAND_RETENTION_FORMAL_FINAL_ACTUAL_REVIEW.json':R/'COMMAND_FORMAL_FINAL_ACTUAL_REVIEW.json',
 'E1_G3_COMMAND_RETENTION_OWN_FORMAL_CPU_VERIFIED.json':sorted(R.glob('COMMAND_OWN_SAVE_ACTUAL_*.json'))[-1],
 'E1_G3_COMMAND_RETENTION_FORMAL_FINAL_CURRENT_ACTUAL.json':sorted(R.glob('EPISODE_REPAIR_ACTUAL_*.json'))[-1],
 'E1_G3_COMMAND_RETENTION_129_CURRENT_COLLECTION.json':sorted(R.glob('CANDIDATE_129_COLLECTED_*.json'))[-1],
 'E1_G3_COMMAND_RETENTION_NATIVE_AND_PREFLIGHT_ACTUAL_ADMITTED.json':R/'COMMAND_NATIVE_AND_PREFLIGHT_ACTUAL_ADMITTED.json',
 'E1_G3_COMMAND_RETENTION_GIT_STAGE1_RECORDED.json':R/'STAGE_GIT_RECORDED.json',
 'E1_G3_COMMAND_RETENTION_GIT_STAGE2_RECORDED.json':R/'EPISODE_STAGE_GIT_RECORDED.json'}
 secret,_=recover('RM_SSH_PASSWORD');os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:
   for n,p in files.items():
    raw=p.read_bytes()
    with f.open(E+'/reports/'+n,'wbx') as out:out.write(raw)
    assert f.open(E+'/reports/'+n).read()==raw
  code=r"""from pathlib import Path
import hashlib,json,time,os,fcntl
R=Path(REPORTS);D=Path(ROOT);B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');H=lambda b:hashlib.sha256(b).hexdigest();j=lambda p:json.loads(p.read_bytes())
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
budget=B.read_bytes();ledger=json.loads(budget);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
for lock in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with lock.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
state=j(D/'reports/E1_STATE.json');assert state['phase']=='E1_G3_command_retention_saved_review_ready' and state['child'] is None
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);event=v['E1_G3_command_retention_364_execution_event'];assert 'formal_actual_closeout' not in event
keys=['E1_G3_COMMAND_RETENTION_FORMAL_FINAL_ACTUAL_REVIEW.json','E1_G3_COMMAND_RETENTION_OWN_FORMAL_CPU_VERIFIED.json','E1_G3_COMMAND_RETENTION_FORMAL_FINAL_CURRENT_ACTUAL.json','E1_G3_COMMAND_RETENTION_129_CURRENT_COLLECTION.json','E1_G3_COMMAND_RETENTION_GIT_STAGE1_RECORDED.json','E1_G3_COMMAND_RETENTION_GIT_STAGE2_RECORDED.json']
event['formal_actual_closeout']=dict(epoch=time.time(),reports={n:str(R/n) for n in keys},actual_saved_phase=state['phase'],no_active_legal_review_boundary=True,all_courses_finished=False,actual129_behavior_still_required_before_more_PPO=True,no_permanent_anti_forgetting_proof=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.CommandFormal-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='E1 G3 command retention source364 own formal closeout20261010:';assert marker.encode() not in old
msg=chr(10)*2+marker+' Own source364 complete formal CPU/PID/PASSED/full old and new command state/actual72 snapshot+364 ownfreeze reviewed; originalparent uniquely settled and actualparent/guardian/child all exited/two original locksfree/noactive legal.129fourcases actually published; read current collector/reviewer actual complete/errorfree2hostbyteSHA/fullNPZ/full root30q-contact-COM-hardware and original signedcycles before morePPO or nextaxis. Old127/128/115complete exactreuse, never replay. Oldfailed348/353/355/360 source/raw/cost preserved. No permanentanti-forgetting/full35mm/E1/RM70mm graduation. Two new annotatedstageGit actualmain/tag/peeled receipts available; all later final/129/sync/monitor reports needGit supplement. ACTIVEevery2h healthy pendingquiet; nooldonce/main/resume/nativeSDK/preflight/record/sync/budgettail replay, nohotpatch/kill/dual20k/clear/extension/S7/S8/teacher.'+chr(10)
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.CommandFormal-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),canonical_bytes_preserved=True,master_approval_tracks_RM_bytes_preserved=True,actual_formal_closeout_synced=True,actual129_collected_stage_only=True,new_budget_seconds=0,remaining_seconds=ledger['authorized_training_seconds']-ledger['charged_training_seconds'],current_before_SHA=H(before),current_after_SHA=H(raw))))
""".replace('REPORTS',repr(E+'/reports')).replace('ROOT',repr(NEW))
  compile(code,'<commandFormalCloseout>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);v['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];save('COMMAND_FORMAL_CLOSEOUT_METADATA_SYNCED.json',v)
  with c.open_sftp() as f:
   raw=(R/'COMMAND_FORMAL_CLOSEOUT_METADATA_SYNCED.json').read_bytes()
   with f.open(E+'/reports/E1_G3_COMMAND_RETENTION_FORMAL_CLOSEOUT_METADATA_SYNCED.json','wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_COMMAND_RETENTION_FORMAL_CLOSEOUT_METADATA_SYNCED.json').read()==raw
  print(json.dumps(dict(formal_closeout_synced=True,remaining=v['remaining_seconds'],new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('COMMAND_FORMAL_CLOSEOUT_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_repeat_completed_transactions=True));raise
