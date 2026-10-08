"""Add the isolated SDK adapter and its CPU fixture; no Isaac/GPU launch."""
from pathlib import Path
import sys,json,time,hashlib,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert (R/'D4_COMPONENT_CPU_PASSED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
root='/home/egde/rl_candidates/MOD4_D4_ACTION_QUEUE_COMPONENT_PREPARE_20261008';c=connect()
try:
    with c.open_sftp() as f:
        for n in ['action_delay_sdk_adapter.py','test_action_delay_adapter_cpu.py']:
            try:f.stat(root+'/'+n)
            except FileNotFoundError:pass
            else:raise AssertionError('Adapter stage already exists; no repeated once')
            f.put(str(D/n),root+'/'+n)
    code='import os,runpy;os.chdir('+repr(root)+');runpy.run_path("test_action_delay_adapter_cpu.py",run_name="__main__")'
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30)
    raw=o.read();err=e.read();exitcode=o.channel.recv_exit_status()
    (R/'ADAPTER_CPU_FIRST_STDOUT.txt').write_bytes(raw);(R/'ADAPTER_CPU_FIRST_STDERR.txt').write_bytes(err)
    with c.open_sftp() as f:
        f.open(root+'/reports/ADAPTER_CPU_FIRST_STDOUT.txt','wb').write(raw);f.open(root+'/reports/ADAPTER_CPU_FIRST_STDERR.txt','wb').write(err)
    assert exitcode==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);assert v['passed'] and v['torch_version'].startswith('2.10.') and not v['actual_SDK']
    v.update(epoch=time.time(),source_sha256={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ['action_delay_sdk_adapter.py','test_action_delay_adapter_cpu.py','action_delay_physics_queue.py']})
    output=json.dumps(v,indent=2).encode();(R/'D4_ADAPTER_CPU_PASSED.json').write_bytes(output)
    with c.open_sftp() as f:f.open(root+'/reports/D4_ADAPTER_CPU_PASSED.json','wb').write(output)
    print(json.dumps(v))
finally:c.close()
