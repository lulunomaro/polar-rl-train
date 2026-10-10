"""New365 metadata annotation, with actual same-scope startup; never touch ledger."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_AUDIT_20261009'))
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';NEW='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,indent=2).encode());return p
def main():
 actual=sorted(R.glob('COMMAND_MATCHED_ACTUAL_[0-9]*.json'))[-1];v=json.loads(actual.read_bytes());assert v['actual'][0] and v['actual'][1] and not v['reports'].get('E1_ATTENTION.json')
 assert v['runs'];startup=v['runs'][0]['files'];terrain=startup['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'];command=startup['E1_COMMAND_RETENTION_STARTUP_VERIFIED.json']
 assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G2_to_G3_geometry_transition'] and command['predecessor_command_state_restored_exact'] and not command['explicitly_new_command_scope']
 save('COMMAND_MATCHED_SYNC_STARTED.json',dict(epoch=time.time(),metadata_only=True,no_canonical_or_training_write=True))
 files={'E1_G3_COMMAND_RETENTION_MATCHED_TARGET_CPU_ADMITTED.json':R/'COMMAND_MATCHED_TARGET_CPU_ADMITTED.json','E1_G3_COMMAND_RETENTION_MATCHED_DISPATCH_ACTUAL.json':R/'COMMAND_MATCHED_DISPATCH_ACTUAL.json','E1_G3_COMMAND_RETENTION_MATCHED_CURRENT_ACTUAL.json':actual,'E1_G3_COMMAND_RETENTION_MATCHED_SOURCE_FREEZE.json':R/'COMMAND_MATCHED_SOURCE_FREEZE.json','NEXT_E1_G3_COMMAND_RETENTION_MATCHED_CONTINUATION_WORK_ORDER.json':R/'NEXT_COMMAND_RETENTION_MATCHED_CONTINUATION_WORK_ORDER.json'}
 # Work order already delivered by129. Reuse identical immutable bytes only.
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:
   for n,p in files.items():
    raw=p.read_bytes()
    try:old=f.open(E+'/reports/'+n).read()
    except FileNotFoundError:old=None
    if old is None:
     with f.open(E+'/reports/'+n,'wbx') as out:out.write(raw)
    else:assert old==raw,(n,'immutable delivered bytes mismatch')
    assert f.open(E+'/reports/'+n).read()==raw
  code=r'''from pathlib import Path
import json,hashlib,time,os
R=Path(REPORTS);D=Path(ROOT);B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');H=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
state=json.loads((D/'reports/E1_STATE.json').read_bytes());ledger=json.loads(B.read_bytes());assert state['phase']=='bounded_E1_G3_command_retention_matched_continuation' and ledger['active_segment']['pid']==state['child']['pid'] and ledger['authorized_training_seconds']==828000
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);key='E1_G3_command_retention_365_matched_execution_event';assert key not in v
v[key]=dict(epoch=time.time(),actual_owner=state['owner'],child_locator=state['child'],run_initial_source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',reports={n:str(R/n) for n in ['E1_G3_COMMAND_RETENTION_MATCHED_TARGET_CPU_ADMITTED.json','E1_G3_COMMAND_RETENTION_MATCHED_DISPATCH_ACTUAL.json','E1_G3_COMMAND_RETENTION_MATCHED_CURRENT_ACTUAL.json','NEXT_E1_G3_COMMAND_RETENTION_MATCHED_CONTINUATION_WORK_ORDER.json']},only_same_geometry_same_command900s=True,no_SDK_native_PPO_preflight_clock_replay=True,actual_same_G3_and_retained_command_restore_verified=True,ownfuturefinal_and130_actual_review_required=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.CommandMatched-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='E1 source365 command matched900s actual deployment20261010:';assert marker.encode() not in old
msg=chr(10)*2+marker+' Independent rootMOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010/source365=all364bytes+onecontroller. Actual129all4review complete decision admits own3c97 checkpoint; SAME35mm and SAMEplane-conditionedcommands,900s only/save25/localguardian15s. ActualsameG3terrain andsamecommand/privateCUDA restore+savedepisode1 verified; firstG2toG3/newcommandfalse now. Read actualPID/cwd/argv/start and ownrun startup/latest_complete/sourcefreeze/PASSED/unique segment, not cached364phase.130fourcases automatically afterownfullsave then reviewboundary, noautomaticthirdblock/50mm/longanti-forgetting claim. Reuse all same-scopeCPU/SDK/native/fullPPO/clock/D0D7, no replay. Canonicalactive normalparentaccounting noextension/clear/recharge. Source364formal and129failprefix/oldfalse/cost retained. All newfinal/130/sync/monitor/errors Git supplement; ACTIVEevery2h healthypendingquiet.'+chr(10)
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.CommandMatched-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert all((R/n).read_bytes()==b for n,b in protected.items());after=json.loads(B.read_bytes());assert after['authorized_training_seconds']==828000
print(json.dumps(dict(epoch=time.time(),new365_metadata_synced=True,master_approval_tracks_RM_bytes_preserved=True,canonical_only_original_parent_normally_accounting=True,no_desktop_ledger_write=True,current_before_SHA=H(before),current_after_SHA=H(raw),new_budget_seconds=0)))
'''.replace('REPORTS',repr(E+'/reports')).replace('ROOT',repr(NEW))
  compile(code,'<matched365metadata>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);v['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];p=save('COMMAND_MATCHED_METADATA_SYNCED.json',v)
  with c.open_sftp() as f:
   raw=p.read_bytes()
   with f.open(E+'/reports/E1_G3_COMMAND_RETENTION_MATCHED_METADATA_SYNCED.json','wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_COMMAND_RETENTION_MATCHED_METADATA_SYNCED.json').read()==raw
  print(json.dumps(dict(matched365_metadata_synced=True,new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('COMMAND_MATCHED_METADATA_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_repeat_completed_sync=True));raise
