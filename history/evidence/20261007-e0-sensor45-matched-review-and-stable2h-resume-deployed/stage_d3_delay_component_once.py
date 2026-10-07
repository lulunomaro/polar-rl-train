"""CPU-only preparation of the approved first0/10ms D3 range."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_D3_DELAY_COMPONENT_PREPARE_20261007';c=connect()
try:
 code=f"from pathlib import Path;D=Path('{ROOT}');assert not D.exists();D.mkdir();(D/'reports').mkdir()"
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=30);assert o.channel.recv_exit_status()==0,(o.read()+e.read()).decode()
 with c.open_sftp() as sf:
  for name in ('feedback_delay_mild.py','test_feedback_delay_mild_cpu.py'):sf.put(str(D/'delay_component'/name),ROOT+'/'+name)
 code=r'''
from pathlib import Path
import subprocess,json,hashlib,time
D=Path('/home/egde/rl_candidates/MOD4_D3_DELAY_COMPONENT_PREPARE_20261007');p=subprocess.run(['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',str(D/'test_feedback_delay_mild_cpu.py')],capture_output=True,text=True,cwd=D,timeout=40)
assert p.returncode==0,p.stdout+p.stderr
v=json.loads(p.stdout);assert v['passed'] and v['no_CUDA_initialized'] and not v['SDK_or_training_deployed']
(D/'reports/D3_DELAY_COMPONENT_CPU_PASSED.json').write_text(json.dumps(v,indent=2))
(D/'reports/SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ('feedback_delay_mild.py','test_feedback_delay_mild_cpu.py')}),indent=2))
(D/'reports/D3_DELAY_WORK_ORDER.json').write_text(json.dumps(dict(epoch=time.time(),status='CPU_COMPONENT_ONLY',control_period_us=10000,first_request_latency_us=[0,10000],physics_dt_us=1000,feedback_sample_rate_hz=100,raw_feedback_five_channels=True,no_command_lastaction_delay=True,clean_critic_unchanged=True,noise_and_episode_bias_before_delay_intention=True,episode_latency_rng_independent=True,reset_current_sample_warmup_age_zero_disclosed=True,actual_SDK_sample_apply_timestamp_frame_scale_reset_proof_pending=True,actor35_critic38_action6_unchanged=True,training_source_not_preselected=True,no_CUDA_GPU_or_PPO=True,no_canonical_write_authority=True,range20ms_and50Hz_not_installed=True),indent=2))
print(json.dumps(v))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'D3_DELAY_COMPONENT_CPU_PASSED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
finally:c.close()
