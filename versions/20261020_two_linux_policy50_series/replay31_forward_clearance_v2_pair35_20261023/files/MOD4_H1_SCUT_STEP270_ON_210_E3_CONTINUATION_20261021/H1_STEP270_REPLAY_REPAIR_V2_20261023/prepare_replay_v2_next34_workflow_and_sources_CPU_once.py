from pathlib import Path
import ast,hashlib,json,shutil,time,traceback

D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports';C=D/'candidate_reward_V3'
P=T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V32_20261023'
OLD=T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V33_20261023'
N=T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V34_20261023'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

try:
    cpu=read(R/'REPLAY_V2_REWARD_RUNTIME_AND_ACTUAL_SDK_COMPUTE_CPU_V3_ACTUAL.json');assert cpu['passed']
    assert not N.exists();shutil.copytree(OLD,N)
    for p in N.glob('*.py'):
        text=p.read_text('utf8').replace('H1step270_reward_boundary_2310v33','H1step270_reward_replay2_2310v34');ast.parse(text);p.write_text(text,encoding='utf8')
    repair=N/'repair_sources'
    for name in ('h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py'):shutil.copy2(C/name,repair/name)
    shutil.copytree(C/'reference_sources',repair/'reference_sources',dirs_exist_ok=True)
    auth=read(P/'repair_sources/H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json')
    auth.update(epoch=time.time(),approved=True,human_request='继续回放看h3为何跳不上台阶，然后修复；明确当前跳270mm台阶的H1车',scope='Reward-only replay31-derived V2 in a fresh root after current32 complete FINAL/wholeCPU/original cost/allout; command publisher, physics, actor inputs and strict 270mm success unchanged.',replay_report=str(R/'RECORDED_STEP_REPLAY_V2_DIAGNOSIS_AND_REPAIR_SCOPE_ACTUAL.json'),reward_CPU=cpu,integration_CPU=cpu,new_reward_module_SHA=cpu['reward_module_SHA'],original_reward_module_SHA='d0f937e840790ddf0602974ff0dca8e5e3183365a6ca2d3afe92a1cdd112bc44',new_runtime_SHA=cpu['runtime_SHA'],original_runtime_SHA=cpu['runtime_SHA'],installed_reward_checker_SHA=cpu['installed_checker_SHA'],new_reward_recipe_version='step270_forward_clearance_replay_v2',human_reply_auth=str(R/'HUMAN_CONTINUE_REPLAY_H1_AND_REPAIR_AUTH_ACTUAL.json'),ordinary_wheel_floor_boundary_repair_not_new_reward_recipe=False,original_v1_auth_preserved_path=str(P/'repair_sources/H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json'))
    (repair/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json').write_text(json.dumps(auth,ensure_ascii=False,indent=2),encoding='utf8')
    loader=repair/'closed_production_continuation_CPU_v2.py';before=loader.read_text('utf8')
    anchor="    assert H(B/reward_module)==current[reward_module]['SHA']==reward['new_reward_module_SHA']"
    assert before.count(anchor)==1
    inserted="    assert H(old/reward_module)==prior[reward_module]['SHA'] and prior[reward_module]['SHA'] in (reward['original_reward_module_SHA'],reward['new_reward_module_SHA'])\n"
    after=before.replace(anchor,inserted+anchor);ast.parse(after)
    assert ast.dump(ast.parse(after.replace(inserted,'')))==ast.dump(ast.parse(before));loader.write_text(after,encoding='utf8')
    prep=N/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py';s=prep.read_text('utf8')
    s=s.replace("reward_stage=T/'H1_STEP270_REWARD_PATH_V1_20261022'","reward_stage=N/'repair_sources'")
    s=s.replace("repair=P/'repair_sources'","repair=N/'repair_sources'")
    s=s.replace("reward_recipe_version='step270_forward_clearance_path_reward_v1'","reward_recipe_version='step270_forward_clearance_replay_v2'")
    assert "P=T/'"+P.name+"';E=P" in s and "reward_stage=N/'repair_sources'" in s and "repair=N/'repair_sources'" in s
    ast.parse(s);prep.write_text(s,encoding='utf8')
    for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'))
    assert H(repair/'h1_step270_sdk_runtime_candidate.py')==cpu['runtime_SHA'] and H(repair/'h1_step270_path_reward_v1.py')==cpu['reward_module_SHA'] and H(repair/'step270_reward_installed_CPU_v1.py')==cpu['installed_checker_SHA']
    assert not (N/'payloads').exists() and not (N/'controllers').exists() and not list((N/'reports').iterdir())
    put(R/'REPLAY_V2_NEXT34_UNUSED_WORKFLOW_REWARD_ALLOWLIST_CPU_ACTUAL.json',dict(epoch=time.time(),passed_AST=True,stage=str(N),predecessor_current32=str(P),only_after_both_complete_FINAL_CPU_cost_health_allout_and_fresh_resources=True,dynamic_both_latest_source_SHA_Adam=True,same_270phase_fullstate=True,same_runtime_boundary_physics_command_goal_bytes=True,new_reward_module_SHA=cpu['reward_module_SHA'],new_installed_checker_SHA=cpu['installed_checker_SHA'],loader_previous_reward_exact_SHA_v1_to_v2_or_v2_to_same_v2=True,all_other_loader_AST_exact=True,source_reward_and_checker_taken_from_new_repair_sources_not_old_B=True,paired_and_H1_only_resource_branches_preserved=True,no_future_payload_Task_GO_or_fee=True,old33_generic_reserved_preserved_do_not_run=True))
    print(json.dumps(dict(prepared_source_AST_only=True,next_stage=str(N),reward_module_SHA=cpu['reward_module_SHA'],no_GO=True)))
except BaseException:
    put(R/('NEXT34_WORKFLOW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_remote_or_GO=True));raise
