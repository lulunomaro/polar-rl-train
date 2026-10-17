"""Latest closed H1 actor/public-clock components only; no SDK, SSH or dispatch."""
from pathlib import Path
import os, sys, time, json, hashlib, ast, copy, shutil, traceback
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import torch

B = Path(__file__).resolve().parent
R = B / 'reports'
Q = B / 'h1_latest_closed24_frozen_public04_components_CPU_v1'
S = B / 'payload_h1_native/job0/runtime/isaac/mod4'
P = B / 'actual_closed_H1_final/model_update24.pt'
BASE = B / 'e3_closed85_frozen_prepared_v2/payload'
EXPECTED = 'fe1709ec470aa4995e0b271947b65135d2e0bd43bec26b28316a451c5f1fa49e'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

GUARD = '''"""Exact latest H1 closed24/Adam644660 source; legacy GPU labels are historical."""
import torch
from h1_takeoff_progress_phase_v2 import PROFILE, H1TakeoffProgressPhaseV2
EXPECTED = 'fe1709ec470aa4995e0b271947b65135d2e0bd43bec26b28316a451c5f1fa49e'
def validate_H1_source(ck):
 assert ck['owned_H1_phase']=='production' and ck['owned_H1_completed_updates']==24 and ck['failed_partial_prefix'] is False
 task=ck['owned_H1_learning_task']
 assert task['kind']=='E5_H1_GROUND_PRELAUNCH_PROGRESS_V2' and task['num_envs']==20000
 assert task['public_normal_controls']==100 and task['public_jump_controls']==80 and task['then_normal_until_reset'] is True
 assert task['physics_dt']==.0025 and task['decimation']==4 and task['steps_per_update']==24
 assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17
 assert {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={644660}
 sd=ck['actor_state_dict'];assert [list(sd[k].shape) for k in ('mlp.0.weight','mlp.2.weight','mlp.4.weight','mlp.6.weight')]==[[256,35],[128,256],[64,128],[6,64]]
 assert ck['critic_state_dict']['mlp.0.weight'].shape[1]==38 and sd['distribution.std_param'].shape==(6,) and torch.isfinite(sd['distribution.std_param']).all() and (sd['distribution.std_param']>0).all()
 state=ck['H1_public_request_phase_state'];phase=state['phase']
 assert state['version']==1 and phase['profile']==PROFILE and phase['num_envs']==20000
 reference=H1TakeoffProgressPhaseV2(20000,'cpu').tensors();assert phase['tensors'].keys()==reference.keys()
 for key, value in reference.items():assert phase['tensors'][key].shape==value.shape and phase['tensors'][key].dtype==value.dtype
 for key in ('sensor_DR_state','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state','chassis_PD_state'):assert key in ck,key
 def finite(x):
  if torch.is_tensor(x):assert not (x.is_floating_point() or x.is_complex()) or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for value in x.values():finite(value)
  elif isinstance(x,(tuple,list)):
   for value in x:finite(value)
 finite(ck);return True
'''

SINGLE = '''"""Frozen H1 actor9; only actual published per-environment public0/4 is accepted."""
from pathlib import Path
import hashlib, torch
from h1_frozen_mean35_exact_v1 import FrozenMean35
from h1_closed24_source_guard_v1 import EXPECTED,validate_H1_source
class Single35:
 def __init__(self,path,n,device):
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==EXPECTED and type(n) is int and n>0
  ck=torch.load(path,map_location='cpu',weights_only=False);validate_H1_source(ck)
  self.model=FrozenMean35(ck['actor_state_dict']).to(device).eval();self.model.requires_grad_(False)
  self.source={key:value.detach().cpu().clone() for key,value in ck['actor_state_dict'].items()}
  self.n=n;self.device=torch.device(device);self.last=torch.zeros(n,6,device=device);self.tick=-1;self.pending=None;self.calls=0;self.controls=0
 def begin(self,tick,provider,public_modes):
  assert type(tick) is int and tick>=0
  assert torch.is_tensor(public_modes) and public_modes.shape==(self.n,) and public_modes.dtype==torch.long and public_modes.device==self.device and ((public_modes==0)|(public_modes==4)).all()
  if self.pending is not None:
   assert self.tick==tick and torch.equal(self.pending['declared_actual_public_modes'],public_modes);return self.pending
  assert self.tick<0 or tick==self.tick+1
  x=provider();assert torch.is_tensor(x) and x.shape==(self.n,35) and x.dtype==torch.float32 and x.device==self.device and torch.isfinite(x).all()
  assert not x[:,:3].any() and torch.equal(x[:,22:28],self.last)
  assert torch.equal(x[:,28:35],torch.nn.functional.one_hot(public_modes,7).to(dtype=x.dtype))
  a=self.model(x);assert a.shape==(self.n,6) and torch.isfinite(a).all()
  self.pending=dict(shared_obs=x.detach().clone(),raw_action=a.detach().clone(),clipped_action=a.detach().clamp(-6,6),declared_actual_public_modes=public_modes.detach().clone());self.tick=tick;self.calls+=1;return self.pending
 def finish(self,actual,ended):
  assert self.pending is not None and torch.is_tensor(actual) and actual.shape==(self.n,6) and actual.dtype==torch.float32 and actual.device==self.device and torch.equal(actual,self.pending['clipped_action'])
  assert torch.is_tensor(ended) and ended.shape==(self.n,) and ended.dtype==torch.bool and ended.device==self.device
  self.last=actual.detach().clone();self.last[ended]=0;self.pending=None;self.controls+=1
 def exact(self):
  assert all(torch.equal(value.detach().cpu(),self.source[key]) for key,value in self.model.snapshot().items());return True
'''

def put(path, value):
    with path.open('x', encoding='utf8', newline='\n') as f:
        f.write(value if isinstance(value, str) else json.dumps(value, indent=2))

def main():
    assert not Q.exists() and H(P) == EXPECTED and not torch.cuda.is_initialized()
    torch.set_num_threads(2)
    rng = torch.get_rng_state().clone()
    Q.mkdir()
    for name in ('h1_public_request_phase_v1.py', 'h1_takeoff_progress_phase_v2.py'):
        shutil.copy2(S/name, Q/name)
        assert H(S/name) == H(Q/name)
    mean_path = BASE/'hard_top1_frozen_expert_CPU_component_v1.py'
    tree = ast.parse(mean_path.read_text('utf8'))
    klass = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'FrozenMean35')
    mean = 'import torch\nfrom torch import nn\nfrom torch.nn import functional as F\n\n' + ast.get_source_segment(mean_path.read_text('utf8'), klass) + '\n'
    put(Q/'h1_frozen_mean35_exact_v1.py', mean)
    copied = next(n for n in ast.parse(mean).body if isinstance(n, ast.ClassDef))
    assert ast.dump(klass) == ast.dump(copied)
    put(Q/'h1_closed24_source_guard_v1.py', GUARD)
    put(Q/'h1_closed24_single35_public04_v1.py', SINGLE)
    sys.path.insert(0, str(Q))
    from h1_closed24_source_guard_v1 import validate_H1_source
    from h1_closed24_single35_public04_v1 import Single35
    from h1_takeoff_progress_phase_v2 import H1TakeoffProgressPhaseV2, PROFILE
    ck = torch.load(P, map_location='cpu', weights_only=False)
    assert validate_H1_source(ck)
    negative_sources = []
    def source_reject(label, change):
        bad = copy.deepcopy(ck);change(bad)
        try: validate_H1_source(bad)
        except (AssertionError, KeyError): negative_sources.append(label)
        else: raise AssertionError('Source accepted: '+label)
    source_reject('wrong_owned_phase', lambda c:c.__setitem__('owned_H1_phase','native'))
    source_reject('wrong_owned_update', lambda c:c.__setitem__('owned_H1_completed_updates',121))
    source_reject('wrong_task_kind', lambda c:c['owned_H1_learning_task'].__setitem__('kind','E3_PUBLIC_RECOVERY'))
    source_reject('wrong_Adam', lambda c:next(iter(c['optimizer_state_dict']['state'].values()))['step'].fill_(644180))
    source_reject('wrong_phase_profile', lambda c:c['H1_public_request_phase_state']['phase']['profile'].__setitem__('version',1))
    source_reject('missing_critic', lambda c:c['critic_state_dict'].pop('mlp.6.bias'))
    source_reject('wrong_actor_shape', lambda c:c['actor_state_dict'].__setitem__('mlp.0.weight',torch.zeros(256,34)))
    source_reject('nonpositive_STD', lambda c:c['actor_state_dict']['distribution.std_param'].fill_(0))
    source_reject('nonfinite_runtime_phase', lambda c:c['H1_public_request_phase_state']['phase']['tensors']['peak'].fill_(float('nan')))
    source_reject('wrong_phase_tensor_dtype', lambda c:c['H1_public_request_phase_state']['phase']['tensors'].__setitem__('age_control',torch.zeros(20000)))

    actor = Single35(P, 8, 'cpu');phase = H1TakeoffProgressPhaseV2(8,'cpu')
    # Actual external clock, including different per-environment ages after selected reset.
    # The feedback below is a CPU fixture, not a robot trajectory or physical witness.
    mode_trace = [];provider_calls = [0];selected_reset = torch.tensor([2,5])
    for tick in range(302):
        modes = phase.public_mode();mode_trace.append(modes.clone())
        x = torch.zeros(8,35);x[:,3:22] = torch.sin(torch.arange(8*19,dtype=torch.float32).reshape(8,19))*.01
        x[:,22:28] = actor.last;x[:,28:] = torch.nn.functional.one_hot(modes,7)
        def provider(): provider_calls[0]+=1;return x
        pending = actor.begin(tick,provider,modes)
        assert actor.begin(tick,provider,modes) is pending and provider_calls[0]==tick+1
        ended = torch.zeros(8,dtype=torch.bool)
        if tick==120: ended[selected_reset]=True
        actual=pending['raw_action'].clamp(-6,6)
        assert torch.equal(actual,pending['clipped_action'])
        actor.finish(actual,ended);phase.begin_control();phase.finish_control_before_selected_reset()
        if tick==120:
            before={k:v.clone() for k,v in phase.tensors().items()};phase.reset(selected_reset)
            other=torch.tensor([0,1,3,4,6,7])
            assert all(torch.equal(v[other],before[k][other]) and not v[selected_reset].any() for k,v in phase.tensors().items())
            assert not actor.last[selected_reset].any() and torch.equal(actor.last[other],actual[other])
    modes=torch.stack(mode_trace)
    assert (modes[:100]==0).all() and (modes[100:121]==4).all()
    assert (modes[121:180,[0,1,3,4,6,7]]==4).all() and (modes[180:,[0,1,3,4,6,7]]==0).all()
    assert (modes[121:221,selected_reset]==0).all() and (modes[221:301,selected_reset]==4).all() and (modes[301:,selected_reset]==0).all()
    assert actor.calls==actor.controls==provider_calls[0]==302 and actor.exact()
    assert not list(actor.model.parameters()) and len(actor.model.snapshot())==9

    # Contact, flight and proxy evidence cannot select the externally requested public mode.
    a=H1TakeoffProgressPhaseV2(2,'cpu');b=H1TakeoffProgressPhaseV2(2,'cpu')
    for tick in range(181):
        assert torch.equal(a.public_mode(),b.public_mode())
        for p in (a,b):p.begin_control()
        for _ in range(4):
            kw=dict(wheel_N=torch.ones(2,2)*10,wheel_clear_m=torch.zeros(2,2),all_min_clear_m=torch.zeros(2),nonwheel_max_N=torch.zeros(2),root_vz=torch.zeros(2),root_planar_speed=torch.zeros(2),roll=torch.zeros(2),pitch=torch.zeros(2),yaw=torch.zeros(2))
            a.physical(**kw)
            kw.update(wheel_N=torch.zeros(2,2),root_vz=torch.ones(2),nonwheel_max_N=torch.ones(2)*5)
            b.physical(**kw)
        a.finish_control_before_selected_reset();b.finish_control_before_selected_reset()
    assert not torch.equal(a.attempt,b.attempt) and torch.equal(a.age_control,b.age_control)

    rejects=[]
    def reject(label, call):
        try:call()
        except AssertionError:rejects.append(label)
        else:raise AssertionError('Adapter accepted: '+label)
    fresh=Single35(P,8,'cpu');pub=torch.zeros(8,dtype=torch.long)
    def obs():
        x=torch.zeros(8,35);x[:,28]=1;return x
    reject('wrong_model_full_SHA',lambda:Single35(B.parent/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017/actual_new_native_first_models/model_update1.pt',8,'cpu'))
    reject('negative_tick',lambda:fresh.begin(-1,obs,pub))
    reject('boolean_tick',lambda:fresh.begin(True,obs,pub))
    reject('mode_shape',lambda:fresh.begin(0,obs,pub[:7]))
    reject('mode_dtype',lambda:fresh.begin(0,obs,pub.int()))
    reject('mode_device',lambda:fresh.begin(0,obs,torch.empty(8,dtype=torch.long,device='meta')))
    reject('undeclared_mode3',lambda:fresh.begin(0,obs,torch.full((8,),3,dtype=torch.long)))
    reject('observation_shape',lambda:fresh.begin(0,lambda:obs()[:,:34],pub))
    reject('observation_dtype',lambda:fresh.begin(0,lambda:obs().double(),pub))
    def altered(column,value):
        x=obs();x[0,column]=value;return x
    reject('nonfinite_observation',lambda:fresh.begin(0,lambda:altered(7,float('nan')),pub))
    reject('nonzero_twist',lambda:fresh.begin(0,lambda:altered(0,.1),pub))
    reject('previous_actual_action_mismatch',lambda:fresh.begin(0,lambda:altered(22,1),pub))
    reject('public_onehot_mismatch',lambda:fresh.begin(0,obs,torch.full((8,),4,dtype=torch.long)))
    p=fresh.begin(0,obs,pub)
    reject('reentrant_mode_change',lambda:fresh.begin(0,obs,torch.full((8,),4,dtype=torch.long)))
    reject('reentrant_tick_change',lambda:fresh.begin(1,obs,pub))
    reject('actual_action_not_whole_clipped6',lambda:fresh.finish(p['clipped_action']+.1,torch.zeros(8,dtype=torch.bool)))
    reject('ended_wrong_dtype',lambda:fresh.finish(p['clipped_action'],torch.zeros(8)))
    fresh.finish(p['clipped_action'],torch.zeros(8,dtype=torch.bool))
    reject('skipped_tick',lambda:fresh.begin(2,obs,pub))
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()

    files=[]
    for path in sorted(Q.glob('*.py')):
        ast.parse(path.read_text('utf8'));files.append(dict(path=str(path),bytes=path.stat().st_size,SHA=H(path)))
    report=dict(epoch=time.time(),trial_id='latest-H1-closed24-frozen-public04-components-CPU-v1',passed_source_actor_and_original_clock_components_CPU=True,
        source=dict(path=str(P),bytes=P.stat().st_size,SHA=EXPECTED,owned_completed_updates=24,all17Adam=644660),
        actual_source_guard_checks_full_checkpoint_runtime_finite=True,actor9_including_STD_initial_final_literalexact=True,critic_optimizer_gate_not_in_frozen_actor=True,
        FrozenMean35_class_AST_exact_to_existing_frozen_component=True,original_H1_phase_two_modules_byteexact=True,source_phase_profile=PROFILE,
        normal100_mode4_next80_then_normal_original_schedule=True,original_selectedreset_only_same_rows_phase_and_previous_action=True,
        actual_published_perenv04_vector_only_no_hidden_contact_or_phase_truth_actor_input=True,original_clock_unchanged_under_two_different_synthetic_contact_inputs=True,
        fixture_controls=302,fixture_environments=8,fixture_not_physics_or_GPU_evidence=True,provider_once_per_tick_whole6_clip6_previous_actual6=True,
        source_negative_cases=negative_sources,adapter_negative_cases=rejects,components=files,
        legacy_source_task_labels_preserved_separate_from_actual_source=dict(GPU_UUID=ck['owned_H1_learning_task']['GPU_UUID'],exact_closed_source_updates=ck['owned_H1_learning_task']['exact_closed_source_updates'],authoritative_current_owned_updates=ck['owned_H1_completed_updates'],authoritative_Adam=644660),
        no_20k_source_state_restored_into_fixture=True,no_new_target_package_SSH_Task_native_full_PPO_GO_or_canonical_write=True,RNG_unchanged0CUDA0optimizer=True,
        pending=['complete_H1_frozen_target_package_and_fresh_actual_resource_identity_lock_source_SDK_admission','new_own_frozen_native_then_independent_allrow_CPU_before_new_full_frozen','actual_jump_flight_landing_recovery_qualification'],
        original_source_and_prior_false_native_events_proxy_and_GPU_geometry_boundaries_unchanged=True,
        local_orientation_issues_preserved=[dict(id='H1-next-source-read-aggregate-output-truncation',type='tool_stdout_truncation',effect='Only broad source reads truncated; subsequent exact files and scalar keys read separately; no GPU inference'),dict(id='E3-perenv-preparer-guessed-path-lookup-miss',type='Get-Content path not found',path='MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017/prepare_E3_closed85_perenv_public03_frozen_components_CPU_V2_once.py',effect='Read existing component files directly; no execution'),dict(id='broad-rg-rmuc2026-unpack-permission',type='rg os5 permission denied',path='rmuc2026_work/unpack_verify_4zomhj13',effect='Unrelated path excluded by subsequent exact owned source reads'),dict(id='H1-phase-inline-dict-JSON-reader-V1',type='TypeError',error='Object of type Tensor is not JSON serializable',effect='No report written and no source change; V2 emits phase tensor shape/dtype and container type only')])
    put(R/'LATEST_H1_CLOSED24_FROZEN_PUBLIC04_SOURCE_COMPONENTS_CPU_PREPARED_ACTUAL.json',report)
    print(json.dumps(dict(H1_latest_source_components_CPU=True,source_Adam=644660,source_negatives=len(negative_sources),adapter_negatives=len(rejects),original_phase_source_byteexact=True,no_GPU_or_PPO=True)),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('H1_LATEST_FROZEN_COMPONENTS_CPU_V1_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),local_CPU_only_no_SSH_SDK_GPU_or_PPO=True,partial_components_preserved=True))
        raise
