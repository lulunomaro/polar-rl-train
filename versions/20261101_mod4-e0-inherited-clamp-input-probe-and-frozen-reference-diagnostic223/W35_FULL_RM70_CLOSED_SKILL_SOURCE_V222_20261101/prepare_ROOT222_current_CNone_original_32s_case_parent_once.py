"""New root finite parent/caller; source and saved metadata only."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;S=N/'ROOT222_TASK_ACTUAL_32404';R=N/'reports'
O=T/'E0_ACTION_INPUT_MODE_CLAMP_DIAGNOSTIC_V223_20261101'
def put(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False)
def source(p,s):ast.parse(s);p.write_text(s,encoding='utf8')
assert json.loads((R/'ROOT222_NEW_OBSERVER_BEHAVIOR_CPU_RETURNED_ACTUAL.json').read_bytes())['passed']
source(S/'contract222.py','''"""Immutable newW35 model and bounded skill-only Task;no old active binding."""
def validate_task(t):
 assert t['kind']=='NEW222_W35_CLOSED_FULL_RM70_SKILL_ONLY'and t['model_SHA']=='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'
 assert t['model_iteration']==32404 and t['num_envs']==20000 and t['controls_max']==1600 and t['physics_max']==12800 and t['feedback_max']==3200
 assert t['worker_seconds']==1680 and t['parent_seconds']==1800 and t['GPU_UUID']=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
 assert t['no_new_learning_or_GO']and t['model_physical_byte_reads']==t['model_decodes']==1 and t['model_copies']==0
 return True
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 return True
''')
parent=(O/'source/target223_single_N1_parent_UNUSED.py').read_text('utf8').replace('223','222')
parent=parent.replace("TASK222.json","TASK222_PENDING_CURRENT_ADMISSION.json")
parent=parent.replace("binding=task['current_authority_binding'];identity=current=None","binding={'kind':'FRESH_CNONE'};identity=current=None")
parent=parent.replace('ram>8*1024**3','ram>32*1024**3')
parent=parent.replace('actual_parent_private_EX_and_authority_admitted=True','actual_current_CNone_private_shared_resources_admitted=True')
parent=parent.replace('model_byte_reads_by_worker_max=1','selected_formal_byte_hash_passes_max=1').replace('controls_max=32,physics_max=256,NN_actor_only=True','controls_max=1600,physics_max=12800,full_compatible_runner_restore_only=True')
parent=parent.replace('evaluate222_input_mode_clamp_UNUSED_once.py','evaluate222_CLOSED_W35_FULL_RM70_SKILL_UNUSED_once.py')
parent=parent.replace('child.wait(timeout=900)','child.wait(timeout=1800)')
parent=parent.replace("out=P/'actual_capture';r=out/'CAPTURE222_ACTUAL_RESULT.json'", "out=P/'actual222';r=out/'ACTUAL222_CLOSED_RM70_SKILL_FACTS.json'")
parent=parent.replace("assert rc==0 and result and result['passed'] and not errors and read(out/'ENV222_CLOSE_RETURNED.json')['closed'] and read(out/'APP222_CLOSE_REQUESTED.json')['close_call_next']", "assert rc==0 and result and result['passed_execution'] and not errors and read(out/'ENV222_CLOSE_RETURNED.json')['closed'] and read(out/'APP222_CLOSING.json')")
parent=parent.replace("bool(result and result['passed'])","bool(result and result['passed_execution'])")
source(S/'target222_single_N1_parent_UNUSED.py',parent)
caller=(O/'run_ROOT223_input_mode_action_flow_once.py').read_text('utf8')
caller=caller.replace("S=N/'source'","S=N/'ROOT222_TASK_ACTUAL_32404'")
caller=caller.replace('MOD4_E0_ACTION_INPUT223_N1_CNONE_20261101/case','MOD4_W35_CLOSED32404_FULL_RM70_SKILL_20261101v222/case')
caller=caller.replace('223','222').replace('run_ROOT222_input_mode_action_flow_once','run_ROOT222_full_RM70_skill_case_once')
caller=caller.replace("TASK222.json","TASK222_PENDING_CURRENT_ADMISSION.json")
caller=caller.replace("B/'actual_capture'","B/'actual222'")
start=caller.index(" q=read(T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/reports/ROOT210_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')")
end=caller.index(" for r in pack['files']:",start)
caller=caller[:start]+" assert read(R/'ROOT222_NEW_OBSERVER_BEHAVIOR_CPU_RETURNED_ACTUAL.json')['passed']\n assert task['model_SHA']=='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'and task['model_iteration']==32404\n"+caller[end:]
caller=caller.replace("assert read(T/'W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101/reports/ROOT219V3_NORMAL900_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'", "assert read(T/'E0_ACTION_INPUT_MODE_CLAMP_DIAGNOSTIC_V223_20261101/reports/ROOT223_STD_SOURCE_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'")
caller=caller.replace("GPU_model_byte_reads=1,GPU_model_decodes=1", "selected_formal_byte_reads=1,selected_formal_decodes=1")
caller=caller.replace('new_case_controls_max=32,physics_callbacks_max=256,feedback_max=64','new_case_controls_max=1600,physics_callbacks_max=12800,feedback_max=3200')
caller=caller.replace('timeout=1800','timeout=1950')
source(N/'run_ROOT222_full_RM70_skill_case_once.py',caller)
# Parent and worker Task use different filenames intentionally; all pending data immutable.
rows=[dict(relative=p.name,bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(S.iterdir())if p.is_file()and p.name!='SOURCE222_INSTALL.json']
put(S/'PACKAGE222_SOURCE_AND_TASK.json',dict(epoch=time.time(),files=rows,model_raw_or_asset_bytes_copied=0))
put(R/'ROOT222_TASK_AND_PARENT_SOURCE_READY.json',dict(epoch=time.time(),source_AST_passed=True,Root_behavior_CPU='ROOT222_NEW_OBSERVER_BEHAVIOR_CPU_RETURNED_ACTUAL.json',GPU_task='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',source_data_model_SDK_remote_calls=0,
 new32s_skill_case_pending_fresh_admission=True,model_physical_byte_read_decode_max=1,constructor_resetNPZ='Existing original20k physical initialization only',own_new_startup_PT_roundtrips='Original source saver/DR compatibility roundtrips only;no old inputs reopened',no_optimizer_step_learning_GO_or_budget_write=True,
 original_source_reader_error_preserved='First ROOT wide UTF8 source print failed in Python GBK console on U+2194 before remaining files; narrow reader explicitly reconfigured stdout UTF8. No SDK/model attempted.',worker_parent_seconds=[1680,1800],retention_source_JSONL='Producer metadata only;no reread/transfer for Git'))
print(json.dumps(dict(passed=True,package_files=len(rows),source_only=True,current_CNone_SDK_not_yet_read=True)))
