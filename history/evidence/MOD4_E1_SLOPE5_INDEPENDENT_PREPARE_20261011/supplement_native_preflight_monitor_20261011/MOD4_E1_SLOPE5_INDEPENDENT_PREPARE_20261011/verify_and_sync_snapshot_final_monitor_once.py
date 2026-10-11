from slope_io import *
import os,tomllib,traceback
def main():
 p=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml';a=tomllib.loads(p.read_text(encoding='utf8'));expected=(D/'MONITOR_CURRENT_FORMAL_FINAL_PROMPT.md').read_text(encoding='utf8').strip();assert a['prompt']==expected and a['status']=='ACTIVE' and a['rrule']=='FREQ=HOURLY;INTERVAL=2' and '\ufffd' not in a['prompt']
 row=dict(epoch=time.time(),automation_id='mod4-10',app_prompt_exact=True,status=a['status'],rrule=a['rrule'],bytes=len(a['prompt'].encode()),sha256=H(a['prompt'].encode()),own_formal_final_and135actual_priority=True,no_extra_automation_or_GPU_action=True)
 rp=save('SNAPSHOT_FINAL_MONITOR_ACTUAL_VERIFIED.json',row);n,w=connect_both()
 try:
  with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE5_SNAPSHOT_FINAL_MONITOR_ACTUAL_VERIFIED.json',rp.read_bytes())
  result=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);beforeB=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);s=v['terrain_subexpert_revision004']['slope5_independent_scope'];assert s['root']=='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011' and s['formal_actual_saved_exit_CPU_PASSED'] and s['actual_135_fullreview_pending']
s.update(monitor_receipt=str(R/'E1_SLOPE5_SNAPSHOT_FINAL_MONITOR_ACTUAL_VERIFIED.json'),formal_closeout_metadata_synced=str(R/'E1_SLOPE5_SNAPSHOT_REVIEWED_FORMAL_CLOSEOUT_METADATA_SYNCED.json'))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.SLOPE404MON-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
assert B.read_bytes()==beforeB and all((R/n).read_bytes()==raw for n,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,monitor_status_ACTIVE_every2h_and_ownfinal_priority=True,master_approval_tracks_RM_canonical_bytes_preserved=True,no_GPU_or_budget_action=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)))
  p=save('SNAPSHOT_FINAL_MONITOR_METADATA_SYNCED.json',result)
  with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE5_SNAPSHOT_FINAL_MONITOR_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(dict(monitor=row,metadata=result)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SNAPSHOT_FINAL_MONITOR_SYNC_ERROR.json',dict(error=traceback.format_exc(),no_oldsync_replay=True));raise
