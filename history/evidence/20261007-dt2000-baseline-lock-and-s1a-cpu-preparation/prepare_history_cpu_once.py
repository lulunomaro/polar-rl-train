"""Bounded actual-target CPU tests while existing4090 PPO continues independently."""
from pathlib import Path
import sys,json,shlex,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
assert not (R/'HISTORY_COMPONENT_CPU_PASSED.json').exists()
root='/home/egde/rl_candidates/MOD4_S1A_HISTORY_COMPONENT_20261007'
files=['history_latent_component.py','test_history_latent_component.py','physics_baseline_contract.py','test_baseline_contract.py','env.json']
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as s:
  try:s.stat(root);raise AssertionError('Unique component root already exists')
  except FileNotFoundError:pass
  s.mkdir(root);s.mkdir(root+'/reports')
  for n in files:s.put(str(D/n),root+'/'+n)
  s.put(str(R/'DT2000_BASELINE_LOCKED.json'),root+'/reports/DT2000_BASELINE_LOCKED.json')
 code=r'''
from pathlib import Path
import torch,sys,json,time,unittest,io,hashlib
D=Path('ROOT');sys.path.insert(0,str(D));torch.set_num_threads(1)
assert not (D/'reports/HISTORY_COMPONENT_CPU_PASSED.json').exists()
suite=unittest.TestSuite()
for name in ('test_baseline_contract','test_history_latent_component'):suite.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=1).run(suite)
assert result.wasSuccessful(),stream.getvalue()
source=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-06_05-04-08_auto_0282_physical_dr_stage1_learning_cap12.5664_white_v3/model_23509.pt')
assert hashlib.sha256(source.read_bytes()).hexdigest()=='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a'
ck=torch.load(source,map_location='cpu',weights_only=False)
from history_latent_component import expand_actor_state
new=expand_actor_state(ck['actor_state_dict']);old=ck['actor_state_dict']
assert all(torch.equal(new[k],old[k]) for k in old if k!='mlp.0.weight')
g=torch.Generator().manual_seed(78);current=torch.randn(128,35,generator=g);latent=torch.randn(128,3,generator=g)
def forward(state,x):
 for i in [0,2,4,6]:
  x=torch.nn.functional.linear(x,state[f'mlp.{i}.weight'],state[f'mlp.{i}.bias'])
  if i<6:x=torch.nn.functional.elu(x)
 return x
a=forward(old,current);b=forward(new,torch.cat((current,latent),1));diff=float((a-b).abs().max())
torch.testing.assert_close(a,b,rtol=1e-5,atol=1e-6)
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),component_root=str(D),scope='S1A CPU mathematical/lifecycle and real-source weights-only migration preparation; not SDK or PPO',
 tests=result.testsRun,passed=True,torch_version=torch.__version__,source_checkpoint_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
 actual_actor_schema_verified=True,source_std_all_other_actor_weights_exact=True,new_latent_columns_zero=True,
 full128_fixture_actor_output_max_abs_difference=diff,migration_float32_rtol=1e-5,migration_float32_atol=1e-6,
 independent_body_velocity_label_and_critic_SDK_readback_pending=True,full_new_architecture_checkpoint_optimizers_RNG_runtime_contract_pending=True,
 new_actor_shape=[38,256,128,64,6],encoder_shape=[175,128,64,3],history_frames=5,history_control_span_s=.04,
 CUDA_initialized=False,GPU_probe_count=0,PPO_update_count=0,canonical_write_operations=0,controller_deployed=False,
 source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.iterdir() if p.is_file()})
(D/'reports/HISTORY_COMPONENT_CPU_PASSED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',root)
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode();v=json.loads(raw)
 (R/'HISTORY_COMPONENT_CPU_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
