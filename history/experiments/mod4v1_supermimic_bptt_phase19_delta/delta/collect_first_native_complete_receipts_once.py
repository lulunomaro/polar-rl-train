"""One bounded first-save purpose, distinct from ongoing counter/close watcher.
Read only E0/E2 producer latest_complete receipts; never PT/modelstat/raw/SDK/C.
"""
from pathlib import Path
import json,sys,time,datetime
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
out=R/'reports/FIRST_E0_E2_NATIVE_COMPLETE_CHECKPOINT_RECEIPTS_V1.json';start=R/'reports/FIRST_E0_E2_NATIVE_COMPLETE_RECEIPT_WATCH_STARTED_V1.json';assert not out.exists()and not start.exists()
m=json.loads((R/'SUPERMIMIC_EIGHT_V1_DISPATCH_ONCE.json').read_bytes());root=m['root'];start.write_text(json.dumps(dict(root=root,started_local=datetime.datetime.now().astimezone().isoformat(),cap_seconds=900,interval_seconds=20,purpose='First producer fullsave metadata only, not a duplicate counter/close observer',PT_stat_read_raw_SDK_C_ops=0),indent=2),encoding='utf-8');c=connect72();s=c.open_sftp();deadline=time.monotonic()+900;rows={}
def get(rel):
 try:
  with s.open(root+'/'+rel,'rb')as f:return json.loads(f.read())
 except FileNotFoundError:return None
try:
 while time.monotonic()<deadline:
  for role in ('E0','E2'):
   if role in rows:continue
   base='roles/'+role+'/production/';error=get(base+'WORKER_ERROR.json')
   if error:
    out.write_text(json.dumps(dict(kind='FIRST_NATIVE_SAVE_WORKER_ERROR_PRESERVED',root=root,role=role,error=error,already_saved_receipts=rows),indent=2),encoding='utf-8');raise RuntimeError('Actual worker error before first-save receipt; native unchanged retry prohibited')
   value=get(base+'latest_complete.json')
   if value:
    assert value['full_new_model_critic_aux_optimizers_replay_RNG_hist_saved']and value['teacher_unchanged']and value['counts']['pi_bptt_optimizer_steps']>0
    assert value['bytes']>0 and len(value['SHA'])==64 and value['path'].startswith(root+'/roles/'+role+'/production/checkpoints/')
    rows[role]=value;print('FIRST_ACTUAL_NATIVE_COMPLETE '+json.dumps(dict(role=role,checkpoint=value)),flush=True)
  if len(rows)==2:
   result=dict(kind='ACTUAL_NATIVE_PRODUCER_COMPLETE_SAVE_RECEIPTS_NOT_SKILL_PASS',root=root,epoch=time.time(),receipts=rows,producer_checkpoint_SHA_not_reopened=True,PT_stat_read_raw_SDK_C_ops=0,windows_not_yet_closed=True)
   out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(out,flush=True);break
  time.sleep(20)
 else:
  out.write_text(json.dumps(dict(kind='FIRST_SAVE_RECEIPT_WATCH_TIMEOUT_NOT_PHYSICS_FAILURE',root=root,receipts=rows,original_workers_not_killed=True,PT_stat_read_raw_SDK_C_ops=0),indent=2),encoding='utf-8');raise TimeoutError('First producer receipt window900expired; own workers untouched')
finally:s.close();c.close()
