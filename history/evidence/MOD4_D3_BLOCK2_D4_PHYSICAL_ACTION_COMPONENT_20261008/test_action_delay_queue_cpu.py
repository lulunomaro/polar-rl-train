"""Independent transition-timing fixtures and state/reset failures; no Isaac/CUDA."""
from pathlib import Path
import torch,json,copy,tempfile,hashlib,ast
from action_delay_physics_queue import PhysicsActionQueue,WIDTHS
torch.set_num_threads(1);assert not torch.cuda.is_initialized()
global_rng=torch.random.get_rng_state().clone();n=12;ids=torch.arange(n)
neutral={k:torch.full((n,width),.125 if k=='legs' else 0.) for k,width in WIDTHS.items()}
q=PhysicsActionQueue(n,'cpu',17)
for k in WIDTHS:q.reset(k,ids,neutral[k])
assert not torch.equal(q.groups['legs']['lag_steps'],q.groups['wheels']['lag_steps'])
passed=['leg_wheel_independent_episode_streams']
# Known two-control-period waveform: policy targets change at0 and10ms.
# At each physics boundary, independently choose the newest command whose
# requested application time has passed. Warmup holds the supplied reset target.
for k,width in WIDTHS.items():q.groups[k]['lag_steps']=torch.arange(n)%3
for tick in range(8):
    if tick in (0,4):
        for k,width in WIDTHS.items():
            x=torch.arange(n*width).reshape(n,width).float()+10*(tick//4+1)
            q.submit(k,x,tick);q.submit(k,x.clone(),tick)
    for k,width in WIDTHS.items():
        before=q.state_dict();actual=q.apply(k,tick)
        for row in range(n):
            lag=row%3;available=[issue for issue in (0,4) if issue<=tick and issue+lag<=tick]
            expected=neutral[k][row] if not available else torch.arange(n*width).reshape(n,width).float()[row]+10*(max(available)//4+1)
            assert torch.equal(actual[row],expected),(k,tick,row)
        after=q.state_dict();assert torch.equal(actual,q.apply(k,tick))
        assert all(torch.equal(after['groups'][k][f],q.groups[k][f]) for f in q.groups[k])
        receipt=q.receipt(k,tick);mask=receipt['valid_policy_command']
        assert torch.equal(receipt['actual_first_transition_delay_us'][mask],receipt['requested_delay_us'][mask])
        assert bool((receipt['actual_first_transition_delay_us'][~mask]==-1).all())
passed+=['0_2500_5000us_target_transition_golden_waveform','new_target_delayed_without_control_step_mislabel','neutral_warmup_is_not_a_valid_policy_sample','same_tick_submit_and_apply_cached_once','held_command_age_distinct_from_transition_latency','group_four_leg_targets_remain_coherent']
selected=torch.tensor([1,4,7]);saved=q.state_dict()
q.reset('legs',selected,neutral['legs']);g=q.groups['legs']
assert torch.equal(g['applied'][selected],neutral['legs'][selected]) and not bool(g['pending_valid'][selected].any())
other=torch.tensor([i for i in range(n) if i not in selected.tolist()])
assert all(torch.equal(g[f][other],saved['groups']['legs'][f][other]) for f in g)
assert all(torch.equal(q.groups['wheels'][f],saved['groups']['wheels'][f]) for f in q.groups['wheels'])
assert torch.equal(g['last_apply_tick'],saved['groups']['legs']['last_apply_tick'])
passed+=['selected_reset_removes_stale_targets_and_preserves_other_rows','leg_reset_does_not_change_wheel_queue_or_clock']
state=q.state_dict();clone=PhysicsActionQueue(n,'cpu',993)
with tempfile.TemporaryDirectory() as td:
    file=Path(td)/'queue.pt';torch.save(state,file);clone.load_state_dict(torch.load(file,weights_only=False))
for k,width in WIDTHS.items():
    command=torch.full((n,width),55.)
    q.submit(k,command,8);clone.submit(k,command,8)
for tick in range(8,12):
    for k in WIDTHS:assert torch.equal(q.apply(k,tick),clone.apply(k,tick))
for k in WIDTHS:
    q.reset(k,selected,neutral[k]);clone.reset(k,selected,neutral[k]);assert torch.equal(q.groups[k]['lag_steps'],clone.groups[k]['lag_steps']) and torch.equal(q.rng[k].get_state(),clone.rng[k].get_state())
passed+=['all_target_queue_timestamps_and_RNG_disk_roundtrip','next_target_and_episode_draws_exact_after_restore']
for mutate in (lambda s:s.update(physics_us=500),lambda s:s['groups'].pop('legs'),lambda s:s['groups']['legs']['applied'].fill_(float('nan')),lambda s:s['groups']['wheels']['lag_steps'].fill_(3),lambda s:s['groups']['legs']['first_apply_tick'].fill_(1000),lambda s:s['groups']['legs'].update(applied=torch.zeros(n,3))):
    bad=copy.deepcopy(q.state_dict());mutate(bad)
    try:clone.load_state_dict(bad)
    except (AssertionError,KeyError,RuntimeError):pass
    else:raise AssertionError('Invalid checkpoint accepted')
passed.append('clock_shape_range_missing_group_nonfinite_future_timestamp_rejected')
def refused(call):
    try:call()
    except AssertionError:return
    raise AssertionError('Invalid operation accepted')
refused(lambda:q.apply('legs',13));refused(lambda:q.submit('legs',torch.zeros(n,4),16))
refused(lambda:q.submit('legs',torch.full((n,4),float('nan')),12));refused(lambda:q.reset('legs',[1,1],neutral['legs']))
refused(lambda:q.reset('legs',selected,neutral['legs'],new_scene_clock=True))
passed+=['physical_callback_or_control_command_gap_rejected','invalid_input_or_partial_scene_rebase_rejected']
# Explicit new scene starts a fresh physics timeline only after state restore.
for k in WIDTHS:q.reset(k,ids,neutral[k],new_scene_clock=True);q.submit(k,torch.ones_like(neutral[k]),0);q.apply(k,0)
passed.append('full_new_scene_reset_explicitly_rebases_clock_no_PhysX_resume_claim')
off=PhysicsActionQueue(n,'cpu',4,enabled=False)
for k in WIDTHS:off.reset(k,ids,neutral[k]);off.submit(k,torch.ones_like(neutral[k]),0);assert torch.equal(off.apply(k,0),torch.ones_like(neutral[k]))
assert off.validate_state(off.state_dict());passed.append('off_exact_and_disabled_lags_zero')
assert torch.equal(global_rng,torch.random.get_rng_state());assert not torch.cuda.is_initialized()
passed.append('global_RNG_untouched_and_no_CUDA_initialized')
# Verify actual installed SDK's integration order, without importing Isaac.
sdk=Path(__file__).parent/'reviewed_sources/manager_based_rl_env.py'
tree=ast.parse(sdk.read_text(encoding='utf8'));klass=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='ManagerBasedRLEnv');step=next(x for x in klass.body if isinstance(x,ast.FunctionDef) and x.name=='step')
loop=next(x for x in ast.walk(step) if isinstance(x,ast.For) and isinstance(x.iter,ast.Call) and ast.unparse(x.iter)=='range(self.cfg.decimation)')
expressions=[ast.unparse(x) for x in loop.body]
assert expressions[0]=='self._sim_step_counter += 1' and expressions[1]=='self.action_manager.apply_action()' and expressions[2]=='self.scene.write_data_to_sim()' and expressions[3]=='self.sim.step(render=False)'
passed.append('actual_SDK_counter_increments_before_apply_so_apply_time_is_counter_minus1')
print(json.dumps(dict(passed=True,count=len(passed),contracts=passed,torch_version=torch.__version__,no_CUDA_initialized=True,no_Isaac_or_PPO_started=True,source_sha256=hashlib.sha256(Path(__file__).with_name('action_delay_physics_queue.py').read_bytes()).hexdigest(),actual_SDK_source_sha256=hashlib.sha256(sdk.read_bytes()).hexdigest(),recipe=q.recipe())))
