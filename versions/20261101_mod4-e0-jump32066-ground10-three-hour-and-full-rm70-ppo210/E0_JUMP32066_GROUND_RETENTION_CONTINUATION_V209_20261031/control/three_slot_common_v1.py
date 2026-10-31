from pathlib import Path
import os,time,json,hashlib,hmac,subprocess,fcntl
B=Path(__file__).resolve().parent
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
LOCKS=(C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock')
PORT=29754
SCHEDULE=json.loads((B/'SCHEDULE_PUBLIC.json').read_bytes())
CAPS={key:spec['max_parent_seconds'] for key,spec in SCHEDULE['experts'].items()}
GPUS={key:spec['GPU_UUID'] for key,spec in SCHEDULE['experts'].items()}

def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)

def read(p):return json.loads(Path(p).read_bytes()) if Path(p).is_file() else None

def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def ident(pid):
 import psutil
 try:p=psutil.Process(pid);return dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd())
 except psutil.Error:return None

def terminal(row):return bool(row.get('terminal_all_own_children_waited') and row.get('returncode') is not None)

def authenticated_row(raw,signature,token,run_id,specs,now):
 assert 0<len(raw)<3000000 and hmac.compare_digest(signature,hmac.new(token,raw,hashlib.sha256).hexdigest());v=json.loads(raw);assert v['run_id']==run_id and abs(v['epoch']-now)<60;row=v['row'];key=row['key'];assert key in specs and row.get('manifest_SHA')==specs[key]['manifest_SHA'];return key,row

def charge_values(c,a,go,rows,now):
 for key,g in go.items():
  x=a['experts'].setdefault(key,dict(started_epoch=g['learning_started_epoch'],accounted_through_epoch=g['learning_started_epoch'],charged_seconds=0.,max_parent_seconds=g['max_parent_seconds']))
  row=rows.get(key) or {};end=row.get('owner_received_terminal_epoch',now) if terminal(row) else now;end=max(end,x['accounted_through_epoch']);dt=end-x['accounted_through_epoch'];assert dt>=0;x['charged_seconds']+=dt;x['accounted_through_epoch']=end;c['charged_training_seconds']+=dt;c['remaining_training_seconds']-=dt;a['charged_expert_seconds']+=dt
  if terminal(row):x.update(ended_epoch=end,actual_returncode=row['returncode'],duration_bound_passed=x['charged_seconds']<=g['max_parent_seconds'])
 a['accounted_through_epoch']=now;assert abs(c['charged_training_seconds']+c['remaining_training_seconds']-2268000)<1e-5;return c,a

def valid_ready(row,spec):
 from owner209_protocol import valid_ready
 return valid_ready(row,spec)
