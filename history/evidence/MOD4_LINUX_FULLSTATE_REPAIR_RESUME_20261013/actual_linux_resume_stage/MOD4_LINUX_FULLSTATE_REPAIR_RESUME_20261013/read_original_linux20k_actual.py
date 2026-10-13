"""Read current own state without starting GPU/PPO, signalling, or changing the ledger."""
from pathlib import Path
import json,time
from remote_session import execute
from deploy_original_linux20k_formal_once import S
src=r'''
from pathlib import Path
import json,subprocess,time,hashlib,fcntl
R=Path(S);row={}
for n in ['DISPATCH_RECEIPT.json','PARENT_IDENTITY.json','CURRENT_STAGE.json','ORIGINAL_PARENT_ERROR.json','ORIGINAL_LINUX_SAVED_REVIEW_READY.json','formal/DISPATCH_RECEIPT.json','formal/GUARDIAN_CURRENT.json','formal/EXIT_RECEIPT.json']:
 p=R/n;row[n]=json.loads(p.read_bytes()) if p.is_file() else None
for key in ('PARENT_IDENTITY.json','formal/DISPATCH_RECEIPT.json'):
 v=row[key]
 if v:
  v=v.get('child',v);p=Path('/proc')/str(v['pid']);row[key+'_actual']=dict(exists=p.exists(),argv=(p/'cmdline').read_bytes().replace(bytes([0]),b' ').decode() if p.exists() else None)
logs=list((R/'formal/learning_logs').glob('*')) if (R/'formal/learning_logs').exists() else []
row['own_logs']=[]
for p in logs:
 proof={}
 for q in p.glob('*STARTUP*VERIFIED.json'):proof[q.name]=json.loads(q.read_bytes())
 latest=p/'latest_complete.json';health=p/'CLOCK_TRAINING_HEALTH.json'
 row['own_logs'].append(dict(path=str(p),startup=proof,latest=json.loads(latest.read_bytes()) if latest.exists() else None,health=json.loads(health.read_bytes()) if health.exists() else None))
log=R/'formal/worker_stdout.log';parent=R/'parent_stdout.log'
row['stdout_tail']=log.read_bytes()[-16000:].decode(errors='replace') if log.exists() else None
row['parent_stdout_tail']=parent.read_bytes()[-4000:].decode(errors='replace') if parent.exists() else None
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');d=json.loads(B.read_bytes());row['canonical_budget']={k:d[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')}
row['compute']=subprocess.run(['nvidia-smi','--query-compute-apps=pid,used_memory,process_name','--format=csv,noheader'],capture_output=True,text=True).stdout
print(json.dumps(row))
'''
if __name__=='__main__':
    row,p=execute('S='+repr(S)+'\n'+src,'ORIGINAL_LINUX20K_CURRENT_ACTUAL',40)
    print(json.dumps(dict(receipt=str(p),parent=row['PARENT_IDENTITY.json_actual'] if 'PARENT_IDENTITY.json_actual' in row else row['parent_stdout_tail'],child=row.get('formal/DISPATCH_RECEIPT.json_actual'),own_logs=row['own_logs'],parent_error=row['ORIGINAL_PARENT_ERROR.json'],stdout_tail=row['stdout_tail'][-3500:] if row['stdout_tail'] else None),indent=2))
