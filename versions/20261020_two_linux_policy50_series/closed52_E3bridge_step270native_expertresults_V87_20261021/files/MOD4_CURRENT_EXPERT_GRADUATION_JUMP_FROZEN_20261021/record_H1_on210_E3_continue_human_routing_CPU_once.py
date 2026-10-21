from pathlib import Path
import json,time,shutil,hashlib,ast
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';T=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021';assert not T.exists();T.mkdir();(T/'reports').mkdir()
P=T/'candidate_uninstalled';shutil.copytree(B/'H1_step270_candidate_uninstalled',P,ignore=shutil.ignore_patterns('__pycache__'))
v=dict(epoch=time.time(),human_answer='保存退出后将210从E2转给H1，E3继续（推荐）',scope='After actual full save/SDKclose/all-own-child-exit/wholeCPU/original-cost settlement of C52, use210 for H1 new .270m step training and continue E3. Current healthy training is not interrupted.',current_training='MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021',do_not_call_generic_cohort53_preparer_or_deployer=True,cohort53_reserved_sources_retained_not_deleted=True,H1_source_SHA='cb118b2ac27cca44466fba9014f4583ee8db23fc2cb2d83c4034b15961178765',H1_Adam=674740,H1_policy_hz=100,E3_policy_hz=50,E3_source='Must bind actual latest closed52 full SHA/Adam after wholeCPU and original cost receipt; not yet available',H1_target_minimum_step_m=.270,H1_actual_future_training_GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',E3_GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',third_GPU_shared_frozen_eval_only=True,one_original_canonical_writer_same1548000_eight_extensions_and_safety_legacy_reserves=True,no_new_writer_or_current_root_or_budget_mutation=True,new_source_CPU_candidates_copied_not_remote_installed=True,pending_native_SDK_terrain_source_admission=True,no_actual_H1_GO_or_PPO=True)
(R/'H1_ON210_E3_CONTINUE_EXPLICIT_HUMAN_ROUTING_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,ensure_ascii=False,indent=2));(T/'reports/HUMAN_ROUTING_AUTHORITY_AND_CURRENT_BOUNDARY_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,ensure_ascii=False,indent=2))
# Controller candidates: minimum scheduling/identity changes, no account arithmetic changes.
base=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/bound_controllers';D=T/'controllers_candidate_uninstalled';D.mkdir()
common=(base/'three_slot_common_v1.py').read_text('utf8');owner=(base/'three_slot_finite_owner_v1.py').read_text('utf8')
newcommon=common.replace("'h1':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'","'h1':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'")
newowner=owner.replace("set(specs)=={'e2','recovery'}","set(specs)=={'h1','recovery'}").replace("cfg['deferred_experts']==['h1']","cfg['deferred_experts']==['e2']").replace("kind='Linux_AVAILABLE_E2_E3_'","kind='Linux_H1_STEP270_E3_' ")
old="source_qualification_kind=rows[key]['closed_source_CPU']['value']['kind']"
new="source_qualification_kind=(rows[key].get('closed_source_CPU') or rows[key].get('native_CPU'))['value'].get('kind','H1_STEP270_SOURCE_AND_NATIVE_CPU')"
assert old in newowner;newowner=newowner.replace(old,new)
assert newcommon!=common and newowner!=owner
for name,s in [('three_slot_common_v1.py',newcommon),('three_slot_finite_owner_v1.py',newowner)]:
 ast.parse(s);(D/name).open('x',encoding='utf8').write(s)
def functions(s):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
before=functions(common);after=functions(newcommon);assert before==after
assert 'sum(b.CAPS[k] for k in specs)+9400.860692501068+512+64800' in newowner
assert all(term in newowner for term in ('1548000',"len(c['budget_extensions'])==8",'actual_H1_prelaunch_v2_scope_admitted'))
proof=dict(epoch=time.time(),passed_source_AST=True,common_all_function_AST_exact=True,common_only_GPU_identity_literal_change=True,owner_explicit_routing_differences=['scheduled keys e2/recovery to h1/recovery','deferred h1 to e2','truthful segment kind','native or closed source qualification label lookup'],all_original_charge_values_account_function_budget_threshold_and_lock_logic_kept=True,not_remote_installed=True,no_owner_or_GO=True,source_files={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py')})
(T/'reports/CONTROLLER_CANDIDATE_ROUTING_SOURCE_AST_CPU_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(proof,indent=2))
prefix=f'''最新人类明确资源分配授权优先：已回答“保存退出后将210从E2转给H1，E3继续”。先让当前cohort52真实完整保存/SDKclose/全部ownout/CPU/原费用结清，再210转H1 270mm真实台阶新任务，E3用当时最新closed52完整源继续。不要调用C53通用E2/E3 preparer/deployer/owner；53仅旧reserved源码保留不删。新T={T.as_posix()}，先读reports/HUMAN_ROUTING_AUTHORITY_AND_CURRENT_BOUNDARY_ACTUAL.json及CONTROLLER_CANDIDATE_ROUTING_SOURCE_AST_CPU_ACTUAL.json。T当前仅本机未安装候选，没有native/新root/GO/费用。H1 source仍hour16 cb118b2ac27cca44466fba9014f4583ee8db23fc2cb2d83c4034b15961178765/674740/100Hz，E3后继必须真实最新closed52整态/全SHA/Adam/50Hz。新H1真实step场景、query/接触/全34几何/native/独立CPU/SDK/PPO/17Adam/资源准入全部过后，用原唯一writer安排h1+recovery两槽；总430h/八extensions/64800安全与旧预留原表达式不改。不得因为新目标直接装旧reward/伪造台阶成绩/重当前owner或清canonical。H1空卡学习守卫保持，选用实际释放后的210，第三卡未知peer只共享冻结评测。
评测当前E3 full first metadata已consume，实际worker217686/create1792577462.58/loaderexe argv/UUID898MiB snapshot核过，当时无FINAL，不再重复首metadata；collect_E3_full750_bounded_once.py唯一unused，返回后用最新run_review_E3_full750_allrows_CPU_V5_once.py（V1-V4未用稿保留；V5只缓存大数组并补独立mode/计时/选中重置/稳定credit/接触核对，不改GPU或门槛）。H1 full已完/E2未跑见下段。T新增未安装SCUT弹道AST exact1002行CPU、step事件16CPU和可观测gyro奖励候选是准备，不是学习成绩。
'''
p=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/PERSISTENT_BUDGET8_SHARED_EVAL_STORAGE_CONTRACT.md';p.write_text(prefix+'\n'+p.read_text('utf8'),'utf8')
C=W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021';args=json.loads((C/'reports/V86_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());args['prompt']=prefix+'\n'+args['prompt'];(R/'H1_ROUTING_EXISTING_MONITOR_UPDATE_ARGS.json').open('x',encoding='utf8').write(json.dumps(args,ensure_ascii=False,indent=2))
print(json.dumps(dict(passed=True,new_stage=str(T),controller_candidates_not_installed=True,generic53_no_longer_next=True)))
