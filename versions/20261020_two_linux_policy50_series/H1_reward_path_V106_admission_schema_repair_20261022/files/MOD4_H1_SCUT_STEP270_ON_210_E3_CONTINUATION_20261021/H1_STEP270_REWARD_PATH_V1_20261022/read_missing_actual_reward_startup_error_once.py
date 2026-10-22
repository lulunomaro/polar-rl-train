from pathlib import Path
import importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports';N=T/'H1_STEP270_E3_REWARD_PATH_PAIR_V17_20261022'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import json,psutil,time
q=v['q'];owner=Path(q['owner_root']);root=Path(q['roots']['h1']);texts={}
for base in (owner,root):
 for p in base.rglob('*'):
  if p.is_file() and p.suffix in ('.json','.log') and '__pycache__' not in p.parts:
   if p.suffix=='.json' and ('INDEX' not in p.name and 'MANIFEST' not in p.name and 'QUALIFIED_RUNTIME_BASE' not in p.name):texts[str(p)]=p.read_text('utf8')
   elif p.suffix=='.log':
    lines=p.read_text('utf8',errors='replace').splitlines()
    table=[x for x in lines if '|' in x and any(k in x for k in ('h1_step270_','h1_control_events','h1_scut_fudan_air_wheel_zero_torque','h1_scut_fudan_leg_tuck','h1_scut_fudan_wheel_below_base'))]
    texts[str(p)]='\n'.join(table+lines[-200:])
processes=[]
for p in psutil.process_iter(['pid','exe','cmdline','create_time']):
 try:
  if any(x.startswith((str(owner)+'/',str(root)+'/')) for x in p.info['cmdline'] or []):processes.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),texts=texts,actual_processes=processes,no_wait_loop_no_PT_GPU_or_account_change=True)))
'''
try:
 q=json.loads((N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());c=d.t.connect()
 try:v=d.code(c,d.t.PY,CODE,dict(q=q),timeout=60)
 finally:c.close()
 put('ACTUAL_REWARD_STARTUP_CURRENT_AND_ORIGINAL_ERROR_TEXT_ACTUAL.json',v)
 for path,text in v['texts'].items():
  if path.endswith(('OWNER_CURRENT.json','production_WORKER.log','NODE_TERMINAL_ACTUAL.json','production_APP.log')):print(path,text[-12000:])
except BaseException:
 put('ACTUAL_REWARD_STARTUP_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
