from pathlib import Path
import sys,shlex,json
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
code=r'''
from pathlib import Path
import sys,json,re,time
D=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_PRACTICAL_REVIEW_20261007');sys.path.insert(0,str(D));import continue_clock2000_practical_review_once as q
rows=[]
for p in sorted((q.P/'reports').glob('*clock*discard*_receipt.json')):
 v=q.w.read(p);ck=Path(v['discarded_weights']['path']);m=q.w.read(ck.parent/'run_manifest.json')
 if m['env'].get('RM_PHYSICS_DT_S')=='0.002' and m['init_checkpoint_sha256']==q.SHA:
  health=q.w.read(ck.parent/'CLOCK_TRAINING_HEALTH.json');log=q.P/(p.name.removesuffix('_receipt.json')+'.log');txt=log.read_text(errors='replace')
  times=[float(x) for x in re.findall(r'Iteration time:\s*([0-9.]+)s',txt)]
  rows.append(dict(receipt=str(p),receipt_sha256=q.base.sha(p),checkpoint=q.base.checkpoint(ck),run_manifest_sha256=q.base.sha(ck.parent/'run_manifest.json'),health=health,
   actual_iteration_times_s=times,policy_steps_per_s=m['num_envs']*24*len(times)/sum(times) if times else None,complete_receipt=v,preflight_weights_discarded=True))
print(json.dumps(dict(epoch=time.time(),rows=rows,budget=q.base.budget_state())))
'''
c=connect()
try:
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode();v=json.loads(raw)
 (R/'DT2000_PPO_HEALTH_EVIDENCE.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=v['epoch'],rows=[{k:r[k] for k in ['receipt','checkpoint','health','actual_iteration_times_s','policy_steps_per_s']} for r in v['rows']])))
finally:c.close()
