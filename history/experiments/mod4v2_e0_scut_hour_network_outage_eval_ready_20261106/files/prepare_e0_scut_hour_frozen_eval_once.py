"""SOURCE ONLY preparer: publish six NEW SCUT E0 frozen-evaluation Python sources.

This preparer uses stdlib source reads/ASTs only. It never imports an entry, SDK,
Torch, connector or generated module, opens a checkpoint, stages, dispatches or
observes a run. The generated stager independently requires the exact CLOSED
SCUT hour, actual owner/child waits/account/release, qualified FINAL and U000.
Existing STOP26 entries, actual training workers and adapters are never edited.
"""
from pathlib import Path
import ast
import hashlib
import textwrap

D = Path(__file__).resolve().parent
PREFIX = 'SCUT_E0_HOUR_FROZEN'
HOUR_ROOT = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SCUT_HOUR_FULL_LEARNER_MIGRATION_20261106_062902_1793917742719982000'
OLD_HOUR_ROOT = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_HOUR_WINDOW_FULL_LEARNER_MIGRATION_20261106_023350_1793903630723043100'
HOUR_WORKER = 'worker_e0_scut_v14_hour_v3.py'
OLD_WORKER = 'worker_mod4v2_frozen_eval_e0_hour_v4.py'
WORKER = PREFIX + '_worker.py'
FACTORY = PREFIX + '_factory.py'
MODE = 'SCUT_V14_ORIGINAL_FINITE_WALL_CLOCK_HOUR'
SCUT_TASK = 'Robotics-Wheelbipe-V14-Flat-v0'
FORMAL_SHA = '6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693'
ASSET_SHA = '7361b6930a7270e65f3b290cfa71c50f8e1f0beccaa9cab1fa8a994f03cb35b8'
CONTRACT_SHA = 'f01ffcf0f967e1c1f8dc153c9e06d73a70ab3f78e17e8b479159c14a6cf63047'
ADAPTER_SHA = {
    'scut_v14_flat_reward_adapter_v4': 'ddb3f77f19a29c0bc047082aef774aa62b585801d539b670f69c434041828570',
    'scut_v14_flat_command_termination_adapter_v1': '3f4c93437a7128677701d58c7012ab13a91d78bec727e1f0b1182f12316a1cd8',
}


def need(value, message):
    if not value:
        raise RuntimeError('Unknown/source precondition: ' + message)


def source(name):
    p = D / name
    need(p.suffix == '.py' and p.is_file() and not p.is_symlink(), 'regular named Python source: ' + name)
    return p.read_text(encoding='utf-8-sig')


def named_node(text, name):
    nodes = [n for n in ast.parse(text).body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name]
    need(len(nodes) == 1, 'one source definition ' + name)
    return nodes[0]


def same_definitions(before, after, names):
    for name in names:
        a = ast.dump(named_node(before, name), include_attributes=False)
        b = ast.dump(named_node(after, name), include_attributes=False)
        need(a == b, 'preserved original AST ' + name)


class Edits:
    """Bounded literal edits, with an exact inverse for every source change."""
    def __init__(self, text):
        self.original = self.text = text
        self.edits = []

    def replace(self, old, new, count=1):
        need(old != new and old and new, 'nonempty distinct bounded edit')
        need(self.text.count(old) == count, 'literal anchor count ' + repr(old[:120]))
        need(new not in self.text, 'new anchor must not collide ' + repr(new[:120]))
        self.text = self.text.replace(old, new, count)
        self.edits.append((old, new, count))
        return self

    def all(self, old, new):
        count = self.text.count(old)
        need(count > 0, 'existing rename anchor ' + old)
        return self.replace(old, new, count)

    def finish(self):
        restored = self.text
        for old, new, count in reversed(self.edits):
            need(restored.count(new) == count, 'unambiguous inverse source edit')
            restored = restored.replace(new, old, count)
        need(restored == self.original, 'finite inverse diff exact')
        return self.text


FACTORY_SOURCE = r'''"""Binding-only SCUT frozen factory. No learner, physics, reset, obs or RNG calls.

The task still names the REAL current SCUT hour worker. Its load_original owns
all original imports, construction, D6 mapping, cmd/reward configure and cmd.bind.
This shim exposes the named original actor CONFIG function, not a PPO clone;
it adds only reward.bind at the frozen worker's existing sole-reset boundary.
"""
from pathlib import Path
import inspect

MODE = __SCUT_MODE__
TASK = __SCUT_TASK__
HOUR_ROOT = __HOUR_ROOT__
WORKER = __HOUR_WORKER__
ADAPTER_SHA = __ADAPTER_SHA__


class Unknown(RuntimeError):
    """Absent/different source-verified field; never a guessed zero or pass."""


def require(value, message):
    if not value:
        raise Unknown(message)


def field(obj, name):
    if not hasattr(obj, name):
        raise Unknown('Required field missing: ' + type(obj).__module__ + '.' + type(obj).__qualname__ + '.' + name)
    value = getattr(obj, name)
    if value is None:
        raise Unknown('Required field is None: ' + name)
    return value


def tensor_view(value, torch, label):
    # Named actual ABI only, full zero-copy view, no reshape/cast/fill/copy.
    if isinstance(value, torch.Tensor):
        return value
    from isaaclab.utils.warp import ProxyArray
    if isinstance(value, ProxyArray):
        view = value.torch
        require(isinstance(view, torch.Tensor) and
                tuple(view.shape[:len(value.shape)]) == tuple(value.shape),
                'ProxyArray cached Torch array-shape prefix differs: ' + label)
        return view  # Warp vector/quaternion component axes MUST stay present.
    raise Unknown('Unsupported tensor ABI for ' + label + ': ' + type(value).__module__ + '.' +
                  type(value).__qualname__ + ' shape=' + str(getattr(value, 'shape', None)))


def load_original(actual, task, out):
    require(task['role'] == 'E0' and task['training_window_mode'] == actual.SCUT_MODE == MODE and
            actual.SCUT_TASK == TASK and actual.SCUT_ADAPTER_SHA == ADAPTER_SHA,
            'Exact current SCUT hour source/mode/adapters required')
    require(str(Path(actual.__file__).resolve()) == HOUR_ROOT + '/' + WORKER == task['migration_worker'],
            'Task.migration_worker must explicitly be the real current SCUT hour worker')
    ns, binding, actual_cfg = actual.load_original(task, out)
    require(task.get('_env') is None and not actual_cfg,
            'load_original must not construct/reset/advance an environment')
    wrapped = ns['runner_config']
    require(inspect.isfunction(wrapped) and wrapped.__module__ == actual.__name__,
            'Named actual-hour runner_config wrapper identity differs')
    closure = inspect.getclosurevars(wrapped).nonlocals
    require('original_runner_config' in closure, 'Source-verified original_runner_config closure absent')
    original = closure['original_runner_config']
    require(inspect.isfunction(original) and original.__globals__ is ns and
            original.__name__ == 'runner_config' and
            Path(original.__code__.co_filename).resolve() == Path(ns['__file__']).resolve(),
            'Original E0 actor configuration function identity differs')
    # Training-only wrapper pins formal6cd LR. Frozen evaluation constructs NO
    # runner/critic/optimizer; keep the original actor cfg function itself and
    # expose actual candidate FINAL.live_core LR, never fabricate formal6cd LR.
    require(task['source_LR'] == task['checkpoint_LR'] == task['candidate_live_core']['source_LR'] and
            task['source_iteration'] == task['checkpoint_iteration'] == task['candidate_live_core']['iteration'],
            'One FINAL.fullsave.live_core must own candidate LR and iteration')
    ns['args'].learning_rate = task['checkpoint_LR']
    ns['runner_config'] = original
    task['_SCUT_actor_config_binding'] = dict(
        original_function_recovered_from_named_actual_hour_closure=True,
        original_actor_configuration_function_unmodified=True,
        training_only_formal_LR_assertion_not_called=True,
        candidate_LR=task['checkpoint_LR'], candidate_iteration=task['checkpoint_iteration'],
        candidate_metadata_origin='FINAL.fullsave.live_core',
        no_PPO_implementation_or_live_critic_optimizer=True)
    return ns, binding, actual_cfg


def observed_binding(task, env, actual_cfg, torch, phase):
    require(phase in ('BEFORE_SOLE_RESET', 'AFTER_SOLE_RESET', 'AFTER_FINITE_EVAL'), 'Named binding boundary')
    cmd, reward = task['_scut_cmd'], task['_scut_reward']
    sources = task['_scut_adapter_sources']
    require(set(sources) == set(ADAPTER_SHA), 'Exact actual loader adapter source set')
    for name, wanted in ADAPTER_SHA.items():
        require(sources[name]['SHA256'] == wanted and sources[name]['path'] == HOUR_ROOT + '/' + name + '.py',
                'Pinned actual source adapter path/SHA differs: ' + name)
    require(task['_scut_cmd_configure']['task'] == task['_scut_cmd_bind']['task'] == TASK and
            actual_cfg['scut_reward_configure']['task'] == TASK,
            'Actual constructor command/reward configure and command.bind receipts required')
    cfg = field(env, 'cfg')
    require(env.num_envs == 80 and cfg.scene.num_envs == 80 and
            env.physics_dt == .0025 and env.step_dt == .02 and cfg.decimation == 8,
            'Actual original N80 physical interface')
    command = env.command_manager.get_term('twist')
    require(type(command) is cmd.ScutV14FlatCommand and cfg.commands.twist.class_type is cmd.ScutV14FlatCommand and
            command.training_iteration == task['candidate_live_core']['iteration'] == task['source_iteration'],
            'Actual SCUT command class/real candidate iteration differs')
    require(field(env, '_scut_v14_bound') is True and
            cfg.terminations.scut_v14.func is cmd.scut_termination and
            cfg.terminations.time_out.func is cmd.scut_time_out and cfg.terminations.time_out.time_out is True,
            'Actual SCUT done/timeout binding missing')
    terms = list(env.termination_manager.active_terms)
    require({'scut_v14', 'time_out', 'closure', 'mimic'} <= set(terms) and
            not ({'bad_orientation', 'base_contact', 'low_base', 'tunnel_roof_hit'} & set(terms)),
            'Original hardware rules plus SCUT performance/timeout terms required')
    require(cfg.terminations.closure.params['threshold'] == .01 and
            cfg.terminations.mimic.params['threshold'] == .01, 'Original .01 hardware gates')
    active = list(env.reward_manager.active_terms)
    require(active == list(reward.ACTIVE_WEIGHTS) and len(reward.REWARD_WEIGHTS) == 37 and len(active) == 26,
            'Actual original 37/26 reward order')
    weights = {}
    for name in active:
        term = env.reward_manager.get_term_cfg(name)
        require(term.func is reward._raw_term and term.weight == reward.ACTIVE_WEIGHTS[name] and
                term.params == {'name': name}, 'Actual SCUT reward term differs: ' + name)
        weights[name] = float(term.weight)
    controls = int(field(env, 'common_step_counter'))
    state = getattr(env, reward.STATE_NAME, None)
    reward_last_step = None
    cached_shape = None
    if phase == 'BEFORE_SOLE_RESET':
        require(state is None, 'Reward must bind once only after the sole fresh reset')
    else:
        require(type(state) is reward._RewardState and state.env is env and state.manager is env.reward_manager and
                tuple(state.prev.shape) == tuple(state.prevprev.shape) == (80, 6),
                'Actual unmodified reward.bind state/history ownership')
        require(task['_scut_reward_bind']['abi'] == 'SCUT_V14_FLAT_REWARD_V1' and
                task['_scut_reward_bind']['active_weights'] == weights,
                'Actual reward.bind receipt missing or changed')
        reward_last_step = int(state.last_step)
        require(reward_last_step == controls, 'Reward/control alignment differs')
        # Read only the already populated sensor cache, never .data/refresh/_inputs.
        data = field(state.sensor, '_data')
        history = tensor_view(field(data, 'net_forces_w_history'), torch, 'cached SCUT reward contact history')
        cached_shape = list(history.shape)
        require(tuple(history.shape) == (80, 3, len(state.sensor.body_names), 3),
                'Cached source reward contact [N,3,B,3] gate differs')
        require(state.sensor.cfg.history_length == 3 and state.sensor.cfg.update_period == .005,
                'Original reward contact-history clock')
    if phase in ('BEFORE_SOLE_RESET', 'AFTER_SOLE_RESET'):
        require(controls == 0 and int(env._sim_step_counter) == 0 and int(env._integrated_contact.tick) == 0,
                'Exactly zero precontrols at SCUT binding boundary')
    else:
        require(controls == task['controls'] == 1000, 'Original finite SCUT control count')
        # mod4_task.closure_broken/mimic_broken publish these per-env cached
        # tensors during original termination compute. Do not synthesize zeros
        # when a real observer field is absent; do not recompute the algorithms.
        for name in ('_mod4_closure_now', '_mod4_mimic_now'):
            metric = tensor_view(field(env, name), torch, 'cached original hardware observer ' + name)
            require(tuple(metric.shape) == (80,) and bool(torch.isfinite(metric).all()),
                    'Unknown: cached original hardware observer ABI differs: ' + name)
    return dict(mode=MODE, task=TASK, phase=phase, role='E0', num_envs=env.num_envs,
        actual_command_class=type(command).__module__ + '.' + type(command).__qualname__,
        real_candidate_iteration=command.training_iteration, controls=controls,
        command_done_bound=True, reward_configured=True, reward_bound=state is not None,
        active_reward_weights=weights, original_ordered_weights=list(reward.REWARD_WEIGHTS.items()),
        actual_termination_terms=terms, actual_adapter_sources=sources,
        reward_last_step=reward_last_step, cached_contact_history_shape=cached_shape,
        cached_sensor_read_only=True, no_extra_reset_observation_RNG_or_precontrol=True,
        reward_and_cached_sensor_algorithms_unmodified=True,
        actor_config_binding=task['_SCUT_actor_config_binding'], skill_grader=None, full_skill_graduation=None)


def before_sole_reset(task, env, actual_cfg, torch):
    task['_SCUT_before_reset_binding'] = observed_binding(task, env, actual_cfg, torch, 'BEFORE_SOLE_RESET')


def bind_after_sole_reset(task, env, actual_cfg, torch):
    require(task['_SCUT_before_reset_binding']['controls'] == 0 and
            getattr(env, task['_scut_reward'].STATE_NAME, None) is None,
            'Source-prescribed prebind/sole-reset boundary')
    task['_scut_reward_bind'] = task['_scut_reward'].bind(env)
    task['_SCUT_eval_binding'] = observed_binding(task, env, actual_cfg, torch, 'AFTER_SOLE_RESET')
'''


SCUT_TRAIN_GATE = r''' need(closed['cases']['E0']['ERROR_JSON']=={} and closed['metadata']['OWNER_ORIGINAL_ERROR.json'] is None,'Unknown: own training ERROR must be absent')
 need(wait['semantic_qualification']['errors']==[] and bool(wait['semantic_qualification']['checks']) and all(v is True for v in wait['semantic_qualification']['checks'].values()),'Every actual waited semantic check must pass')
 need(final['worker_pid']==wait['semantic_qualification']['actual_child_pid'] and final['parent_pid']==wait['semantic_qualification']['actual_parent_pid']==closed['metadata']['OWNER_STARTED.json']['pid'],'Actual SCUT training child/parent identity')
 need(final['window_mode']==save['window_mode']==SCUT_MODE and final['requested_update_quota'] is None and final['hour_not_started'] is False and final['stop_reason'] in ('STOP_SAVE','save_deadline'),'Actual SCUT finite wall-clock hour FINAL, not prior probe/non-SCUT/U000')
 need(final['source_env_state_applied'] is False and final['source_once1'] is True and final['actual_original_runner_learn_calls']==1 and final['learnedstate']['complete_original_actor_critic_STD6_Adam17_LR_normalizer'] is True,'Complete actual SCUT learner/source-once/fresh physical boundary')
 need(final['target_asset_SHA']==EXPECTED_ASSET_SHA and final['target_contract_SHA']==EXPECTED_CONTRACT_SHA,'Exact D6 producer asset/contract')
 need(all(final['source_IO'][k]==1 for k in ('physical_byte_opens','SHA_calculations','CPU_decodes')),'Actual once-only source byte/hash/CPU decode')
 need(save['actual_optimizer_steps']==final['actual_optimizer_steps'] and save['actual_rollout_controls']==final['actual_rollout_controls'],'Same FINAL/save actual counters only; no arithmetic labels')
 need(all(save[k] is True for k in ('own_roundtrip_full_tree_exact','command_done_and_reward_history_saved','actual_cfg_and_source_SHA_saved')),'Complete original SCUT state/config/source full-save evidence')
 initial=closed['cases']['E0']['SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json']
 exact7=('actor_exact','critic_exact','normalization_exact','learned_STD_exact','Adam17_exact','LR_exact','iteration_exact')
 need(initial==final['initial_checkpoint_acceptance'] and initial['schema']=='mod4v2.e0.scut_initial_checkpoint_acceptance.v1' and initial['role']=='E0' and initial['run_id']==final['run_id'] and initial['worker_pid']==final['worker_pid'] and initial['task_sha256']==final['task_sha256'],'Standalone and FINAL U000 receipt exact identity')
 need(initial['mode']==SCUT_MODE and initial['accepted'] is True and initial['passed'] is True and all(initial[k] is True for k in exact7) and initial['source_SHA']==FORMAL_SOURCE_SHA,'Actual formal6cd U000 exact7 acceptance')
 need(initial['source_core']==initial['saved_core']==save['source_core']==final['learnedstate']['source_core'],'U000 complete source/saved core exact, separate from current live_core')
 need(initial['source_once1'] is True and initial['source_immutable_CPU_tree_exact'] is True and initial['own_full_save_roundtrip_exact'] is True and initial['statistics_invented'] is False and initial['source_environment_state_applied'] is False,'Actual complete immutable initial checkpoint, no invented state')
 need(initial['actual_PPO_updates']==initial['actual_Adam_steps']==initial['actual_PPO_rollout_controls']==0 and initial['native_zero_controls_not_PPO']==1,'U000 accepted before all PPO, separate native admission only')
 need(initial['actual_save']==initial['latest_complete_save'] and initial['checkpoint']==initial['actual_save']['path'] and initial['bytes']==initial['actual_save']['bytes'] and initial['SHA']==initial['actual_save']['sha256'],'Exact U000 complete save metadata')
 need(latest['path']!=initial['checkpoint'] and latest['sha256']!=initial['SHA'],'FINAL latest candidate must not be first V2_COMPLETE_SAVE/U000')
 need(final['recipe_binding']['mode']==SCUT_MODE and final['recipe_binding']['task']==SCUT_TASK,'Actual SCUT recipe, not renamed old E0 evaluation')
'''


PARENT_SCUT_CHECKS = r'''   scut=f.get('actual_SCUT_binding') or {};scut_after=f.get('actual_SCUT_binding_after') or {};candidate=f.get('candidate_SCUT_cache_binding') or {};source=f.get('migration_worker_source') or {}
   checks['explicit_actual_SCUT_hour_worker']=task['migration_worker']==expect['migration_worker']==source.get('path') and source.get('SHA')==expect['migration_worker_SHA']
   checks['qualified_SCUT_hour_U000_exact7_gate']=task['training_window_mode']==scut.get('mode')==scut_after.get('mode')=='SCUT_V14_ORIGINAL_FINITE_WALL_CLOCK_HOUR' and task['migration_cohort_close_receipt'].get('U000_exact7') is True and task['migration_cohort_close_receipt'].get('training_window_mode')==task['training_window_mode']
   checks['actual_SCUT_cmd_done_reward_binding']=ready.get('actual_SCUT_binding')==scut and all(x.get('task')=='Robotics-Wheelbipe-V14-Flat-v0' and x.get('command_done_bound') is True and x.get('reward_configured') is True and x.get('reward_bound') is True and x.get('real_candidate_iteration')==expect['checkpoint_iteration'] and x.get('cached_sensor_read_only') is True and x.get('no_extra_reset_observation_RNG_or_precontrol') is True and x.get('reward_and_cached_sensor_algorithms_unmodified') is True for x in (scut,scut_after)) and scut.get('controls')==0 and scut_after.get('controls')==scut_after.get('reward_last_step')==1000 and scut.get('active_reward_weights')==scut_after.get('active_reward_weights')
   checks['SCUT_candidate_whole_CPU_provenance']=ready.get('candidate_SCUT_cache_binding')==candidate and candidate.get('mode')==expect['training_window_mode'] and candidate.get('same_FINAL_live_core') is True and candidate.get('U000_exact7') is True and candidate.get('actual_new_updates')==expect['candidate_actual_updates'] and candidate.get('physical_history_applied') is False
   checks['original_actor_config_only_binding']=all((x.get('actor_config_binding') or {}).get('original_actor_configuration_function_unmodified') is True and (x.get('actor_config_binding') or {}).get('no_PPO_implementation_or_live_critic_optimizer') is True and (x.get('actor_config_binding') or {}).get('candidate_LR')==expect['checkpoint_LR'] for x in (scut,scut_after))
'''


CACHE_SCUT_CHECKS = r'''    need(migration['window_mode'] == task['training_window_mode'] == frozen_factory.MODE and
         migration['requested_effective_update_quota'] is None and migration['hour_not_started'] is False and
         migration['source_SHA'] == task['formal_source_SHA'] and migration['source_once1'] is True and
         migration['iteration_published_by_original_runner'] is True and migration['iteration_label_rewritten'] is False and
         migration['old_physical_state_restored'] is False and migration['source_env_state_applied'] is False and
         migration['source_unknowns_are_CPU_history_not_live_state'] is True,
         'Actual complete SCUT candidate metadata, not a renamed non-SCUT/probe/partial checkpoint')
    initial = migration['initial_checkpoint_acceptance']
    exact7 = ('actor_exact', 'critic_exact', 'normalization_exact', 'learned_STD_exact', 'Adam17_exact', 'LR_exact', 'iteration_exact')
    need(initial == task['initial_checkpoint_acceptance'] and initial['passed'] is True and initial['accepted'] is True and
         all(initial[k] is True for k in exact7) and initial['mode'] == frozen_factory.MODE and
         initial['source_SHA'] == task['formal_source_SHA'], 'Cached actual SCUT U000 exact7 receipt')
    need(migration['actual_new_updates'] == task['candidate_actual_updates'] and
         migration['actual_optimizer_steps'] == task['candidate_actual_optimizer_steps'] and
         migration['actual_rollout_controls'] == task['candidate_actual_rollout_controls'],
         'Candidate counters must agree with the same actual FINAL/save, never calculated labels')
    need(task['_hour_cpu_core_reader'](cache.state, torch) == task['candidate_live_core'],
         'Whole CPU candidate core must equal FINAL.fullsave.live_core directly')
    task['_candidate_SCUT_cache_binding'] = dict(mode=migration['window_mode'], same_FINAL_live_core=True,
        U000_exact7=True, actual_new_updates=migration['actual_new_updates'], physical_history_applied=False)
'''


def make_stage(original, worker_sha):
    s = Edits(original)
    s.all('E0_HOUR_FROZEN', PREFIX)
    s.all(OLD_WORKER, WORKER)
    s.replace('import argparse,hashlib,json,math,os,posixpath,sys,time', 'import argparse,ast,hashlib,json,math,os,posixpath,sys,time')
    s.replace('E0_HOUR_WINDOW_CLOSED_RESULT_PATH.json', 'E0_SCUT_HOUR_CLOSED_RESULT_PATH.json')
    s.replace('SOURCE_PLAN_E0_HOUR_WINDOW_ACTUAL_V1.json', 'SOURCE_PLAN_E0_SCUT_HOUR_ACTUAL_V1.json')
    closed_anchor = " closed_path,closed=closed_input(args.closed)"
    s.replace(closed_anchor, " need(args.closed.resolve()==(D/FRONTDOOR['closed_pointer']).resolve(),'Unknown: exact E0_SCUT_HOUR_CLOSED_RESULT_PATH.json frontdoor required')\n" + closed_anchor)
    s.replace(OLD_HOUR_ROOT, HOUR_ROOT)
    constants = '\n'.join((
        'SCUT_MODE=' + repr(MODE), 'SCUT_TASK=' + repr(SCUT_TASK),
        'FORMAL_SOURCE_SHA=' + repr(FORMAL_SHA), 'EXPECTED_ASSET_SHA=' + repr(ASSET_SHA),
        'EXPECTED_CONTRACT_SHA=' + repr(CONTRACT_SHA), 'SCUT_ADAPTER_SHA=' + repr(ADAPTER_SHA),
        'EXPECTED_HOUR_WORKER_SHA=' + repr(worker_sha),
    ))
    s.replace("OWN='/home/lc01/Zonglin Li/zonglin2'", "OWN='/home/lc01/Zonglin Li/zonglin2'\n" + constants)
    epoch = " epoch=max(float(end['epoch']),float(outer['epoch']),float(wait['owner_received_terminal_epoch']))"
    s.replace(epoch, SCUT_TRAIN_GATE.rstrip() + '\n' + epoch)
    s.replace("actual_child_semantic_qualification=wait['semantic_qualification'])",
              "actual_child_semantic_qualification=wait['semantic_qualification'],training_window_mode=SCUT_MODE,U000_exact7=True,formal_source_SHA=FORMAL_SOURCE_SHA)")
    old = " old=train_plan['entries'][0];need(latest['path']!=old['source_path'] and latest['sha256']!=old['source_SHA'],'New actual candidate, not original 6cd mother')"
    s.replace(old, old + "\n need(old['worker_argv'][0]==closed['root']+'/" + HOUR_WORKER + "' and old['source_SHA']==FORMAL_SOURCE_SHA,'Exact current SCUT hour plan worker/formal source')\n need(sha((D/'" + HOUR_WORKER + "').read_bytes())==EXPECTED_HOUR_WORKER_SHA,'Unknown: current local hour worker source changed since preparation')")
    payload = "  '" + FACTORY + "':(D/'" + FACTORY + "').read_bytes(),"
    s.replace(" payload={'" + PREFIX + "_parent.py':", " payload={\n" + payload + "\n  '" + PREFIX + "_parent.py':")
    before_marker = " put(marker,dict(epoch=time.time(),root=root,run_id=run,closed_path=str(closed_path),source_checkpoint_operations=0,SDK_GPU_C_locks_GO=0,no_samepurpose_retry=True))"
    new_payload_sources = (PREFIX + '_parent.py', WORKER, FACTORY)
    s.replace(before_marker,
              " for rel in " + repr(new_payload_sources) + ":\n  raw_source=payload[rel];ast.parse(raw_source,filename=rel);compile(raw_source,rel,'exec')\n" + before_marker)
    s.replace("migration_worker=closed['root']+'/worker_mod4v2_expert_migration_hour_v5.py'",
              "migration_worker=closed['root']+'/" + HOUR_WORKER + "',migration_worker_SHA=EXPECTED_HOUR_WORKER_SHA,training_window_mode=SCUT_MODE,formal_source_SHA=FORMAL_SOURCE_SHA,SCUT_adapter_SHA=SCUT_ADAPTER_SHA,candidate_live_core=core,candidate_actual_updates=final['completed_actual_updates'],candidate_actual_optimizer_steps=final['actual_optimizer_steps'],candidate_actual_rollout_controls=final['actual_rollout_controls'],initial_checkpoint_acceptance=final['initial_checkpoint_acceptance']")
    actual_task = "   need(actual_task['original_entry']=='runtime/isaac/mod4/train_mod4v1_e0.py','Original family E0 entry unchanged')"
    s.replace(actual_task, actual_task + "\n   need(actual_task['window_mode']==SCUT_MODE and actual_task['source_SHA']==FORMAL_SOURCE_SHA and actual_task['num_envs']==20000 and actual_task['seed']==20260928,'Actual SCUT training TASK, not frozen eval or a probe')\n   need(get_train_json('roles/E0/production/SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json')==final['initial_checkpoint_acceptance'],'Own remote U000 receipt differs from actual CLOSED snapshot')")
    return s.finish()


def make_parent(original):
    s = Edits(original)
    s.all('E0_HOUR_FROZEN', PREFIX)
    anchor = "   checks['original_env_close_returned']="
    s.replace(anchor, PARENT_SCUT_CHECKS + anchor)
    changed = s.finish()
    # Resource/accounting/cleanup/waits and all time bounds are untouched.
    same_definitions(original, changed.replace(PREFIX, 'E0_HOUR_FROZEN'),
                     ('main', 'settle_own_card', 'nvidia', 'make_task'))
    return changed


def make_worker(original):
    s = Edits(original)
    s.all('worker_mod4v2_expert_migration_hour_v5.py', HOUR_WORKER)
    s.replace('from types import SimpleNamespace', 'from types import SimpleNamespace\nimport ' + PREFIX + '_factory as frozen_factory')
    task_anchor = "    task['_migration_closed'] = closed"
    s.replace(task_anchor,
              "    need(closed['training_root'] == frozen_factory.HOUR_ROOT and closed['training_window_mode'] == frozen_factory.MODE and\n         closed['U000_exact7'] is True and closed['actual_child_semantic_qualification']['qualified'] is True and\n         closed['actual_child_semantic_qualification']['errors'] == [] and\n         task['migration_worker'] == frozen_factory.HOUR_ROOT + '/' + frozen_factory.WORKER,\n         'Actual current SCUT CLOSED/qualified/U000 identity required')\n" + task_anchor)
    s.replace("    def cpu_only(value):", CACHE_SCUT_CHECKS + "    def cpu_only(value):")
    s.replace('    from mild_dr import tensor',
              "    def tensor(value):\n        return frozen_factory.tensor_view(value, torch, 'original finite observer/fresh DR field')")
    s.replace("        env.reset()\n        if book is not None:",
              "        frozen_factory.before_sole_reset(task, env, actual_cfg, torch)\n        env.reset()\n        frozen_factory.bind_after_sole_reset(task, env, actual_cfg, torch)\n        if book is not None:")
    s.replace("    if not torch.is_tensor(limits):\n        import warp as wp\n        limits = wp.to_torch(limits)",
              "    limits = frozen_factory.tensor_view(limits, torch, 'actual fresh native DOF limits')")
    s.replace("    need(tuple(limits.shape[-2:]) == (len(names), 2), 'Actual native DOF limit ABI differs')",
              "    need(tuple(limits.shape) == (80, len(names), 2), 'Unknown: actual native DOF [80,joints,2] ABI differs')")
    s.replace("        actual_native_static=native, actor=actor_receipt, route_scope=bundle['route_scope'],",
              "        actual_native_static=native, actor=actor_receipt, route_scope=bundle['route_scope'],\n        actual_SCUT_binding=task['_SCUT_eval_binding'], candidate_SCUT_cache_binding=task['_candidate_SCUT_cache_binding'],")
    s.replace("    result.update(schema=SCHEMA, kind=KIND, execution=True, passed_execution=True,",
              "    scut_after = frozen_factory.observed_binding(task, env, actual_cfg, torch, 'AFTER_FINITE_EVAL')\n    result.update(schema=SCHEMA, kind=KIND, execution=True, passed_execution=True,\n        actual_SCUT_binding=task['_SCUT_eval_binding'], actual_SCUT_binding_after=scut_after,\n        candidate_SCUT_cache_binding=task['_candidate_SCUT_cache_binding'],")
    s.replace("        migration = source_module(migration_path, '_mod4v2_eval_original_factory_helper')",
              "        need(str(migration_path) == frozen_factory.HOUR_ROOT + '/' + frozen_factory.WORKER and\n             hashlib.sha256(migration_path.read_bytes()).hexdigest() == task['migration_worker_SHA'],\n             'Unknown: exact real SCUT hour worker path/source SHA differs')\n        migration = source_module(migration_path, '_mod4v2_eval_original_factory_helper')\n        task['_hour_cpu_core_reader'] = migration.adam_core")
    s.replace('        ns, binding, actual_cfg = migration.load_original(task, out)',
              '        ns, binding, actual_cfg = frozen_factory.load_original(migration, task, out)')
    changed = s.finish()
    same_definitions(original, changed,
        ('put', 'fail', 'source_module', 'check_stop', 'wait_start', 'frozen_actor', 'RouteV2',
         'actual_identity', 'five_loop', 'close_resources', 'failed_cache_receipt'))
    tree = ast.parse(changed)
    need(not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and
                 n.func.attr == 'native_initialized' for n in ast.walk(tree)), 'No native initializer call')
    fresh = named_node(changed, 'fresh_bundle')
    reset_calls = [n for n in ast.walk(fresh) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'reset']
    need(len(reset_calls) == 1, 'Same sole explicit eval reset, no zero-control addition')
    return changed


def make_factory():
    result = textwrap.dedent(FACTORY_SOURCE)
    for token, value in (('__SCUT_MODE__', MODE), ('__SCUT_TASK__', SCUT_TASK),
                         ('__HOUR_ROOT__', HOUR_ROOT), ('__HOUR_WORKER__', HOUR_WORKER),
                         ('__ADAPTER_SHA__', ADAPTER_SHA)):
        need(result.count(token) == 1, 'one factory constant placeholder ' + token)
        result = result.replace(token, repr(value))
    tree = ast.parse(result)
    blocked = {'native_initialized', 'learn', 'step', 'reset', 'compute', 'manual_seed',
               'seed', 'load_state_dict', 'set_state', 'restore_state', 'update'}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            need(node.func.attr not in blocked, 'binding-only factory has no direct ' + node.func.attr)
    return result


def validate_source(path, text):
    tree = ast.parse(text, filename=str(path))
    compile(tree, str(path), 'exec', dont_inherit=True)
    # The dispatcher's controller and launch source are also syntax-checked as
    # source, never executed. __ROOT__/__PLAN_SHA__ are valid placeholder names.
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.startswith('from pathlib import Path\n'):
            count += 1
            label = str(path) + ':embedded-' + str(count)
            embedded = ast.parse(node.value, filename=label)
            compile(embedded, label, 'exec', dont_inherit=True)
    if path.name.endswith('_dispatch_once.py'):
        need(count == 2, 'Both original controller/launch sources checked')


def main():
    hour = source(HOUR_WORKER)
    tree = ast.parse(hour, filename=str(D / HOUR_WORKER))
    constants = {n.targets[0].id: n.value for n in tree.body if isinstance(n, ast.Assign) and
                 len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)}
    need(ast.literal_eval(constants['SCUT_MODE']) == MODE and
         ast.literal_eval(constants['SCUT_TASK']) == SCUT_TASK and
         ast.literal_eval(constants['SCUT_ADAPTER_SHA']) == ADAPTER_SHA, 'Current actual hour constants')
    loader = ast.get_source_segment(hour, named_node(hour, 'load_original'))
    for anchor in ("original_runner_config = ns['runner_config']", "ns['runner_config'] = runner_config",
                   "task['_scut_cmd_configure'] = cmd.configure(cfg, ns['mod4_task'])",
                   "actual_cfg['scut_reward_configure'] = reward.configure(cfg, ns['mod4_task'])",
                   "task['_scut_cmd_bind'] = cmd.bind(env)",
                   "cmd.set_training_iteration(env, task['source_iteration'])"):
        need(loader.count(anchor) == 1, 'Source-verified actual factory binding ' + anchor)
    need(not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in
                 ('reset', 'step', 'native_initialized') for n in ast.walk(named_node(hour, 'load_original'))),
         'Actual load_original is construction/config only; no reset/zero/native call')
    for name, wanted in ADAPTER_SHA.items():
        raw = (D / (name + '.py')).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == wanted, 'Pinned unchanged actual SCUT adapter ' + name)
    # Preserve actual byte identity; no newline/BOM normalization in the SHA.
    worker_sha = hashlib.sha256((D / HOUR_WORKER).read_bytes()).hexdigest()
    outputs = {
        D / (PREFIX + '_stage.py'): make_stage(source('E0_HOUR_FROZEN_stage.py'), worker_sha),
        D / (PREFIX + '_parent.py'): make_parent(source('E0_HOUR_FROZEN_parent.py')),
        D / WORKER: make_worker(source(OLD_WORKER)),
        D / FACTORY: make_factory(),
    }
    for kind in ('dispatch_once', 'collect_once'):
        original = source('E0_HOUR_FROZEN_' + kind + '.py')
        edits = Edits(original)
        edits.all('E0_HOUR_FROZEN', PREFIX)
        outputs[D / (PREFIX + '_' + kind + '.py')] = edits.finish()
    need(len(outputs) == 6, 'Only six independent new source outputs; no report/manifest/test')
    for path, text in outputs.items():
        need(path.parent == D and path.name.startswith(PREFIX + '_') and not path.exists(),
             'Exclusive new namespace only, existing output must not be overwritten: ' + str(path))
        validate_source(path, text)
    # All sources, controllers, original-function ASTs and bounded inverses have
    # passed before ANY publication. Mode x gives a second no-overwrite barrier.
    for path, text in outputs.items():
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
    print('Published exactly six NEW SCUT E0 frozen sources; stage requires actual CLOSED current hour, qualified FINAL/latest/live_core and U000 exact7. No stage/dispatch/eval/SDK/model operation performed by this preparer.')
    for path in outputs:
        print(path)


if __name__ == '__main__':
    main()
