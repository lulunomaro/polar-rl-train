"""Read closed zero-control health, typed restore receipts and error, not GPU replay."""
from pathlib import Path
import sys,json,time,shlex
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_LOGGER_V2_20261015'
def main():
 c=None;stamp=str(time.time_ns())
 try:
  c=t.connect();code='''from pathlib import Path
import json,time,hashlib,psutil
r=Path('''+repr(ROOT)+''');a=r/'own_first_fullsave0_loggerfix/attempt';parent=json.loads((r/'PARENT_IDENTITY_ACTUAL.json').read_bytes());assert not psutil.pid_exists(parent['pid'])
rows=[]
for p in sorted(a.glob('*')):
 if p.is_file() and p.suffix in ('.json','.log'):
  raw=p.read_bytes();rows.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),root=str(r),files=rows,original_parent_error=json.loads((r/'PIPELINE_ORIGINAL_ERROR.json').read_bytes()),original_parent_exit=json.loads((r/'PARENT_EXIT_ACTUAL.json').read_bytes()),actual_parent_absent=True)))
'''
  si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
  p=D/'reports'/('S4_ZERO_HEALTH0_SCHEMA_TRANSPORT_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace')),indent=2));assert rc==0
  v=json.loads(raw);p=D/'reports'/('S4_ZERO_HEALTH0_ORIGINAL_CLOSED_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(v,indent=2))
  h=json.loads(next(row['text'] for row in v['files'] if row['path'].endswith('/CLOCK_TRAINING_HEALTH.json')))
  print(json.dumps(dict(report=str(p),health=h)))
 finally:t.close(c)
if __name__=='__main__':main()
