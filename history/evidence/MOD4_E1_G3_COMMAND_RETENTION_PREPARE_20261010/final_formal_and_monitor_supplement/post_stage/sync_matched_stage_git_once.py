"""Synchronize verified stage Git and actual active ownsave references, metadata only."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,indent=2).encode());return p
def main():
 stage=json.loads((R/'MATCHED_STAGE_GIT_RECORDED.json').read_bytes());assert stage['remote_main_tag_peeled_verified'] and not stage['push_pending']
 own=sorted(R.glob('COMMAND_MATCHED_OWN_CPU_[0-9]*.json'))[-1];v=json.loads(own.read_bytes());assert v['saved'] and not v['pending']
 save('COMMAND_MATCHED_GIT_SYNC_STARTED.json',dict(epoch=time.time(),new_verified_stage_metadata_only=True,new_budget_seconds=0))
 files={'E1_G3_COMMAND_RETENTION_MATCHED_GIT_RECORDED.json':R/'MATCHED_STAGE_GIT_RECORDED.json','E1_G3_COMMAND_RETENTION_MATCHED_OWN_ACTIVE_CPU_VERIFIED.json':own}
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:
   for n,p in files.items():
    raw=p.read_bytes()
    with f.open(E+'/reports/'+n,'wbx') as out:out.write(raw)
    assert f.open(E+'/reports/'+n).read()==raw
  code=r'''from pathlib import Path
import json,hashlib,time,os
R=Path(REPORTS);H=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);event=v['E1_G3_command_retention_365_matched_execution_event'];assert 'verified_stage_Git' not in event
stage=json.loads((R/'E1_G3_COMMAND_RETENTION_MATCHED_GIT_RECORDED.json').read_bytes());assert stage['remote_main_tag_peeled_verified'] and not stage['push_pending']
event['verified_stage_Git']=stage;event['own_active_CPU_report']=str(R/'E1_G3_COMMAND_RETENTION_MATCHED_OWN_ACTIVE_CPU_VERIFIED.json');event['later_final_130_sync_monitor_reports_need_Git_supplement']=True
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.MatchedGit-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
assert all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),actual_stage_Git_and_active_own_CPU_metadata_synced=True,master_approval_tracks_RM_bytes_preserved=True,no_canonical_training_or_queue_write=True,current_before_SHA=H(before),current_after_SHA=H(raw),new_budget_seconds=0)))
'''.replace('REPORTS',repr(E+'/reports'))
  compile(code,'<matchedGitMetadata>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);v['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];p=save('COMMAND_MATCHED_GIT_METADATA_SYNCED.json',v)
  with c.open_sftp() as f:
   raw=p.read_bytes()
   with f.open(E+'/reports/E1_G3_COMMAND_RETENTION_MATCHED_GIT_METADATA_SYNCED.json','wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_COMMAND_RETENTION_MATCHED_GIT_METADATA_SYNCED.json').read()==raw
  print(json.dumps(dict(stage_Git_metadata_synced=True,new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('COMMAND_MATCHED_GIT_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_repeat_completed_sync_or_record=True));raise
