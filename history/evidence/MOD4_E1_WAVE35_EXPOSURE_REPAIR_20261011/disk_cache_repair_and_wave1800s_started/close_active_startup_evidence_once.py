"""Freeze actual active-run evidence and verify the existing monitor; no GPU writes."""
from wave_io import *
import tomllib

def main():
 request=json.loads((R/'WAVE_MONITOR_UPDATE_REQUEST.json').read_bytes())
 p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');a=tomllib.loads(p.read_text(encoding='utf8'))
 assert a['status']=='ACTIVE' and a['rrule']=='FREQ=HOURLY;INTERVAL=1'
 assert a['prompt']==request['prompt']
 save('WAVE_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),automation_id='mod4-10',status=a['status'],rrule=a['rrule'],prompt_sha256=H(a['prompt'].encode()),same_existing_heartbeat=True,actual_toml_path=str(p),no_new_monitor=True))
 proofpath=sorted(R.glob('WAVE_OWN_ACTIVE_SCHEMA_CPU_ACTUAL_[0-9]*.json'))[-1];proof=json.loads(proofpath.read_bytes());assert proof['passed'] and proof['actual_updates_observed']>0
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import json,hashlib,time
D=Path(ROOT_TOKEN);run=Path(RUN_TOKEN);rows=[]
assert run.is_relative_to(D/'learning_logs')
for base in (D/'reports',run):
 for p in sorted(base.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  if p.suffix.lower() not in ('.json','.log','.txt','.pt','.npz','.md'):continue
  raw=p.read_bytes();rows.append(dict(path=str(p),relative_path=str(p.relative_to(D)),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),full_capture=p.suffix.lower() not in ('.pt','.npz') and len(raw)<=8000000))
print(json.dumps(dict(epoch=time.time(),root=str(D),run=str(run),entries=rows,active_snapshot_not_formal_final=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('RUN_TOKEN',repr(proof['own_run'])))
  dest=D/'own_active_actual';assert not dest.exists();dest.mkdir()
  with n.open_sftp() as f:
   for row in v['entries']:
    if row['full_capture']:
     raw=f.open(row['path'],'rb').read()
     # A dynamic receipt may advance while collecting; keep the frozen bytes actually read.
     row.update(bytes=len(raw),sha256=H(raw),captured_at=time.time())
     p=dest/row['relative_path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row['local_capture']=str(p)
  save('WAVE_ACTIVE_SOURCE_REPORT_COLLECTION.json',v)
  with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_WAVE35_EXPOSURE_OWN_ACTIVE_CPU_VERIFIED.json',proofpath.read_bytes())
  code=r'''from pathlib import Path
import json,time,os,hashlib
E=Path(CENTRAL_TOKEN);R=E/'reports';j=lambda p:json.loads(p.read_bytes());proof=j(R/'E1_WAVE35_EXPOSURE_OWN_ACTIVE_CPU_VERIFIED.json')
assert proof['passed'] and proof['actual_updates_observed']>0 and proof['active_startup_and_snapshot_only_not_formal_final']
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);scope=c['terrain_subexpert_revision004']['wave35_exposure_repair_next_scope'];assert scope['root']==proof['root'] and scope['source_count']==368
scope.update(own_same_G3_samecommand_full_CPU_CUDA_startup_verified=True,actual_PPO_update_snapshot=proof['actual_updates_observed'],actual_control_snapshot=proof['actual_PPO_controls'],own_active_CPU_report=str(R/'E1_WAVE35_EXPOSURE_OWN_ACTIVE_CPU_VERIFIED.json'),formal_final_pending=True,full_candidate142_behavior_pending=True)
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.WAVESTARTUP-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';before=p.read_bytes();msg='\n\nOwnWave368 active startup independently CPU-verified: sameG3/samecommand actorcriticoptimizerstd/allD0D7/globalnamed/dictprivateCPUCUDA/diskroundtrip/episode+1 exact. Actual saved snapshot '+str(proof['actual_updates_observed'])+' PPO updates/'+str(proof['actual_PPO_controls'])+' controls, changedactor '+str(proof['actor_changed_tensor_count'])+' tensors and optimizerstepdelta '+str(proof['optimizer_step_delta'])+' prove actual learning. This is an active snapshot, notformal-final orqualifiedWave. First health receipt event/600-control cadence can be pending; originalreader premature required-file failure retained and independent schema reader fixed onlyreadcontract. Formal1800s originalparent unique save/exit and complete142 fourcase stillrequired. HourlyACTIVE sameheartbeat actually verified; allnewreports/source/errors/sync/receipts Git stage+supplement required.\n'
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.WAVESTARTUP-'+str(time.time_ns()));tmp.write_bytes(before+msg.encode());os.replace(tmp,p)
assert all((R/name).read_bytes()==raw for name,raw in protected.items())
v=dict(epoch=time.time(),metadata_synced=True,root=proof['root'],own_startup_report=str(R/'E1_WAVE35_EXPOSURE_OWN_ACTIVE_CPU_VERIFIED.json'),actual_PPO_update_snapshot=proof['actual_updates_observed'],formal_final_pending=True,master_approval_tracks_RM_bytes_exact=True,no_training_or_canonical_write=True)
p=R/'E1_WAVE35_EXPOSURE_STARTUP_METADATA_SYNCED.json';assert not p.exists();p.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CENTRAL_TOKEN',repr(io.E))
  save('WAVE_STARTUP_METADATA_SYNCED.json',run(n,code))
  print(json.dumps(dict(monitor_verified=True,active_reports_collected=len(v['entries']),startup_synced=True,formal_final=False)))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE_ACTIVE_EVIDENCE_CLOSE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True));raise
