"""Authorize only the two actually missing zero-PPO integration cases."""
from pathlib import Path
import sys,json,hashlib,time,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    receipt=D/'S4_ZERO_FULLSAVE_HEALTH_V3_TARGET_CPU_ACTUAL.json';v=json.loads(receipt.read_bytes())
    assert v['passed'] is True and v['approved_PPO'] is False and v['original522_runtime_assets_byteexact'] is True
    root=v['target_root'];stamp=str(time.time_ns());c=None
    code='''from pathlib import Path
import sys,json,hashlib,subprocess,os,time,psutil
r=Path('''+repr(root)+''');p=r/'S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='''+repr(sha(receipt))+'''
v=json.loads(p.read_bytes());assert v['passed'] is True and v['approved_PPO'] is False
assert not (r/'GPU_FIXED_TWO_DISPATCH_INTENT.json').exists() and not (r/'PARENT_IDENTITY_ACTUAL.json').exists()
sys.path.insert(0,str(r));from s4_missing_zero_fullsave_parent_v3 import LOCKS,guard
import fcntl
for path in LOCKS:
 with path.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
resources=guard()
for name,h in v['active_files'].items():assert hashlib.sha256((r/name).read_bytes()).hexdigest()==h
intent=dict(epoch=time.time(),cases=['own_first_fullsave0_healthschema','own_fullrestore0_healthschema'],PPO_updates_authorized=0,source_SHA=v['refs'][1]['sha256'],target_CPU_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),no_retry_signal_or_budget_write=True)
with (r/'GPU_FIXED_TWO_DISPATCH_INTENT.json').open('x') as f:json.dump(intent,f);f.flush();os.fsync(f.fileno())
argv=[sys.executable,'-u',str(r/'s4_missing_zero_fullsave_parent_v3.py')]
with (r/'parent_stdout.log').open('xb') as f:proc=subprocess.Popen(argv,cwd=r,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
q=psutil.Process(proc.pid);out=dict(epoch=time.time(),parent=dict(pid=proc.pid,created=q.create_time(),argv=q.cmdline(),cwd=q.cwd()),root=str(r),resources=resources,fixed_two_missing_cases_only=True,PPO_updates_authorized=0)
with (r/'ROOT_GPU_FIXED_TWO_DISPATCH_ACTUAL.json').open('x') as f:json.dump(out,f,indent=2);f.flush();os.fsync(f.fileno())
print(json.dumps(out))
'''
    try:
        c=t.connect();si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
        p=D/'reports'/('S4_ZERO_FULLSAVE_HEALTH_V3_UNIQUE_DISPATCH_TRANSPORT_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_retry=True),indent=2),encoding='utf8');assert rc==0,str(p)
        out=json.loads(raw);p=D/'reports'/('S4_ZERO_FULLSAVE_HEALTH_V3_UNIQUE_DISPATCH_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(out,indent=2),encoding='utf8')
        print(json.dumps(dict(report=str(p),root=out['root'],parent=out['parent'],PPO_updates_authorized=0)))
    except Exception:
        (D/'reports'/('S4_FIXED_TWO_DISPATCH_ORIGINAL_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),do_not_retry_unknown_mutation=True)),encoding='utf8');raise
    finally:t.close(c)
if __name__=='__main__':main()
