"""Stage only the isolated D4 math module and run the target Torch CPU fixtures."""
from pathlib import Path
import sys,json,time,hashlib,shlex
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
remote='/home/egde/rl_candidates/MOD4_D4_ACTION_QUEUE_COMPONENT_PREPARE_20261008'
names=['action_delay_physics_queue.py','test_action_delay_queue_cpu.py','reviewed_sources/manager_based_rl_env.py']
sha={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in names}
c=connect()
try:
    with c.open_sftp() as f:
        try:f.stat(remote)
        except FileNotFoundError:pass
        else:raise AssertionError('This isolated component stage already exists; do not rerun once')
        f.mkdir(remote);f.mkdir(remote+'/reports');f.mkdir(remote+'/reviewed_sources')
        for n in names:
            f.put(str(D/n),remote+'/'+n)
            assert hashlib.sha256(f.open(remote+'/'+n).read()).hexdigest()==sha[n]
        work=dict(epoch=time.time(),scope='CPU-only component preparation, not D4 SDK or learning',source_sha256=sha,approved_plan='MOD4-MOE-PLAN-001 v1.5',approved_plan_sha256='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b',production234_changed=False,GPU_authority=False,PPO_authority=False,canonical_write_authority=False,actual_candidate_delay_us=[0,2500,5000],future_required=['actual SDK target application and timing/reset readback','full queue/RNG save and new physical episode restore','20k callback/parameter/physics readback','new range full PPO with discarded weights','explicit saved boundary D4 executor'])
        raw=json.dumps(work,indent=2).encode();f.open(remote+'/reports/COMPONENT_WORK_ORDER.json','wb').write(raw)
    code='import runpy,os;os.chdir('+repr(remote)+');runpy.run_path("test_action_delay_queue_cpu.py",run_name="__main__")'
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45)
    raw=o.read();err=e.read();exitcode=o.channel.recv_exit_status()
    (R/'CPU_COMPONENT_FIRST_STDOUT.txt').write_bytes(raw);(R/'CPU_COMPONENT_FIRST_STDERR.txt').write_bytes(err)
    first=dict(epoch=time.time(),exit_code=exitcode,source_sha256=sha,stdout_sha256=hashlib.sha256(raw).hexdigest(),stderr_sha256=hashlib.sha256(err).hexdigest())
    (R/'CPU_COMPONENT_FIRST_EXECUTION.json').write_text(json.dumps(first,indent=2),encoding='utf8')
    with c.open_sftp() as f:
        for n,b in [('CPU_COMPONENT_FIRST_STDOUT.txt',raw),('CPU_COMPONENT_FIRST_STDERR.txt',err),('CPU_COMPONENT_FIRST_EXECUTION.json',json.dumps(first,indent=2).encode())]:f.open(remote+'/reports/'+n,'wb').write(b)
    assert exitcode==0,(raw+err).decode(errors='replace')
    proof=json.loads(raw);assert proof['passed'] and proof['torch_version'].startswith('2.10.') and proof['no_CUDA_initialized']
    proof.update(remote_root=remote,epoch=time.time(),component_source_sha256=sha,not_SDK_or_learning=True)
    output=json.dumps(proof,indent=2).encode()
    (R/'D4_COMPONENT_CPU_PASSED.json').write_bytes(output)
    with c.open_sftp() as f:f.open(remote+'/reports/D4_COMPONENT_CPU_PASSED.json','wb').write(output)
    print(json.dumps(proof))
finally:c.close()
