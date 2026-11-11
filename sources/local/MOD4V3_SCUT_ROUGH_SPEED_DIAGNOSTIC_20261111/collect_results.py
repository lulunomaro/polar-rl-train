"""Collect both finite replay jobs and summarize direct velocity errors."""
from pathlib import Path
import sys,json,hashlib
b=Path(__file__).resolve().parent;plan=json.loads((b/'PLAN.json').read_text());sys.path.insert(0,r'D:/claude2/fangzhen/tmp');from step7_remote_access import connect
c=connect();s=c.open_sftp();remote=plan['diagnostic_remote'];allrows=[];index=[]
try:
 for level in (0,3):
  job=f'paired_speed_level{level}_r1';local=b/'evidence'/job;local.mkdir(exist_ok=True)
  for name in ['SPEED_RESULT.json','RESULT.json','SAFE_CLOSED.json','INITIAL_DR.json','PROGRESS.json']:
   with s.open(remote+'/'+job+'/'+name,'rb') as f:raw=f.read()
   (local/name).write_bytes(raw)
  for name in [job+'_LAUNCH.json',job+'.log']:
   with s.open(remote+'/'+name,'rb') as f:raw=f.read()
   (b/'evidence'/name).write_bytes(raw)
  value=json.loads((local/'SPEED_RESULT.json').read_bytes());result=json.loads((local/'RESULT.json').read_bytes())
  assert json.loads((local/'SAFE_CLOSED.json').read_bytes())['result']
  assert result['input_sha256']==plan['models_sha256']
  for row in value['rows']:
   if row['task']=='all':allrows.append(row)
  with s.open(remote+'/'+job+'/trajectory.npz','rb') as f:raw=f.read()
  # Exact raw endpoints are compact enough to preserve for subsequent read-only analysis.
  (local/'trajectory.npz').write_bytes(raw);index.append(dict(path=(local/'trajectory.npz').relative_to(b).as_posix(),remote=remote+'/'+job+'/trajectory.npz',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
 summary=dict(protocol=json.loads((b/'evidence/paired_speed_level0_r1/SPEED_RESULT.json').read_bytes())['protocol'],rows=allrows,raw_index=index)
 (b/'evidence/SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps([dict(level=x['level'],model=x['model'],variant=x['variant'],MAE=x['steady_pre_push']['scut_horizontal_vx'].get('MAE'),RMSE=x['steady_pre_push']['scut_horizontal_vx'].get('RMSE'),eligible=x['steady_pre_push']['scut_horizontal_vx']['eligible_envs'],completed=x['steady_pre_push']['scut_horizontal_vx']['completed_window_count'],first_term=x['first_terminal_failures'],first_timeout=x['first_timeouts']) for x in allrows],ensure_ascii=False,indent=2))
finally:s.close();c.close()
