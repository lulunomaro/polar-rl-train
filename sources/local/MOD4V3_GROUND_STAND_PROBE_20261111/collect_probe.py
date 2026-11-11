from pathlib import Path
import sys,json
ROOT=Path('D:/claude2/fangzhen');B=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tmp'));from step7_remote_access import connect
r=json.loads((B/'LAUNCH.json').read_text(encoding='utf-8'));c=connect();s=c.open_sftp();remote=r['remote']+'/test01'
for name in ['RESULT.json','SETTLED_STATES.npz','TRAJECTORIES.npz','SAFE_CLOSED.json','ERROR.txt']:
 try:
  s.stat(remote+'/'+name);target=B/(name+'.partial');s.get(remote+'/'+name,str(target));target.replace(B/name);print('FETCHED',name)
 except FileNotFoundError:pass
s.get(r['remote']+'/probe.log',str(B/'probe.log'))
if (B/'RESULT.json').exists():
 d=json.loads((B/'RESULT.json').read_text(encoding='utf-8'))
 for row in d['rows']:
  print(row['case'],row['variant'],'valid',row['valid_ground_start'],'success',row['success'],'rise_s',row['first_stable_interval_start_s'],'initial_h',round(row['settled_root_height_m'],4),'initial_support',round(row['settled_support_force_N'],2),'hard',row['first_hard_failure'])
else:
 print((B/'ERROR.txt').read_text(encoding='utf-8') if (B/'ERROR.txt').exists() else (B/'probe.log').read_text(encoding='utf-8',errors='replace')[-1600:])
s.close();c.close()
