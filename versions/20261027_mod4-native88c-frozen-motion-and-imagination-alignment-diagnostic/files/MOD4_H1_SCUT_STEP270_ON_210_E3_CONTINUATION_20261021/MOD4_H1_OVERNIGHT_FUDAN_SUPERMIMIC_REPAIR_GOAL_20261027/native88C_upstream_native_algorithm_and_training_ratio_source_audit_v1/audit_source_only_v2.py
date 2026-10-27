"""Read explicit local source files; AST and scalar arithmetic only. No imports of learner.

Unused as a runtime/admission tool. Does not inspect weights, raw data, USD or processes.
"""
from pathlib import Path
import ast
import copy
from datetime import datetime, timezone
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
L = HERE.parent
T = L.parent
B = T / 'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/payloads/h1'
S = B / 'source'
U = T / 'MOD4_UNISUPERMIMIC_WHEEL_LEG_SINGLE4090_TEST_20261026/upstream'
P = L / 'upstream_pinned_source'
FILES = {
 'upstream_README': U/'README.md',
 'upstream_learner': U/'src/unisupermimic/rl/algos/supermimic/learner.py',
 'upstream_networks': U/'src/unisupermimic/rl/algos/supermimic/networks.py',
 'upstream_replay': U/'src/unisupermimic/rl/algos/supermimic/replay.py',
 'upstream_config': P/'config.yaml',
 'upstream_receipt': P/'config_CONNECTOR_RECEIPT.json',
 'upstream_mdp': P/'mdp.py',
 'upstream_manager_terms': P/'manager_terms.py',
 'actual_learner': S/'supermimic_wheel_leg_v3/learner.py',
 'actual_networks': S/'supermimic_wheel_leg_v3/networks.py',
 'actual_replay': S/'supermimic_wheel_leg_v3/replay.py',
 'actual_augmented_WM': S/'supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py',
 'actual_training': S/'native_own_fudan88_gas400_training_v2.py',
 'actual_migration': S/'native88_gas400_migration_v1.py',
 'actual_restore': S/'same_architecture_native_continuation_candidate_v1.py',
 'actual_bridge': S/'native_wheel_leg_bridge_v4.py',
 'actual_mdp': S/'converted_MOD4_jump_mdp_v4.py',
 'actual_objective_v1': S/'own_step_differentiable_objective_v1.py',
 'actual_objective_v2': S/'own_step_differentiable_objective_v2.py',
 'actual_static': S/'compact_episode_static31_v1.py',
 'actual_queue_contract': S/'static_dynamic_delay_contract_v1.py',
 'actual_getter': S/'actual_DR_memory_getter_v1.py',
 'actual_trace': B/'h1_production_control_prefix_trace_v1.py',
 'actual_reset': B/'job0/runtime/isaac/mod4/scut_flat_rescue.py',
}

def put(name, value):
    with (HERE/name).open('x', encoding='utf-8', newline='\n') as f:
        else: json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')

def sha(data): return hashlib.sha256(data).hexdigest()

def functions(source):
    return {node.name: node for node in ast.walk(ast.parse(source))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

def main():
    source = {}; lineage = {}
    for key, path in FILES.items():
        assert path.suffix in ('.py','.md','.yaml','.json'), path
        raw = path.read_bytes()
        text = raw.decode('utf-8-sig')
        source[key] = text
        row = dict(path=str(path), bytes=len(raw), SHA=sha(raw))
        if path.suffix == '.py':
            tree = ast.parse(text)
            row['definitions'] = [dict(name=n.name, line=n.lineno, end_line=n.end_lineno,
                kind=type(n).__name__) for n in ast.walk(tree)
                if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]
        lineage[key] = row

    def evidence(key, fragment):
        hits = [i for i, line in enumerate(source[key].splitlines(),1) if fragment in line]
        assert hits, (key, fragment)
        return dict(source=key,path=lineage[key]['path'],SHA=lineage[key]['SHA'],
                    lines=hits,anchor=fragment)

    pairs = {}
    uf, af = functions(source['upstream_learner']), functions(source['actual_learner'])
    for name in ('_wm_err','wm_update','_sample_valid_starts','policy_update','lr_at',
                 '_imag_step','collect','train','_wm_rollout','_critic_input'):
        a,b = uf[name],af[name]
        da,db = ast.dump(a,include_attributes=False),ast.dump(b,include_attributes=False)
        row = dict(upstream_line=a.lineno,actual_line=b.lineno,AST_exact=da==db,
                   upstream_AST_SHA=sha(da.encode()),actual_AST_SHA=sha(db.encode()))
        if name=='policy_update':
            normalized=copy.deepcopy(b)
            for n in ast.walk(normalized):
                if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='range' and len(n.args)==1 and isinstance(n.args[0],ast.Constant) and n.args[0].value==7:
                    n.args[0].value=6
            row['AST_exact_after_only_State7_to_State6_range_normalization']=da==ast.dump(normalized,include_attributes=False)
        pairs[name]=row
    for key,name in (('networks','RunningNorm'),('replay','ReplayBuffer')):
        ut=ast.parse(source['upstream_'+key]); at=ast.parse(source['actual_'+key])
        uc=next(x for x in ast.walk(ut) if isinstance(x,ast.ClassDef) and x.name==name)
        ac=next(x for x in ast.walk(at) if isinstance(x,ast.ClassDef) and x.name==name)
        pairs[name]=dict(AST_exact=ast.dump(uc,include_attributes=False)==ast.dump(ac,include_attributes=False),upstream_line=uc.lineno,actual_line=ac.lineno)

    cfg_call=next(n for n in ast.walk(af.get('config_for', ast.parse(source['actual_training'])))
                  if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='SuperMimicConfig')
    cfg={k.arg:ast.literal_eval(k.value) for k in cfg_call.keywords if not isinstance(k.value,ast.Name)}
    assert cfg['utd']==.4 and cfg['wm_batches']==10 and cfg['wm_batch']==1024 and cfg['pi_batch']==1024 and cfg['horizon']==32
    def ratios(n,utd,batches,batch,horizon,pi_batch,window):
        real=n/utd
        return dict(num_envs=n,utd=utd,mean_controls_per_iteration=1/utd,
            mean_real_transitions_per_iteration=real,WM_window_starts_per_iteration=batches*batch,
            WM_window_starts_per_new_real_transition=batches*batch/real,
            WM_nominal_loss_timepoints_per_new_real_transition=None if window is None else batches*batch*window/real,
            imagined_policy_timepoints_per_new_real_transition=None if pi_batch is None else pi_batch*horizon/real)
    ratio = dict(actual=ratios(4096,.4,10,1024,32,1024,8),
        pinned_config=ratios(4096,.4,10,2048,32,4096,8),
        user_screenshot_conditional_same_UTD_definition=ratios(4096,2,5,8192,16,None,None),
        qualifications=['Long-run ratio; physical warmup/world-only iteration phase excluded.',
            'WM window masks reduce actual effective timepoints; overlapping windows are not independent samples.',
            'Screenshot code/link and UTD definition not verified; its WM window/Pi batch unspecified.',
            'UTD here is algorithm iterations per physical vector-control, not optimizer-steps per transition.'])
    lr = {str(i):dict(coefficient=.03+.97*.5*(1+math.cos(math.pi*i/250000)),
                     lr=2e-4*(.03+.97*.5*(1+math.cos(math.pi*i/250000))))
          for i in (0,1409,2677,3317,6469)}
    moments = {role:dict(new_WM=wm,new_Pi=pi,new_V_steps=pi*20,
        old_WM_second_moment_weight=.999**wm,old_Pi_second_moment_weight=.95**pi,
        old_V_second_moment_weight=.999**(pi*20))
        for role,wm,pi in (('h1',31520,3088),('recovery',12680,1204))}
    findings = [
      dict(id='F01',classification='preserved_native_algorithm',conclusion='Native policy BPTT and supervised autoregressive WM training remain. Frozen WM/critic parameters do not detach the rollout graph; policy loss backward traverses WM, soft reward, future observations and critic bootstrap. This is not a PPO surrogate.',evidence=[evidence('actual_learner','_set_requires_grad(self.wm, False)'),evidence('actual_learner','loss.backward()'),evidence('actual_learner','predicted = self._wm_rollout_fn'),evidence('actual_learner','self.opt_pi.step()')]),
      dict(id='F02',classification='deliberate_adapter_and_config_difference',conclusion='Actual WM10x1024 and Pi1024 are respectively half and quarter pinned-config batches; H32 matches pinned config, differs from screenshot H16. Current FP32/no compile differs from pinned BF16/compile. If screenshot UTD semantics match, its WM window-start/real-transition ratio is20 versus ours1, pinned2.',evidence=[evidence('actual_training','wm_window=8,wm_batches=10'),evidence('actual_training',"amp='none',compile=False"),evidence('upstream_config','wm_batch: 2048'),evidence('upstream_config','pi_batch: 4096'),evidence('actual_learner','step_accumulator += 1.0 / self.cfg.utd')]),
      dict(id='F03',classification='source_rule_out_large_LR_decay',conclusion='Global iteration continuation does preserve cosine LR phase, but at6469 coefficient remains about.9984. Current failure cannot be explained by a near-zero scheduled LR. All3 optimizer group LRs are reassigned every iteration.',evidence=[evidence('actual_learner','def lr_at'),evidence('actual_learner','group["lr"] = learning_rate'),evidence('actual_restore','load_state_dict')]),
      dict(id='F04',classification='changed_plant_adaptation_risk_not_proven_cause',conclusion='All models, normalizers and3 Adam states are preserved across700->400 and changed native reward.64 new world-only iterations adapt WM but not critic. First newPi bootstraps old-reward critic before subsequent critic fitting. Old Adam moments may matter initially; exponential carryover at FINAL is tiny, so permanent old-momentum dominance is unsupported. Cumulative normalizers have no forgetting and can preserve old-scale weighting longer.',evidence=[evidence('actual_restore','load_state_dict'),evidence('actual_migration','ready=iteration-self.source'),evidence('actual_learner','objective = objective +'),evidence('actual_learner','self.critic.norm.update'),evidence('actual_networks','if self.count >= self.max_count')]),
      dict(id='F05',classification='preserved_transition_semantics',conclusion='Replay stores actual clipped6 action ingress from original trace, not raw unbounded Pi proposal.30 applied torques/contact18/old processed6 are dynamic aux54, while true episode-static DR31 is fixed in imagination. Terminal state/aux are captured before original auto-reset; static cache updates only selected reset environments. Old dynamic-xi49 freezing bug is not present in currentC.',evidence=[evidence('actual_bridge',"applied_ingress=frame['executed6']"),evidence('actual_bridge',"frame['history5ms'],frame['applied_torque'],applied"),evidence('actual_bridge','def current'),evidence('actual_static','FIELDS='),evidence('actual_augmented_WM','next_state[6]-state[6]')]),
      dict(id='F06',classification='model_constraint_risk_not_runtime_bug_proof',conclusion='Aux54,30q and30dq all evolve by learned residuals. Exact differentiable four-substep actuator queue helper exists but is not called by active AugmentedWM. No explicit closed-chain projection, q-limit cost or closure/contact hard-termination is applied in imagined rollout. Pinned G1 reward has joint-limit penalty. Real physical queue/reset/hard limits remain. An imagined off-manifold shortcut is plausible but needs actual predicted-state evidence; no causal conclusion or new physical gate.',evidence=[evidence('actual_augmented_WM','d_q, d_dq, d_aux'),evidence('actual_objective_v2','def objective_terms'),evidence('upstream_mdp','w_joint_limit: float = -2.0'),evidence('actual_mdp','def soft_termination')]),
      dict(id='F07',classification='task_reset_sampling_difference',conclusion='Pinned manager samples adaptive reference-frame starts and resets to reference state; pinned MDP excludes starts whose horizon crosses clip end. MOD4 starts from real flat reset bank/age0, request100..179, and allows all imagination starts including held reference afterage300 and physical timeout vicinity. This is a major task-distribution/termination design difference, not permission to spawn airborne poses or alter original success.',evidence=[evidence('upstream_manager_terms','def start_bin_probabilities'),evidence('upstream_manager_terms','self.motion.ref_state(full_frames)'),evidence('upstream_mdp','def valid_imagination_start'),evidence('actual_mdp','def valid_imagination_start'),evidence('actual_reset','def consistent_reset')]),
      dict(id='F08',classification='definite_metadata_wording_mismatch_data_sign_pending',conclusion='Active objective uses signed world-Z contact force, not vector magnitude: relu(1-force_z). Source manifest describes worldZ consistently, but precontrol receipt label says soft_magnitude. Label is inaccurate; whether signedZ itself has wrong support sign requires actual same-state signedZ/norm/support observation. Do not silently replace sign/norm.',evidence=[evidence('actual_objective_v1','force_z=state[6]'),evidence('actual_objective_v1','contact_cost=alpha')]),
      dict(id='F09',classification='provenance_and_comparison_scope',conclusion='Local pinned Motphys repo explicitly identifies an independent downstream reproduction, not official original-author code. Demo screenshot project/source identity is pending. Speed/yaw/standing31min evidence cannot establish MOD4 dual-wheel270mm success and does not disprove nativeWM+BPTT. Global6469/2677 includes sourceR5; C new iterations3152/1268 are the relevant fresh changed-plant work, not fresh6469/2677.',evidence=[evidence('upstream_README','independent downstream reproduction'),evidence('upstream_receipt','faf7818')]),
    ]
    assert pairs['wm_update']['AST_exact']
    assert pairs['_wm_err']['AST_exact']
    assert pairs['lr_at']['AST_exact']
    assert pairs['policy_update']['AST_exact_after_only_State7_to_State6_range_normalization']
    assert 'advance_queue' not in source['actual_augmented_WM']
    result=dict(schema='mod4.native88C.local_pinned_algorithm_source_audit.v1',
        completed_UTC=datetime.now(timezone.utc).isoformat(),scope='source + AST + scalar arithmetic only',
        actual_execution=False,models_read_stat_hash_or_forward=False,GPU_SDK_scene_physics=False,
        upstream_commit_from_saved_receipt='faf7818e8abac3ec6abb8f00e6e904d3577f800b',
        config=cfg,AST_comparisons=pairs,ratios=ratio,global_LR=lr,old_Adam_carryover_formula= moments,
        critic_normalizer_cap_theoretical_Pi_updates=math.ceil(2e8/(33*1024)),
        theoretical_count_warning='No checkpoint tensor or actual count was inspected. Critic norm update counts include(H+1)*PiBatch eachPi; constructor/previous lineage counts require saved evidence before claiming actual cap state.',
        findings=findings,
        next_checks=['Obtain demo project/source link; verify algorithm/UTD definitions and task settings before matching speed claim.',
          'Use separately admitted same-state diagnostics: compare real vs imagined geometry, q limits/closure, contact signedZ/norm, action saturation and phasewise loss. No current runtime change.',
          'Inspect source-preserved critic targets/normalizer counts on existing qualified evidence only when authorized; distinguish warmup adaptation from lasting model/objective mismatch.',
          'Before another training window choose one bounded, typed experiment from those observations; do not reset optimizers/norms or raise UTD blindly.'])
    put('SOURCE_LINEAGE_AND_LINES_ACTUAL.json',lineage)
    put('AST_AND_RATIO_SOURCE_AUDIT_ACTUAL.json',result)
    put('ERROR_HISTORY_ACTUAL.json',dict(errors=[
        dict(kind='source_reader_output_truncation',runtime_failure=False,description='Previous helper-context final batch returned output exceeded context; no model/SDK/runtime execution. Re-read necessary bounded source slices.'),
        dict(kind='source_reader_output_truncation',runtime_failure=False,description='Two PowerShell rg source listings exceeded requested token budgets; all needed source/anchors re-read by explicit-file audit script. Raw source unchanged.')],
        previous_runtime_and_reader_errors='All originalC/R5 reports and source directories remain immutable; this audit creates no new training trial.'))
    print(json.dumps(dict(passed=True,source_files=len(lineage),AST_checks=pairs,lr=lr,output=str(HERE)),ensure_ascii=False))

if __name__=='__main__': main()
