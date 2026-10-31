"""Keep failed201 intact. Rebuild with version-aware strings; preserve physics numbers."""
from pathlib import Path
import ast,hashlib,json,re,time
B=Path(__file__).resolve().parent;T=B.parent;S=T/'JUMP197_FINAL5367_USER_MUJOCO_V200_20261031_V2';V=B.with_name(B.name+'_V2')
R=B/'reports';assert not V.exists()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
old=read(R/'ROOT201V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json')
assert not old['passed_execution'] and old['result'] is None and old['worker_errors']
error=next(x for x in old['full_UTF8'] if x['path'].endswith('ORIGINAL201_CAPTURE_ERROR.json'))
assert 'nominal_stiffness_N_m' in error['UTF8'] and '2010' in error['UTF8']
closed=read(R/'ROOT201V2_ALL_SSH_CLOSED_SESSION_RESTORED_LEASE_FREE.json');assert closed['global_serial_lease']=='FREE'
V.mkdir();(V/'reports').mkdir()
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_E0_FINAL32066_SAME_PLANE_HEADLESS_20261031v201_v2'
oldroot='/mnt/mod4_linux_durable_20261013/MOD4_JUMP197_FINAL5367_USER_VIEW_20261031v200_v2'
def version(s):return re.sub(r'(?<![0-9])200(?![0-9])','201',s)
base=(S/'capture200_final197_literal_jump_plane_once.py').read_text('utf8')
worker=version(base).replace('5367','32066')
worker=worker.replace("ck['source_resume194_SHA']==TASK['input197_SHA']","ck['source_E0_SHA']==TASK['inputE0_SHA']").replace("ck['typed_JUMP197_resume_task']","ck['typed_E0_JUMP198_task']")
worker=worker.replace("NN_policy='final197 deterministic PPO mean'","NN_policy='E0 branch final32066 deterministic PPO mean'")
worker=worker.replace('CLOSED197 TRAINING / NEW201 PLANE EVAL; recorded actual, not live learning','CLOSED E0 BRANCH TRAINING / NEW201 SAME-PLANE HEADLESS EVAL')
def numbers(s):return [n.value for n in ast.walk(ast.parse(s)) if isinstance(n,ast.Constant) and isinstance(n.value,(float,int))]
assert numbers(worker)==[32066 if x==5367 else x for x in numbers(base)]
assert "MOD4_RESUME_QUEUE_CONTROL_US']='20000'" in worker and 'queue.control_us=20000' in worker
assert "nominal_stiffness_N_m']==2000" in worker and '==2010' not in worker and '20100' not in worker
(V/'evaluate201_E0_final32066_same_plane_once.py').write_text(worker,encoding='utf8',newline='\n')
(V/'zonglin2_app_launcher.py').write_bytes((S/'zonglin2_app_launcher.py').read_bytes())
task=read(B/'TASK201.json')
# The first purpose uploaded and verified this immutable input but failed before model read.
task.update(epoch=time.time(),model_path='/mnt/mod4_linux_durable_20261013/MOD4_E0_FINAL32066_SAME_PLANE_HEADLESS_20261031v201/input_E0_final_complete.pt',
    local_NEW_E0_upload_byte_passes=0,remote_postcopy_checkpoint_integrity_passes=0,
    input_reuse='Original201 newly uploaded immutable E0 final; original app failed before any checkpoint read/decode or action',
    narrow_repair='Version-aware string substitutions preserve all original physical numeric constants',
    original_failed_purpose=str(B),new_distinct_purpose=str(V))
task['counts']['local_checkpoint_upload_byte_passes']=0;task['counts']['remote_postcopy_checkpoint_integrity_passes']=0
put(V/'TASK201.json',task)
post=version((S/'remote200_postcopy_and_frozen_capture.txt').read_text('utf8').replace(oldroot,ROOT))
post=post.replace('capture201_final197_literal_jump_plane_once.py','evaluate201_E0_final32066_same_plane_once.py')
post=post.replace('previous_models_copied_or_read=0','checkpoint_copies=0,selected_E0_gpu_read_first_admitted_in_new_worker=True')
assert ROOT in post;ast.parse(post);(V/'remote201_postcopy_and_frozen_capture.txt').write_text(post,encoding='utf8',newline='\n')
install=version((S/'install_capture200_final197_literal_jump_plane_once.py').read_text('utf8').replace(oldroot,ROOT))
install=install.replace('install_capture201_final197_literal_jump_plane_once','install_evaluate201_E0_final32066_same_plane_once')
install=install.replace("closed['roles']['h1_210']","closed['roles']['e0_72']").replace("closed['formals']['h1_210']","closed['formals']['e0_72']").replace("cpu['roles']['h1_210']","cpu['roles']['e0_72']").replace("['saved_iteration']==5367","['saved_iteration']==32066")
install=install.replace("human_request='Show latest primary5367 in local MuJoCo; one new recorded original-JUMP plane episode'","human_request='Assess E0 final32066; NEWV2 numeric-preserving source repair before first model read, same original commands and plant, headless'")
ast.parse(install);(V/'install_evaluate201_E0_final32066_same_plane_once.py').write_text(install,encoding='utf8',newline='\n')
files=[]
for name in ('TASK201.json','evaluate201_E0_final32066_same_plane_once.py','zonglin2_app_launcher.py'):
    raw=(V/name).read_bytes();files.append(dict(relative=name,local_relative=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
put(V/'FROZEN_EVAL201_COMPLETE_MANIFEST.json',dict(epoch=time.time(),schema='mod4.E0branch201.newV2.numeric-preserving.eval.inputs.v1',files=files,task=task))
report=dict(epoch=time.time(),passed_source=True,original_error_full_UTF8=error,original_remote_worker=old['actual_worker_identity'],
    original_wait_RC=old['returncode'],original_passed_execution=False,
    original_runtime_model_reads=0,original_runtime_model_decodes=0,original_physical_controls=0,
    original_Kit_rc0_does_not_override_function_error=True,
    cause='Unbounded source text replace200->201 changed2000 to2010 and queue20000 to20100; premodel guard refused',
    original_physics_asset_or_training_source_changed=False,original_worker_queue_value_not_used_by_any_step=True,
    narrow_repair='Rebuild from successful200 with regex bounded by digits; all AST numeric constants identical except model iteration5367->32066',
    numeric_AST_sequence_preserved=True,queue_control_us20000=True,gas_nominal_k2000=True,
    new_V2_namespace=ROOT,source_dir=str(V),model_gpu_read_decode_budget_NEW1_each=True,
    existing_uploaded_new_E0_checkpoint_reused_without_copy_hash_or_CPUdecode=True,
    no_primary_window_or_reward_command_guard_change=True,no_new_training=True,files=files)
put(R/'ROOT201_ORIGINAL_PREMODEL_NUMERIC_ASSERT_FAILURE_AND_NEW_V2_REPAIR.json',report)
put(V/'reports/FROZEN201_V2_NUMERIC_PRESERVING_SOURCE_AND_NEW_PURPOSE.json',report)
print(json.dumps(dict(passed_source=True,new_V2=str(V),all_numeric_constants_preserved_except_model_iteration=True,model_not_yet_read=True)))
