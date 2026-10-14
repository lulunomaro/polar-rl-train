"""Start only the originally approved first bounded S4 learning parent."""
from pathlib import Path
import sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=D/'S4_FIRST_FORMAL_TARGET_CPU_ACTUAL.json';cpu=json.loads(p.read_bytes())
 assert cpu['passed'] and cpu['source_CPU_complete'] and cpu['closed_native_and_zero_fullrestore_CPU_admitted'] and cpu['duration_seconds']==2700
 root=cpu['root'];c=None;stamp=str(time.time_ns())
 code='''from pathlib import Path
import os,sys,json,time,hashlib,subprocess,psutil,fcntl,shutil
r=Path('''+repr(root)+''');cpu=r/'S4_FIRST_FORMAL_TARGET_CPU_ACTUAL.json';assert hashlib.sha256(cpu.read_bytes()).hexdigest()=='''+repr(sha(p))+'''
d=json.loads(cpu.read_bytes());assert d['passed'] and d['source_CPU_complete'] and d['closed_native_and_zero_fullrestore_CPU_admitted']
assert not (r/'ROOT_FIRST_GATE_DISPATCH_INTENT.json').exists() and not (r/'PARENT_IDENTITY_ACTUAL.json').exists()
sys.path.insert(0,str(r));from s4_first_supported_gate_formal_parent_v2 import LOCKS,budget_guard
for path in LOCKS:
 with path.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
budget_guard()
assert psutil.virtual_memory().available>=55000000000 and shutil.disk_usage(r).free>=30000000000
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
for name,h in d['sourcefreeze'].items():assert hashlib.sha256((r/name).read_bytes()).hexdigest()==h
assert hashlib.sha256(Path(d['source_path']).read_bytes()).hexdigest()==d['source_SHA']
intent=dict(epoch=time.time(),first_S4_gate_window_seconds=2700,source_SHA=d['source_SHA'],original005_budget_only=True,no_automatic_next_gate_block=True,own_startup_must_admit_before_PPO=True)
with (r/'ROOT_FIRST_GATE_DISPATCH_INTENT.json').open('x') as f:json.dump(intent,f);f.flush();os.fsync(f.fileno())
argv=[sys.executable,'-u',str(r/'s4_first_supported_gate_formal_parent_v2.py')]
with (r/'parent_stdout.log').open('xb') as f:p=subprocess.Popen(argv,cwd=r,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
q=psutil.Process(p.pid);out=dict(epoch=time.time(),root=str(r),parent=dict(pid=q.pid,created=q.create_time(),argv=q.cmdline(),cwd=q.cwd()),source_SHA=d['source_SHA'],first_bounded_gate_only=True,startup_or_dispatch_is_not_PPO_save_proof=True)
with (r/'ROOT_FIRST_GATE_DISPATCH_ACTUAL.json').open('x') as f:json.dump(out,f,indent=2);f.flush();os.fsync(f.fileno())
print(json.dumps(out))
'''
 try:
  c=t.connect();si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
  p=D/'reports'/('S4_FIRST_GATE_UNIQUE_DISPATCH_TRANSPORT_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_retry=True),indent=2));assert rc==0,str(p)
  out=json.loads(raw);p=D/'reports'/('S4_FIRST_GATE_UNIQUE_DISPATCH_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(out,indent=2));print(json.dumps(dict(report=str(p),root=root,parent=out['parent'],source_SHA=out['source_SHA'])))
 except BaseException:
  (D/'reports'/('S4_FIRST_GATE_DISPATCH_ORIGINAL_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),unknown_mutation_requires_read_not_retry=True)),encoding='utf8');raise
 finally:t.close(c)
if __name__=='__main__':main()
