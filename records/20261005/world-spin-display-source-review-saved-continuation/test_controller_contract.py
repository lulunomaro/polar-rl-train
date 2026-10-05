"""CPU control contracts. Does not instantiate a simulator or start workers."""
import ast,copy,json,math,sys,types
from pathlib import Path
D=Path(__file__).resolve().parent;O=D/'overrides'
checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
for p in O.rglob('*.py'):ast.parse(p.read_text(encoding='utf8'))
check('all_candidate_python_syntax',True)
tree=ast.parse((O/'supervise_world_spin.py').read_text())
functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
lesson=functions['run_lesson']
calls=lambda name:[ast.unparse(n.func) for n in ast.walk(functions[name]) if isinstance(n,ast.Call)]
check('one_shot_state_guard','assert not STATE.exists()' in ast.unparse(functions['controller']))
check('sole_canonical_locked','helpers.acquire' in calls('controller') and 'native_floor_supervisor.lock' in ast.unparse(functions['controller']))
check('original_spin_final_preserved','AUTONOMY_FINISHED.json' not in [str(n.args[0]) for n in ast.walk(functions['finish']) if isinstance(n,ast.Call) and ast.unparse(n.func)=='base.atomic_json'])
preflights=[n.value for n in ast.walk(lesson) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='ctl.training']
check('preflight_weights_discarded',len(preflights)==2 and {next(k.value.value for k in c.keywords if k.arg=='iterations') for c in preflights}=={2,4})
check('full_state_training_reused_no_copy','training' not in functions and 'ctl.training' in calls('run_lesson'))
check('physical_and_old_skills_before_PPO',ast.unparse(lesson).index("probe(ck, '20k'")<ast.unparse(lesson).index('baseline = regression(ck,')<ast.unparse(lesson).index("ctl.training(ck, 'world_128_discard'"))
check('intermediate_quality_not_a_veto',any(ast.unparse(n.test)=='goal != 0.5' and len(n.body)==1 and isinstance(n.body[0],ast.Break) for n in ast.walk(lesson) if isinstance(n,ast.If)))
check('no_old_quality_gate_calls',not any(x in calls('probe')+calls('paired')+calls('run_lesson') for x in ('ctl.gate','ctl.current_decision','rate.assess','ctl.safety_veto')))
check('three_goals_registered','for goal in (0.15, 0.3, 0.5)' in ast.unparse(lesson))
check('two_seeds_and_retention_pairs',"for seed in (20261002, 20261003)" in ast.unparse(functions['paired']) and "('flat', 'spin', 'world')" in ast.unparse(functions['paired']))
check('effective_exposure_from_canonical',"charged_training_seconds" in ast.unparse(lesson) and 'exposure += time.time()' not in ast.unparse(lesson))
class Base:
 def budget_state(self):return dict(authorized_training_seconds=324000)
 def status(self,**kw):self.output=kw
b=Base();ns=dict(read=lambda p:dict(RM_SPIN_WORLD_PROGRESS_M_S='.15'),CODE=Path('.'),base=b,D=Path('.'),ctl=types.SimpleNamespace(CANONICAL=Path('sole')),os=types.SimpleNamespace(getpid=lambda:123),math=math)
exec(compile(ast.Module(body=[functions['status']],type_ignores=[]),'status-contract','exec'),ns)
ns['status']('training',budget_seconds=324000,authorized_training_seconds=324000,training_pid=456)
check('training_status_duplicate_defaults_handled',b.output['training_pid']==456 and b.output['authorized_training_seconds']==324000)
# Factual target confirmation: these values never affect physical/learning gates.
module=types.ModuleType('scut_curriculum_gate_v4');module.assess=lambda r:dict(pass_=r.get('actual_evidence_pass',True));sys.modules[module.__name__]=module
ns={};exec((O/'world_progress_contract.py').read_text(),ns)
row=lambda i:dict(env_id=i,group_id=3+i%8,valid=True,complete_cycle_count=2,complete_prefix_along_m_s=.15,complete_prefix_cross_m_s=0.,command_yaw_rad_s=2.,cycles=[dict(duration_s=math.pi)],cross_peak_to_peak_m=.15)
r=dict(world_cycle_metrics=[row(i) for i in range(64)],per_environment=dict(yaw_rate=[2.]*64))
check('correct_full_circle_net_progress',ns['target'](r,.15)['pass_'])
bad=copy.deepcopy(r);bad['world_cycle_metrics'][0]['complete_prefix_along_m_s']=0
check('constant_body_zero_net_progress_rejected_as_target',not ns['target'](bad,.15)['pass_'])
bad=copy.deepcopy(r);bad['world_cycle_metrics'][0]['complete_cycle_count']=0
check('partial_turn_not_target_completion',not ns['target'](bad,.15)['pass_'])
bad=copy.deepcopy(r);bad['world_cycle_metrics'][0]['complete_prefix_along_m_s']=-.15
check('wrong_world_direction_not_target',not ns['target'](bad,.15)['pass_'])
bad=copy.deepcopy(r);bad['per_environment']['yaw_rate'][0]=-2
check('wrong_signed_yaw_not_target',not ns['target'](bad,.15)['pass_'])
bad=copy.deepcopy(r);bad['actual_evidence_pass']=False
check('real_model_data_failure_not_hidden',not ns['target'](bad,.15)['pass_'])
check('target_confirmation_separate_from_learning',ns['target'](bad,.15)['used_for_learning_veto'] is False)
result=dict(pass_=True,count=len(checks),checks=checks,no_simulation=True,no_PPO=True)
(D/'CONTROLLER_CPU_CONTRACT.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))
