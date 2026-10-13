from pathlib import Path
import sys,os,json,time,base64,traceback
D=Path(__file__).resolve().parent;W=D.parent
CODE=r'''
from pathlib import Path
import psutil,time,json,hashlib,ast,subprocess
pid=24856;created=1791299198.2378356
p=psutil.Process(pid);assert abs(p.create_time()-created)<.001
script=Path('D:/claude2/fangzhen/runs3060/flat_scratch_v1/monitor/mirror_target_tui.py')
assert any(str(script).replace('\\','/').lower()==v.replace('\\','/').lower() for v in p.cmdline())
raw=script.read_bytes();tree=ast.parse(raw.decode('utf8-sig'))
network_calls=[]
for n in ast.walk(tree):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('connect','sleep','exec_command','open_sftp','close'):
  row=dict(line=n.lineno,call=n.func.attr,keyword_names=[v.arg for v in n.keywords])
  if n.func.attr=='connect':
   for kw in n.keywords:
    if kw.arg in ('hostname','username','port','timeout','banner_timeout','auth_timeout') and isinstance(kw.value,ast.Constant):row[kw.arg]=kw.value.value
   if n.args and isinstance(n.args[0],ast.Constant):row['first_host_arg']=n.args[0].value
  if n.func.attr=='sleep' and n.args and isinstance(n.args[0],ast.Constant):row['duration']=n.args[0].value
  network_calls.append(row)
parents=[]
for q in p.parents()[:5]:
 parents.append(dict(pid=q.pid,creation=q.create_time(),name=q.name(),exe=q.exe(),argv=q.cmdline()))
children=[dict(pid=q.pid,creation=q.create_time(),name=q.name(),exe=q.exe(),argv=q.cmdline()) for q in p.children(recursive=True)]
ps=r"Get-ScheduledTask | Where-Object { ($_.Actions.Arguments -join ' ') -match 'mirror_target_tui|flat_scratch_v1.*monitor' } | ForEach-Object { [pscustomobject]@{TaskName=$_.TaskName;TaskPath=$_.TaskPath;State=[string]$_.State;Arguments=($_.Actions.Arguments -join ' ');Execute=($_.Actions.Execute -join ' ')} } | ConvertTo-Json -Depth 4 -Compress"
r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',ps],capture_output=True)
tasks=json.loads(r.stdout.decode('utf8-sig')) if r.stdout.strip() else []
conn=[c for c in p.net_connections(kind='tcp') if c.raddr and c.raddr.ip=='10.24.4.210']
print(json.dumps(dict(epoch=time.time(),PID=pid,creation=p.create_time(),argv=p.cmdline(),script_path=str(script),source_size_bytes=len(raw),source_sha256=hashlib.sha256(raw).hexdigest(),open_connections_to_210=len(conn),network_calls=network_calls,children=children,parents=parents,matching_scheduled_tasks=tasks,read_only=True,no_credentials_or_environment_collected=True)))
'''
def main():
 stamp=str(time.time_ns())
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
 from reuse_authorized_session_transport import recover
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
 sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
 from eval_remote_io import connect_eval
 c=connect_eval()
 try:
  enc=base64.b64encode(CODE.encode()).decode();cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
  _,o,e=c.exec_command(cmd,timeout=45);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:raise RuntimeError('Mirror owner readonly returned '+str(rc)+': '+err.decode('utf8','replace'))
  a=json.loads(raw);p=D/'reports'/('3060_MIRROR_CONNECTION_OWNER_READONLY_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(a,ensure_ascii=False))
 except Exception:
  (D/'reports'/('3060_MIRROR_OWNER_READER_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_action=True)),encoding='utf8');raise
 finally:c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':main()
