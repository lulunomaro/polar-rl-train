from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 cpu=json.loads((R/'REWARD_PATH_CPU_ACTUAL.json').read_bytes());integration=json.loads((R/'ACTUAL_RUNTIME_CALLBACK_AND_SDK_REWARD_COMPUTE_CPU_V3_ACTUAL.json').read_bytes());assert cpu['passed'] and integration['passed']
 N=T/'H1_STEP270_E3_REWARD_PATH_PAIR_V17_20261022';assert not N.exists();N.mkdir();(N/'reports').mkdir()
 old=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V16_20261022';shutil.copytree(old/'controllers',N/'controllers')
 names=['deploy_pair_new_original_writer_bounded_once.py','collect_pair_first_actual_GO_positive_PPO_once.py','collect_pair_complete_finals_original_cost_bounded_once.py','review_pair_complete_models_original_cost_CPU_once.py','relocate_actual_closed_H1_forensics_peer_TLS_bounded_once.py']
 for name in names:shutil.copy2(old/name,N/name)
 cfg=json.loads((old/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json').read_bytes());cfg.update(sequence=17,cohort_id=N.name,owner_root='/mnt/mod4_linux_durable_20261013/H1step270_rewardpath_2210v17/owner',roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_rewardpath_2210v17/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_rewardpath_2210v17/recovery'),explicit_human_authorized_reward_path_change=True)
 put(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json',cfg)
 auth=dict(epoch=time.time(),approved=True,human_request='根据回放验证修改一下奖励函数让车能完成我们的跳上台阶任务',scope='Reward-only path shaping in a new unused root after current pair15 full save/wholeCPU/original-cost/allout; no extra budget, command/input/physics/guard or success changes.',replay_report=str(T/'H1_STEP270_REPLAY_DIAG_20261022_V105/reports/RECORDED_STEP_REPLAY_DIAGNOSIS_AND_LIMITS_ACTUAL.json'),reward_CPU=cpu,integration_CPU=integration,new_reward_module_SHA=H(B/'h1_step270_path_reward_v1.py'),new_runtime_SHA=H(B/'h1_step270_sdk_runtime_candidate.py'),original_runtime_SHA=cpu['original_runtime']['SHA'])
 target=(T/'target_H1_step270_closed_source_sdk_cpu_review_v1.py').read_text('utf8')
 needle="(B / 'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json').write_text"
 assert target.count(needle)==1
 target=target.replace(needle,"from step270_reward_installed_CPU_v1 import check as reward_check\nv['new_reward_integration_CPU']=reward_check(B,sdk.parent.parent/'managers/reward_manager.py')\nv['reward_runtime_SHA']=H(B/'h1_step270_sdk_runtime_candidate.py')\nv['reward_module_SHA']=H(B/'h1_step270_path_reward_v1.py')\n"+needle)
 (B/'target_H1_step270_reward_path_closed_source_sdk_cpu_review_v1.py').write_text(target,encoding='utf8')
 auth['target_CPU_SHA']=H(B/'target_H1_step270_reward_path_closed_source_sdk_cpu_review_v1.py');auth['installed_reward_checker_SHA']=H(B/'step270_reward_installed_CPU_v1.py')
 put(R/'HUMAN_REWARD_CHANGE_AND_SOURCE_CPU_AUTH_ACTUAL.json',auth)
 loader=(T/'closed_step270_approved_trace_retention_source_CPU_v1.py').read_text('utf8')
 needle="    for row in m['files']:\n        rel=row['relative']"
 extra="""    reward=read(B/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json')
    assert reward['approved'] and reward['reward_CPU']['passed'] and reward['integration_CPU']['passed']
    runtime='h1_step270_sdk_runtime_candidate.py';reward_module='h1_step270_path_reward_v1.py'
    assert H(old/runtime)==prior[runtime]['SHA'] and prior[runtime]['SHA'] in (reward['original_runtime_SHA'],reward['new_runtime_SHA'])
    assert H(B/runtime)==current[runtime]['SHA']==reward['new_runtime_SHA']
    assert H(B/reward_module)==current[reward_module]['SHA']==reward['new_reward_module_SHA']
    assert H(B/'step270_reward_installed_CPU_v1.py')==reward['installed_reward_checker_SHA']
    assert H(B/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')==reward['target_CPU_SHA']
"""
 assert loader.count(needle)==1;loader=loader.replace(needle,extra+needle)
 loader=loader.replace("rel not in (trace,'closed_production_continuation_CPU_v2.py')","rel not in (trace,'closed_production_continuation_CPU_v2.py',runtime,reward_module,'step270_reward_installed_CPU_v1.py','target_H1_step270_closed_source_sdk_cpu_review_v1.py')")
 loader=loader.replace("    v=dict(kind=", "    assert cpu['new_reward_integration_CPU']['passed'] and cpu['reward_runtime_SHA']==reward['new_runtime_SHA'] and cpu['reward_module_SHA']==reward['new_reward_module_SHA']\n    v=dict(explicit_human_authorized_reward_change=True,reward_runtime_SHA=reward['new_runtime_SHA'],reward_module_SHA=reward['new_reward_module_SHA'],kind=")
 loader=loader.replace('same_active_runtime_assets_and_PPO_AST=True','same_assets_PPO_account_and_physics_reward_allowlist_CPU=True')
 (B/'closed_step270_reward_path_source_CPU_v1.py').write_text(loader,encoding='utf8')
 source=(old/'prepare_pair_from_actual_closed_pair_with_approved_retention_CPU_once.py').read_text('utf8')
 source=source.replace("T/'closed_step270_approved_trace_retention_source_CPU_v1.py'","T/'H1_STEP270_REWARD_PATH_V1_20261022/closed_step270_reward_path_source_CPU_v1.py'")
 needle="   proofname='CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json'"
 inject="""   reward_stage=T/'H1_STEP270_REWARD_PATH_V1_20261022'
   for name in ('h1_step270_sdk_runtime_candidate.py','h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py'):
    shutil.copy2(reward_stage/name,dest/name)
   shutil.copy2(reward_stage/'target_H1_step270_reward_path_closed_source_sdk_cpu_review_v1.py',dest/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')
   shutil.copy2(reward_stage/'reports/HUMAN_REWARD_CHANGE_AND_SOURCE_CPU_AUTH_ACTUAL.json',dest/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json')
"""
 assert source.count(needle)==1;source=source.replace(needle,inject+needle)
 source=source.replace("task.update(approved_future_prefix_retention_policy=", "task.update(explicit_human_authorized_reward_path_change=key=='h1',reward_recipe_version='step270_forward_clearance_path_reward_v1' if key=='h1' else None,approved_future_prefix_retention_policy=")
 (N/'prepare_pair_after_closed15_with_reward_path_CPU_once.py').write_text(source,encoding='utf8')
 files=[]
 for p in [*N.rglob('*.py'),B/'closed_step270_reward_path_source_CPU_v1.py',B/'target_H1_step270_reward_path_closed_source_sdk_cpu_review_v1.py']:
  ast.parse(p.read_text('utf8'));files.append(dict(path=str(p),SHA=H(p)))
 put(R/'REWARD_PAIR17_UNUSED_WORKFLOW_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),passed=True,new_stage=str(N),files=files,previous_stage=cfg['previous_stage_dir'],human_reward_authorization=str(R/'HUMAN_REWARD_CHANGE_AND_SOURCE_CPU_AUTH_ACTUAL.json'),only_reserved_no_payload_remote_Task_GO_or_new_cost=True,old_pair16_generic_reserved_not_to_run=True,new_runtime_reward_candidate_only_not_installed=True))
 print(json.dumps(dict(reserved=str(N),AST_passed=True,no_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/('REWARD_WORKFLOW_PREPARE_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_GO=True));raise
