from pathlib import Path
import json,sys,time
T=Path(__file__).resolve().parent;W=T.parent;N=T/'H1_STEP270_E3_REPAIR_PAIR_V3_20261022';R=N/'reports'
q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
c=d.t.connect()
try:
 v=d.code(c,d.t.PY,"""from pathlib import Path
import json,os,psutil,shutil,time
B=Path(v['root']);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
e=read(B/'NODE_EXIT_ACTUAL.json');assert e and e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired']
assert not any(p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
out=B/'job0/production';files={}
for p in out.rglob('*'):
 if p.is_file() and (p.name in ('FINAL.json','STOP_AFTER_SAVE.json','STOP_AFTER_SAVE','CLOCK_TRAINING_HEALTH.json','OWN_STORAGE_OR_UPDATE_BOUND_SAVED_STOP_ACTUAL.json','APP_CLOSING.json') or 'ORIGINAL_ERROR' in p.name):files[p.relative_to(B).as_posix()]=p.read_text('utf8','replace')
print(json.dumps(dict(epoch=time.time(),H1_actual_all_children_out=True,H1_node_exit=e,H1_node_terminal=read(B/'NODE_TERMINAL_ACTUAL.json'),H1_node_original_error=read(B/'NODE_ORIGINAL_ERROR.json'),actual_early_H1_complete_texts=files,durable_free_snapshot=shutil.disk_usage(B).free,owner_current=read(Path(v['owner'])/'OWNER_CURRENT.json'),only_H1_closed_slot_observation_not_cohort_closure=True,no_model_NPZ_download_or_GPU_or_account_write=True)))
""",dict(root=q['roots']['h1'],owner=q['owner_root']),timeout=45)
finally:c.close()
with (R/'H1_EARLY_COMPLETE_FINAL_AND_STOP_REASON_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(out=v['H1_actual_all_children_out'],files=v['actual_early_H1_complete_texts'],node_error=v['H1_node_original_error']),indent=2))
