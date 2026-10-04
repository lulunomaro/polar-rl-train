"""One read-only GPU/log snapshot for the scheduled inspection."""
import json,sys,shlex
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
code=r'''import json,subprocess,time,re
from pathlib import Path
P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
s=json.loads((P/'status.json').read_text());p=Path(s['active_log'])
with p.open('rb') as f:f.seek(max(0,p.stat().st_size-200000));tail=f.read().decode(errors='replace')
times=re.findall(r'Iteration time:\s*([0-9.]+)s',tail)
gpu=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,temperature.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True).stdout.strip()
kernel=subprocess.run(['journalctl','-k','--since','2 hours ago','--no-pager'],capture_output=True,text=True)
faults=[line for line in kernel.stdout.splitlines() if re.search(r'NVRM.*Xid|GPU has fallen off',line)]
print(json.dumps(dict(epoch=time.time(),active_log=str(p),training_pid=s.get('training_pid'),gpu_csv=gpu,
    last_iteration_s=float(times[-1]) if times else None,environment_policy_steps_per_s=480000/float(times[-1]) if times else None,
    recent_error_lines=[line for line in tail.splitlines() if re.search(r'Traceback|OutOfMemory|CUDA.*error|PhysX.*error|nan\b',line,re.I)],
    kernel_available=kernel.returncode==0,kernel_gpu_errors=faults,read_only=True)))'''
c=connect()
try:
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30)
    raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err
    x=json.loads(raw);(D/'LIVE_EXTRA_HEALTH_20261004_1922.json').write_text(json.dumps(x,indent=2),encoding='utf8')
    print(json.dumps(x))
finally:c.close()
