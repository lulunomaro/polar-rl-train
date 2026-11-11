"""Compact read-only snapshot of this R0 job; no waiting or mutation on target."""
from pathlib import Path
import sys,json
ROOT=Path(r'D:/claude2/fangzhen');sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
TRIAL=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_ROUGH_R0_20261111'
PLAN=json.loads((TRIAL/'PLAN.json').read_text());REMOTE=PLAN['support'].rsplit('/support',1)[0]
c=connect();s=c.open_sftp()
try:
 for name in ('LATEST_PROGRESS.json','ERROR.json','FINAL.json','SAFE_CLOSED.json'):
  try:
   with s.open(REMOTE+'/train040m_rough_r0_r1/'+name) as f:d=json.loads(f.read().decode())
  except FileNotFoundError:continue
  if name=='LATEST_PROGRESS.json':
   t=d.get('terrain',{});print(json.dumps(dict(elapsed=d.get('training_elapsed_seconds'),iteration=d.get('iteration'),done=d.get('done_totals'),forward=d.get('forward_tracking'),levels=t.get('population_by_family_level'),up=t.get('level_up'),down=t.get('level_down')),ensure_ascii=False))
  else:print(name,json.dumps(d,ensure_ascii=False))
 for f in sorted((TRIAL/'evidence/training_round').glob('*_EVAL_SUMMARY.json')):
  d=json.loads(f.read_text(encoding='utf8'));print(d['checkpoint'],[(v['command'],round(v['vx_mean'],4),round(v['wz_mean'],4),round(v['height_mean'],4),v['passed'],v['resets']) for v in d['rows']])
 for name in ('paired_flat_final_r1','paired_rough_final_r1'):
  for f in ('PROGRESS.json','RESULT.json','ERROR.json','SAFE_CLOSED.json'):
   try:
    with s.open(REMOTE+'/'+name+'/'+f) as h:d=json.loads(h.read().decode())
   except FileNotFoundError:continue
   if f=='RESULT.json':print(name,f,'rows',len(d['rows']),'seconds',d['wall_seconds'])
   else:print(name,f,json.dumps(d,ensure_ascii=False))
finally:s.close();c.close()
