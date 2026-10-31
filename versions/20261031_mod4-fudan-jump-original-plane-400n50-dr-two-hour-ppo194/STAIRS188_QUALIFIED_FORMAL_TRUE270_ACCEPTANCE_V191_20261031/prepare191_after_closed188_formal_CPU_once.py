"""Bind one new188 formal to an unchanged original40050 true270 assessment.

No model content is read here. Construction waits for actual closing+initialCPU.
"""
from pathlib import Path
import ast,hashlib,json,time

B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
N=T/'FUDAN_STAIRS3_LITERAL_REWARD_TERRAIN_400N50_ADAPT_V188_20261031'
OLD=T/'DELIVERED_JUMP4999_TOTAL_PLAN_400N50_DR_270_CHECK_V187_20261031/V2_EXISTING_NORMALIZED_CLOCK_AND_FEEDBACK_SOURCE'
REMOTE='/mnt/mod4_linux_durable_20261013/MOD4_STAIRS188_FORMAL40050_TRUE270_EVAL_20261031v191'
PAYLOAD='/mnt/mod4_linux_durable_20261013/MOD4_DELIVERED4999_PLAN40050_DR_STEP270_EVAL_20261031v187_v2/payload'

def load(p):return json.loads(Path(p).read_bytes())
def put(p,value):
    with Path(p).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False)

closed=load(N/'reports/ROOT188_COMPLETE_FINAL_OR_FAILURE_ORIGINAL_COST_RETURNED_ACTUAL.json')
cpu=load(N/'reports/ROOT188_NEW_FORMAL_INITIAL_CPU_RETURNED_ACTUAL.json')
free=load(N/'reports/ROOT188_NORMAL900_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')
assert closed['passed_collection'] and closed['source_node']['qualified_formal'] and cpu['passed']
assert closed['owner_closed']['canonical_None'] and free['all_owned_SSH_closed'] and free['SESSION_restored']
formal=closed['formal'];assert formal['two_host_SHA_equal'] and formal['transfers']==1 and formal['SHA']==cpu['SHA']
assert cpu['actor35_critic38_action6'] and cpu['target_DR_full_states_present'] and not cpu['CUDA_initialized']
assert cpu['actual_new_PPO_updates']>0 and cpu['saved_iteration']==4999+cpu['actual_new_PPO_updates']
put(R/'PREPARE191_CLOSED188_NEW_FORMAL_BINDING_STARTED.json',dict(epoch=time.time(),source=formal,
    source_CPU=cpu,new_model_byte_reads=0,no_learning=True))

original=(OLD/'evaluate187_delivered_actor40050_step270_once.py').read_text('utf8')
value=original.replace('187','191')
old_sha="MODEL_SHA = '5932295297ed93b65fd88fe142d6fc66099c0a936f23091a79a3b2752c51dfa4'"
old_path="MODEL_PATH = '/mnt/mod4_linux_durable_20261013/rm2026_fudan_exact_20261031/runs20k_tgs32_16/2026-10-31_04-38-39_fudan_exact_mod4_plane_edge4090_20k_2p5ms_tgs32_16/model_4999.pt'"
assert value.count(old_sha)==value.count(old_path)==1
value=value.replace(old_sha,'MODEL_SHA = '+repr(formal['SHA']))
value=value.replace(old_path,'MODEL_PATH = '+repr(formal['source']))
value=value.replace("root = job / 'payload'", "root = Path(task['qualified_existing_payload_root'])")
value=value.replace('len(raw) == 1244341', 'len(raw) == '+str(formal['bytes']))
value=value.replace("ck['iter'] == 4999", "ck['iter'] == "+str(cpu['saved_iteration']))
value=value.replace('source_iteration=4999', 'source_iteration='+str(cpu['saved_iteration']))
value=value.replace('source_training_policy_hz=100', 'source_training_policy_hz=50')
value=value.replace('source_nominal_gas_stiffness=3500', 'source_nominal_gas_stiffness=2000')
value=value.replace('source_was_not_trained_under_these_target_conditions=True',
                    'source_adapted400N50_DR_on_original_Fudan_stairs3=True')
value=value.replace('source_not_trained_under_target_profile=True',
                    'source_training_max_stair_height_m=.21, source270_skill_not_previously_proved=True')
value=value.replace('ACTUAL_DELIVERED4999_GPU_ACTOR_LITERAL_RESTORE', 'ACTUAL_QUALIFIED188_GPU_ACTOR_LITERAL_RESTORE')
value=value.replace('DELIVERED4999_TOTALPLAN_400N50_DR_270_EVAL191','QUALIFIED188_TOTALPLAN_400N50_DR_270_EVAL191')
value=value.replace('ACTUAL191_FROZEN4999_', 'ACTUAL191_FROZEN188_')
ast.parse(value)
# Physics/event-observer function bodies are byte-for-byte AST-equivalent.
for observer in ('observed_physical','observed_terminal'):
    def find(source):
        return [node for node in ast.walk(ast.parse(source))
                if isinstance(node,ast.FunctionDef) and node.name==observer]
    before=find(original);after=find(value)
    assert len(before)==len(after)
    assert all(ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
               for a,b in zip(before,after)),observer
dest=B/'evaluate191_qualified188_actor40050_step270_once.py';dest.write_text(value,encoding='utf8',newline='\n')

task=load(OLD/'FROZEN_EVAL187_TASK.json')
task.update(schema='mod4.qualified188.plan40050DR.step270.frozen.v1',model_SHA=formal['SHA'],
            model_path=formal['source'],model_bytes=formal['bytes'],source_iteration=cpu['saved_iteration'],
            source188_original_owner_fully_closed=True,source188_new_initial_CPU_passed=True,
            source188_new_initial_CPU_report_SHA=hashlib.sha256((N/'reports/ROOT188_NEW_FORMAL_INITIAL_CPU_RETURNED_ACTUAL.json').read_bytes()).hexdigest(),
            qualified_existing_payload_root=PAYLOAD,source_training_terrain='Original Fudan stairs3 max.21m',
            source_training_policy_hz=50,source_nominal_gas_k=2000,
            reuse187_original_plant_and_success_observer=True,
            new_purpose='Fresh source188 actual first32 episodes at original270mm; no old models/raw replays',
            old_input4999_PT_reads=0,CPU_decodes=0,new_GPU_model_decodes=1)
task.pop('source_was100Hz_3500_N_m_no_target_DR_adaptation_claim',None)
put(B/'FROZEN_EVAL191_TASK.json',task)
launcher=(OLD/'zonglin2_app_launcher.py').read_text('utf8').replace('187','191')
(B/'zonglin2_app_launcher.py').write_text(launcher,encoding='utf8',newline='\n')

post=(OLD/'remote187_postcopy_and_frozen_eval.txt').read_text('utf8').replace('187','191')
post=post.replace('/mnt/mod4_linux_durable_20261013/MOD4_DELIVERED4999_PLAN40050_DR_STEP270_EVAL_20261031v191_v2',REMOTE)
post=post.replace('evaluate191_delivered_actor40050_step270_once.py',dest.name)
post=post.replace('ACTUAL191_FROZEN4999_', 'ACTUAL191_FROZEN188_')
# Original parent wait900/worker720 and physical observer remain unchanged.
ast.parse(post);(B/'remote191_postcopy_and_frozen_eval.txt').write_text(post,encoding='utf8',newline='\n')

install=(OLD/'install_evaluate187_totalplan_frozen_once.py').read_text('utf8').replace('187','191')
install=install.replace('N.parent.parent','N.parent')
install=install.replace('/mnt/mod4_linux_durable_20261013/MOD4_DELIVERED4999_PLAN40050_DR_STEP270_EVAL_20261031v191_v2',REMOTE)
install=install.replace('install_evaluate191_totalplan_frozen_once','install_evaluate191_qualified188_frozen_once')
install=install.replace("run_ROOT171_secure'", "run_ROOT171_secure|collect188_original_formal_cost_normal900_UNUSED_once|run189_W35_saved_cycle_single_pass_once|start190_|install190_'" )
install=install.replace('import json,time,hashlib\np=Path', 'import json,time,hashlib,subprocess,psutil,shutil\np=Path')
install=install.replace("CNone=True,remaining_snapshot=c['remaining_training_seconds'],SHA=hashlib.sha256(b).hexdigest(),readonly=True)",
    "CNone=True,remaining_snapshot=c['remaining_training_seconds'],SHA=hashlib.sha256(b).hexdigest(),readonly=True,resources72_GPU_UUID_free_util=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().splitlines(),resources72_RAM_available=psutil.virtual_memory().available,resources72_task_disk_free=shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2/tasks').free,resource_purpose='Human requested expert-native ready queue placement; snapshot only, not reserved',unknown_process_or_GPU_PID_reads=0)")
install=install.replace("source_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),serial_lease='EXCLUSIVE_ROOT191'",
                        "source_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),serial_lease='EXCLUSIVE_ROOT191'")
ast.parse(install)
(B/'install_evaluate191_qualified188_frozen_once.py').write_text(install,encoding='utf8',newline='\n')

files=[]
for name in (dest.name,'FROZEN_EVAL191_TASK.json','zonglin2_app_launcher.py'):
    p=B/name;raw=p.read_bytes();files.append(dict(relative=name,local_relative=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
put(B/'FROZEN_EVAL191_COMPLETE_MANIFEST.json',dict(schema='mod4.actual191.bound_frozen_input.v1',
    epoch=time.time(),files=files,source188=formal,source_CPU=cpu,
    physical_source='Exact existing187v2 normalized40050 payload retained read-only',
    qualified_existing_payload_root=PAYLOAD,no_payload_binary_copy_or_read_during_preparation=True,
    resource72_query_purpose='User requested idle-card allocation for expert/native learning; one UUID/free/util-only read, not Git',
    old187_source_observer_geometry_physics_and_success_unchanged=True))
put(R/'FROZEN191_SOURCE_BINDING_AND_PROTOCOL_ACTUAL.json',dict(epoch=time.time(),passed=True,
    model_SHA=formal['SHA'],model_bytes=formal['bytes'],source_iteration=cpu['saved_iteration'],
    output_remote=REMOTE,protocol=task,new_model_reads=0,source_only=True,
    source_change_scope='New checkpoint identity/source-domain metadata, new own output namespace; original physical observer unchanged',
    current_GPU_SDK_admission_or_evaluation=False))
print(json.dumps(dict(passed=True,model_SHA=formal['SHA'],source_iteration=cpu['saved_iteration'],
                      source_only=True,next_entry='install_evaluate191_qualified188_frozen_once.py')))
