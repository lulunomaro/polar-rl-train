"""New D4 checkpoint/admission/rebase tests; no Isaac or CUDA initialization."""
import os,torch,tempfile,json,hashlib,time
from pathlib import Path
from types import SimpleNamespace
from action_delay_physics_queue import PhysicsActionQueue,WIDTHS
from action_delay_checkpoint import append_action_state,restore_action_before_new_episode,verify_action_new_episode
from feedback_delay_checkpoint import exact

torch.set_num_threads(1)
def fixture(seed=3,n=7):
 q=PhysicsActionQueue(n,'cpu',seed)
 a=SimpleNamespace(queue=q,state_dict=q.state_dict,load_state_dict=q.load_state_dict,
      neutral=lambda k:torch.full((n,WIDTHS[k]),.125 if k=='legs' else 0.))
 for k in WIDTHS:q.reset(k,torch.arange(n),a.neutral(k))
 return SimpleNamespace(_physics_action_delay=a,_sim_step_counter=0,action_delay_recipe=lambda:q.recipe())
e=fixture();a=e._physics_action_delay
for tick in range(8):
 for k in WIDTHS:
  if tick%4==0:a.queue.submit(k,torch.full((7,WIDTHS[k]),float(tick)),tick)
  a.queue.apply(k,tick)
ck=append_action_state(dict(sensor_recipe=dict(profile='noise_bias_mild_v1'),feedback_delay_recipe=dict(profile='control_0_10ms_v1')),e)
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'full.pt';torch.save(ck,p);loaded=torch.load(p,map_location='cpu',weights_only=False)
 assert exact(loaded,ck)
n=fixture(99);saved_global=torch.random.get_rng_state().clone()
has,episodes=restore_action_before_new_episode(n,loaded);assert has
assert all(torch.equal(n._physics_action_delay.queue.rng[k].get_state(),loaded['physical_action_delay_state']['rng'][k]) for k in WIDTHS)
for k,g in n._physics_action_delay.queue.groups.items():
 for name in g:
  if name!='last_apply_tick':assert torch.equal(g[name],loaded['physical_action_delay_state']['groups'][k][name])
 n._physics_action_delay.queue.reset(k,torch.arange(7),n._physics_action_delay.neutral(k))
assert verify_action_new_episode(n,episodes) and torch.equal(saved_global,torch.random.get_rng_state())
for k in WIDTHS:
 n._physics_action_delay.queue.submit(k,torch.ones((7,WIDTHS[k])),0)
 for tick in range(4):n._physics_action_delay.queue.apply(k,tick)
 assert bool(n._physics_action_delay.queue.groups[k]['applied_valid'].all())
old={k:v for k,v in loaded.items() if not k.startswith('physical_action_delay')}
os.environ['RM_ACTION_DELAY_INITIAL_ADMISSION']='D3_to_D4'
x=fixture();has,episodes=restore_action_before_new_episode(x,old);assert not has
for k in WIDTHS:x._physics_action_delay.queue.reset(k,torch.arange(7),x._physics_action_delay.neutral(k))
assert verify_action_new_episode(x,episodes)
os.environ.pop('RM_ACTION_DELAY_INITIAL_ADMISSION')
try:restore_action_before_new_episode(fixture(),old);raise RuntimeError('missing admission accepted')
except AssertionError:pass
bad=dict(loaded,physical_action_delay_recipe={'wrong':True})
try:restore_action_before_new_episode(fixture(),bad);raise RuntimeError('wrong recipe accepted')
except AssertionError:pass
out=dict(epoch=time.time(),passed=True,contracts=10,torch=torch.__version__,CUDA_initialized=torch.cuda.is_initialized(),actual_SDK=False,PPO=False,
         disk_full_state_exact=True,restore_targets_timestamps_RNG_before_rebase=True,new_episode_once=True,global_RNG_untouched=True,
         source_sha256={n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in ('action_delay_checkpoint.py','action_delay_training_env.py','test_action_checkpoint_cpu.py')})
assert not out['CUDA_initialized'];print(json.dumps(out))
