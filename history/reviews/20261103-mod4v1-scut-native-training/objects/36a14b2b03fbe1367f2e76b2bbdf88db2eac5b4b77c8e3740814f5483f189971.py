"""Analyze recorded first episodes and one necessary CPU final-model diagnostic."""
from pathlib import Path
import hashlib,io,json,time,sys,pickle,types
sys.path.insert(0,'C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/project/isaac')
import numpy as np
import torch
from tensordict import TensorDict
from mod4v1_scut.train import build_runner
from mod4v1_scut.checkpoint import check_interface

N=Path(__file__).resolve().parent;A=N/'env20000_1h';R=A/'reports'
out=R/'ACTUAL20000_ACTION_FAILURE_CPU.json'
if out.exists():raise FileExistsError(out)
f=json.loads((R/'POSTROUND_FULL_RETURNED.json').read_bytes())['files']
curves=f['evaluation/CONTROL_CURVES.json']['curves'];episodes=f['evaluation/ALL80.json']['first_episodes']
actions=np.array([r['action']for r in curves]);active=np.array([r['active']for r in curves],bool)
targets=np.array([r['joint_target']for r in curves]);rewards=np.array([r['reward']for r in curves])
terminal=np.array([r['controls']for r in episodes])
perenv=[]
for i,end in enumerate(terminal):
    # Source done sees the previous observation. Two initial observations occur
    # before control1, so _value_debug_step>10 first applies at control10.
    predicted=next((t for t in range(10,int(end)+1)if abs(actions[t-2,i]).max()>120),None)
    perenv.append(dict(env=i,terminal_control=int(end),first_previous_action_outlier_after_warmup=predicted,
        same_control=(predicted==int(end)),first_action=actions[0,i].tolist(),
        max_action_abs=float(abs(actions[:end,i]).max())))
raw=(A/'models/model_final.pt').read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert sha==f['production/FINAL.json']['checkpoint']['SHA']
# Decode the NumPy2 RNG tuple with the equivalent NumPy1 module name without
# modifying global imports or changing the source checkpoint.
class CompatUnpickler(pickle.Unpickler):
    def find_class(self,module,name):
        if module.startswith('numpy._core'):module=module.replace('numpy._core','numpy.core',1)
        return super().find_class(module,name)
compat_pickle=types.ModuleType('numpy_rng_compat_pickle')
compat_pickle.Unpickler=CompatUnpickler
compat_pickle.load=pickle.load
saved=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False,pickle_module=compat_pickle);del raw
torch.set_num_threads(2)
class Env:
    num_envs=8;num_actions=6;device='cpu';max_episode_length=400;cfg={}
    episode_length_buf=torch.zeros(8,dtype=torch.long)
    def get_observations(self):return TensorDict(dict(policy=torch.zeros(8,35),critic=torch.zeros(8,78)),[8])
runner=build_runner(Env(),None)
compatibility=check_interface(saved,'jump270',True)
runner.alg.load(saved,load_cfg=None,strict=True)
runner.current_learning_iteration=saved['iter'];runner.alg.learning_rate=saved['learning_rate']
before=[p.clone()for group in runner.alg.optimizer.param_groups for p in group['params']]
obs=torch.zeros(8,35);obs[:,0]=.6;obs[:,3]=1.25;obs[:,9]=-1.;obs[:,28]=1.
with torch.no_grad():
    nominal=runner.alg.actor(TensorDict(dict(policy=obs.clone()),[8]))
    unclipped=obs.clone();unclipped[:,22:28]=nominal
    clipped=obs.clone();clipped[:,22:28]=nominal.clamp(-6,6)
    next_raw=runner.alg.actor(TensorDict(dict(policy=unclipped),[8]))
    next_clip=runner.alg.actor(TensorDict(dict(policy=clipped),[8]))
assert all(torch.equal(a,b)for a,b in zip(before,[p for g in runner.alg.optimizer.param_groups for p in g['params']]))
steps=[int(x['step'])for x in runner.alg.optimizer.state.values()]
manifold=np.load(A/'evaluation/actual400hz.npz')
mask=manifold['active'];top=manifold['top_force'];both=(top>1).all(-1)&mask;anytop=(top>1).any(-1)&mask
report=dict(epoch=time.time(),kind='RECORDED_NATIVE_FAILURE_AND_CPU_INTERFACE_DIAGNOSIS',
    final=f['production/FINAL.json'],owner_exit=f['OWNER_EXIT.json'],
    actual_samples=f['production/FINAL.json']['PPO_updates']*24*20000,
    actual_first80=dict(strict=sum(r['strict270']for r in episodes),wholeclear=sum(r['first_flight_wholeclear']for r in episodes),
        leading=sum(r['first_flight_leading']for r in episodes),controls_min=int(terminal.min()),controls_max=int(terminal.max()),
        controls_mean=float(terminal.mean()),anytop_envs=int(anytop.any(0).sum()),bothtop_envs=int(both.any(0).sum()),
        max_active_top_force=float(top[mask].max()),
        raw_action_min=actions[active].min(0).tolist(),raw_action_max=actions[active].max(0).tolist(),
        action_clip_fraction_by_axis=(abs(actions[active])>6).mean(0).tolist(),
        recorded_joint_target_min=targets[active].min(0).tolist(),recorded_joint_target_max=targets[active].max(0).tolist(),
        joint_target_caveat='Original evaluator sampled target after reset on terminal controls; new evaluator captures pre-reset target',
        previous_action_outlier_predicts_exact_done=sum(x['same_control']for x in perenv),
        causal_limit='Old evaluator omitted reason masks. Alignment is retrospective evidence, not saved direct cause labels.',perenv=perenv),
    bug=dict(source='Enhanced MOD4 E0 train_mod4v1_e0.py lines169/246 clip_actions6.0 and actual retention meanclip6',
        lost_at='ScutVecEnv.step passed raw actor output to env and pending_actions',
        effect='Unbounded applied action and recurrent action-history input differ from source policy contract',
        original_SCUT_agent_clip_actions=None,explicit_MOD4_execution_mapping=6.0,
        repair='Clip env input out-of-place; retain original Gaussian samples/logprob for PPO'),
    CPU=dict(checkpoint_path=str(A/'models/model_final.pt'),checkpoint_SHA=sha,production_model_decodes=1,
        compatibility=compatibility,iter=saved['iter'],optimizer_entries=len(steps),Adam_min=min(steps),Adam_max=max(steps),
        STD=saved['actor_state_dict']['distribution.std_param'].tolist(),
        synthetic_nominal_input=obs[0].tolist(),synthetic_nominal_mean=nominal[0].tolist(),
        same_synthetic_pose_next_raw_history_mean=next_raw[0].tolist(),
        same_synthetic_pose_next_clip6_history_mean=next_clip[0].tolist(),
        synthetic_inputs_not_actual_rollout=True,optimizer_operations=0,weights_unchanged=True,physics=0),
    native_visual_review=dict(images=[str(A/'evaluation/recorded_native'/('actual20000final_'+v+'.png'))for v in ('side','top')],
        reviewed_by='current model native view_image',selected=[0,1,40,41],
        observation='All selected episodes collapse/drop near spawn, no edge approach. Terminal panels clamp END at .30/.22/.32/.26 seconds.',
        visual_collision_geometry='enhanced contract31bodies, no neural inference or fresh physics',
        not_all_contact_types_inferred_from_projection=True),
    decision='Repair original MOD4 action contract before another training window; short native samefinal diagnostic then decide continuation')
with out.open('x',encoding='utf8')as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
print(json.dumps(dict(report=str(out),exact_done_alignment=report['actual_first80']['previous_action_outlier_predicts_exact_done'],
    CPU=report['CPU']),ensure_ascii=False))
