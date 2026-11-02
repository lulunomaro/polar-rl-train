"""Observe this actual finite original-owner window; no model or ledger reads here."""
from pathlib import Path
import json,datetime
from project_connector import connect72
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--expected-root');args=parser.parse_args()
R=Path(__file__).resolve().parent;d=json.loads(sorted((R/'reports').glob('W35_adaptation_dispatch_*.json'))[-1].read_bytes());job=d['new_job'];assert args.expected_root is None or job==args.expected_root,'Do not silently observe another attempt';r={'job':job,'captured_local':datetime.datetime.now().astimezone().isoformat(),'files':{}}
c=connect72();s=c.open_sftp()
try:
 for rel in ('OWNER_STARTED.json','OWNER_ORIGINAL_ERROR.json','ACTUAL_CANONICAL_READ.json','ACTUAL_RESOURCE_LEASES.json','ROOT_ADMISSION_ACTUAL.json','READY_MOD4V1_ACTUAL.json','GO_PRODUCTION.json','WORKER_IDENTITY_BEFORE_WAIT.json','OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','production/FINAL.json','production/NATIVE24_W35_RM70_V3_ACTUAL.json','production/FIRST_ACTUAL_NEW_PPO_UPDATE.json','production/LATEST_PROGRESS.json','production/SOURCE208_V3_FINAL_READ_COUNTS.json','production/ORIGINAL_W35_RM70_V3_ERROR.json'):
  try:
   st=s.stat(job+'/'+rel)
   if st.st_size>3000000:r['files'][rel]={'bytes':st.st_size,'bounded_skip':True};continue
   with s.open(job+'/'+rel,'rb')as f:r['files'][rel]=json.loads(f.read())
  except FileNotFoundError:pass
 for rel in ('OWNER_CONSOLE.log','PPO_FULL_STDOUT_STDERR.log'):
  try:
   st=s.stat(job+'/'+rel)
   with s.open(job+'/'+rel,'rb')as f:f.seek(max(0,st.st_size-20000));text=f.read().decode('utf-8','replace')
   r['files'][rel]={'bytes':st.st_size,'tail_only':text}
  except FileNotFoundError:pass
 i,o,e=c.exec_command('nvidia-smi --query-gpu=index,uuid,memory.used,utilization.gpu --format=csv,noheader,nounits',timeout=30);i.close();r['GPU_now']={'stdout':o.read().decode(),'stderr':e.read().decode(),'rc':o.channel.recv_exit_status()}
finally:s.close();c.close()
p=R/'reports'/('W35_adaptation_snapshot_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps({k:v for k,v in r.items() if k!='files'},ensure_ascii=False,indent=2))
for k,v in r['files'].items():print(k,json.dumps(v,ensure_ascii=False) if not k.endswith('.log') else v['tail_only'][-4500:])
