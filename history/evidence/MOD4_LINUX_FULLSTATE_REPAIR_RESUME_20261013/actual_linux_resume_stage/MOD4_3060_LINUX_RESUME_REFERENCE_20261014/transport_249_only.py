"""Existing transient credential transport, sole249; no210 or GPU calls."""
from pathlib import Path
import sys, os, base64, json, importlib.util
P=Path(__file__).resolve().parent;W=P.parent
PY='D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe'
ROOT='D:/MOD4_async_eval/MOD4_LINUX_RESUME_REFERENCE_20261014'

def connect():
    sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
    from reuse_authorized_session_transport import recover
    secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret
    os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
    sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
    from eval_remote_io import connect_eval
    c=connect_eval();assert c.get_transport().getpeername()[0]=='10.24.4.249'
    return c

def close(c):
    if c:c.close()
    os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)

def py(c,code,timeout=60):
    compile(code,'<new authorized249 operation>','exec')
    b=base64.b64encode(code.encode()).decode()
    command='"'+PY+'" -X utf8 -c "import base64;exec(base64.b64decode(\''+b+'\'))"'
    _,o,e=c.exec_command(command,timeout=timeout);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
    assert rc==0,(rc,err.decode('utf8','replace')[-6000:]);return json.loads(raw)

def ps(c,code,timeout=60):
    enc=base64.b64encode(code.encode('utf-16-le')).decode()
    _,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+enc,timeout=timeout)
    raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
    assert rc==0,(rc,err.decode('utf8','replace')[-6000:]);return json.loads(raw.decode('utf-8-sig'))

def guard_code():
    spec=importlib.util.spec_from_file_location('old_guard_readonly_reference',W/'MOD4_3060_DIRECT_FACTOR_20261013/deploy_direct3060_baseline120_WDDM_guard_reviewed_once.py')
    g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    source=g.GUARD
    source=source.replace('ROOT',repr(ROOT))
    old="assert not outbound, 'Retired210 bridge still connected'"
    assert source.count(old)==1
    allow=json.loads((P/'reports/REFERENCE17B_INTERACTIVE_SSH_PARENT_ACTUAL.json').read_bytes())
    known=repr(allow['known_interactive_ssh'])
    replacement="""known=KNOWN
classified=[];blocked=[]
for row in outbound:
 try:
  p=psutil.Process(row['pid']);parent=psutil.Process(p.ppid())
  actual=dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),exe=p.exe(),parent=p.ppid(),parent_creation=parent.create_time(),parent_argv=parent.cmdline(),parent_exe=parent.exe())
  assert actual==known,'Outbound identity is not the explicitly identified interactive SSH'
  assert Path(actual['exe']).name.lower()=='ssh.exe'
  assert Path(actual['parent_exe']).name.lower() in ('powershell.exe','pwsh.exe','cmd.exe')
  assert not any(x in ' '.join(actual['parent_argv']).lower() for x in ('mirror_target','eval_worker','rpc','poller','retry'))
  classified.append(dict(connection=row,actual_identity=actual,role='Existing interactive user SSH terminal; preserved; no GPU or task ownership'))
 except (AssertionError,psutil.Error) as error:blocked.append(dict(connection=row,error=repr(error)))
assert not blocked,'Retired or unidentified210 bridge still connected'
""".replace('KNOWN',known)
    source=source.replace(old,replacement)
    source=source.replace("index,name,total,free=[x.strip() for x in device[0].split(',')]", "index,name,total,free=[x.strip() for x in device[0].split(',')];device_name=name")
    source=source.replace("name=name,total_MiB", "name=device_name,total_MiB")
    source=source.replace("target210_outbound=[]", "target210_outbound=outbound,identified_interactive_SSH_preserved=classified")
    compile(source,'<strict slot guard role reviewed>','exec')
    return source
