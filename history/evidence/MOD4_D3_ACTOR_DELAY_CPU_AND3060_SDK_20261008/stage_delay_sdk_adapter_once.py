"""Isolated adapter preparation while production continues; no training authority."""
from pathlib import Path
import json, sys, shlex
D = Path(__file__).resolve().parent
R = D / 'reports';R.mkdir(exist_ok=True)
ROOT = '/home/egde/rl_candidates/MOD4_D3_ACTOR_DELAY_SDK_PREPARE_20261008'
assert not (R / 'ADAPTER_CPU_PASSED.json').exists()
sys.path.insert(0, str(D.parent / 'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c = connect()
try:
    code = r'''
from pathlib import Path
import json,hashlib,shutil,time
OLD=Path('/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007')
D=Path('/home/egde/rl_candidates/MOD4_D3_ACTOR_DELAY_SDK_PREPARE_20261008')
assert not D.exists()
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==218
D.mkdir();(D/'reports').mkdir()
for name,digest in f.items():
 p=OLD/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,name
 dest=D/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
component=Path('/home/egde/rl_candidates/MOD4_D3_DELAY_COMPONENT_PREPARE_20261007')
proof=json.loads((component/'reports/CPU_PASSED.json').read_text()) if (component/'reports/CPU_PASSED.json').exists() else None
math=component/'feedback_delay_mild.py';assert math.is_file()
shutil.copyfile(math,D/'isaac/mod4/feedback_delay_mild.py')
(D/'reports/ORIGINAL218_AND_MATH_REUSED.json').write_text(json.dumps(dict(epoch=time.time(),old_root=str(OLD),original218=f,math_path=str(math),math_sha256=hashlib.sha256(math.read_bytes()).hexdigest(),old_component_CPU_proof=proof,no_PPO_or_GPU_or_canonical_write=True),indent=2))
print('Isolated218 source copy plus original D3 math completed')
'''
    _, out, err = c.exec_command('/usr/bin/python3 -c ' + shlex.quote(code), timeout=30)
    raw, errors = out.read(), err.read()
    assert out.channel.recv_exit_status() == 0, (raw + errors).decode()
    with c.open_sftp() as ftp:
        for name in ('feedback_delay_runtime.py', 'test_delay_actor_boundary_cpu.py'):
            ftp.put(str(D / name), ROOT + '/isaac/mod4/' + name)
    code = r'''
from pathlib import Path
import json,hashlib,subprocess,time,sys
D=Path('/home/egde/rl_candidates/MOD4_D3_ACTOR_DELAY_SDK_PREPARE_20261008');R=D/'reports';C=D/'isaac/mod4'
old=json.loads((R/'ORIGINAL218_AND_MATH_REUSED.json').read_text());f=old['original218'].copy()
for name in ('feedback_delay_mild.py','feedback_delay_runtime.py','test_delay_actor_boundary_cpu.py'):
 p=C/name;compile(p.read_text(),str(p),'exec');f['isaac/mod4/'+name]=hashlib.sha256(p.read_bytes()).hexdigest()
assert len(f)==221
for name,digest in f.items():assert hashlib.sha256((D/name).read_bytes()).hexdigest()==digest,name
res=subprocess.run([sys.executable,str(C/'test_delay_actor_boundary_cpu.py')],cwd=C,capture_output=True,text=True)
assert res.returncode==0,res.stdout+res.stderr
v=json.loads(res.stdout);assert v['passed'] and v['no_CUDA_initialized'] and not v['actual_SDK'] and not v['PPO_deployed']
(R/'SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=f,original218_exact=True),indent=2))
(R/'ADAPTER_CPU_PASSED.json').write_text(json.dumps(dict(epoch=time.time(),CPU=v,old_D3_math_exact_reused=True,source_count=221,production_runtime_unchanged=True,scope='Adapter CPU fixture only; next immutable3060 SDK is not yet launched',copied_training_entries_forbidden=True),indent=2))
print(json.dumps(json.loads((R/'ADAPTER_CPU_PASSED.json').read_text())))
'''
    _, out, err = c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c ' + shlex.quote(code), timeout=45)
    raw, errors = out.read(), err.read()
    assert out.channel.recv_exit_status() == 0, (raw + errors).decode()
    value = json.loads(raw)
    with c.open_sftp() as ftp:
        for name in ('ADAPTER_CPU_PASSED.json', 'SOURCE_FREEZE.json', 'ORIGINAL218_AND_MATH_REUSED.json'):
            ftp.get(ROOT + '/reports/' + name, str(R / name))
    print(json.dumps(value))
finally:
    c.close()
