"""Freeze one posttraining E0 evaluation; preserve the primary200 visible window."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
S=T/'JUMP197_FINAL5367_USER_MUJOCO_V200_20261031_V2'
N=T/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_E0_FINAL32066_SAME_PLANE_HEADLESS_20261031v201'
OLD='/mnt/mod4_linux_durable_20261013/MOD4_JUMP197_FINAL5367_USER_VIEW_20261031v200_v2'
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
c=json.loads((N/'reports/ROOT197_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
cpu=json.loads((N/'reports/ROOT197_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes())
assert c['passed_collection'] and c['owner_closed']['canonical_None'] and cpu['roles']['e0_72']['passed']
formal=c['formals']['e0_72'];meta=c['roles']['e0_72']['formal'];p=cpu['roles']['e0_72']
assert formal['SHA']==p['SHA'] and p['saved_iteration']==32066 and p['Adam17_step']==642840
task=json.loads((S/'TASK200.json').read_bytes());task.update(schema='mod4.E0branch201.final32066.same_original_plane.v1',
    epoch=time.time(),human_request='我看过窗口了，他在转圈着跳，支线e0跳跃如何了？',
    model_path=ROOT+'/input_E0_final_complete.pt',model_SHA=formal['SHA'],model_bytes=formal['bytes'],model_iteration=32066,
    original_E0_formal_source=formal['source'],inputE0_SHA=meta['source_SHA'],
    purpose='One new headless E0 final32066 deterministic first episode with same seed27, SDK plant and original commands as primary200; keep main GUI unchanged',
    no_E0_GUI_authorized_or_launched=True,
    local_NEW_E0_upload_byte_passes=1,remote_postcopy_checkpoint_integrity_passes=1,
    no_CPU_model_decode_or_old_input_model_read=True)
del task['input197_SHA']
task['counts']['raw_artifact_transfers']=1
task['counts']['local_visual_byte_passes']=0
task['counts']['npz_member_reads_each']=0
task['counts']['local_checkpoint_upload_byte_passes']=1
task['counts']['remote_postcopy_checkpoint_integrity_passes']=1
put(B/'TASK201.json',task)
worker=(S/'capture200_final197_literal_jump_plane_once.py').read_text('utf8').replace('200','201').replace('5367','32066')
worker=worker.replace("ck['source_resume194_SHA']==TASK['input197_SHA']","ck['source_E0_SHA']==TASK['inputE0_SHA']")
worker=worker.replace("ck['typed_JUMP197_resume_task']","ck['typed_E0_JUMP198_task']")
worker=worker.replace("NN_policy='final197 deterministic PPO mean'","NN_policy='E0 branch final32066 deterministic PPO mean'")
worker=worker.replace('CLOSED197 TRAINING / NEW201 PLANE EVAL; recorded actual, not live learning','CLOSED E0 BRANCH TRAINING / NEW201 SAME-PLANE HEADLESS EVAL')
ast.parse(worker);(B/'evaluate201_E0_final32066_same_plane_once.py').write_text(worker,encoding='utf8',newline='\n')
(B/'zonglin2_app_launcher.py').write_bytes((S/'zonglin2_app_launcher.py').read_bytes())
post=(S/'remote200_postcopy_and_frozen_capture.txt').read_text('utf8').replace(OLD,ROOT).replace('200','201')
post=post.replace('capture201_final197_literal_jump_plane_once.py','evaluate201_E0_final32066_same_plane_once.py')
post=post.replace('previous_models_copied_or_read=0','selected_NEW_E0_checkpoint_postcopy_integrity_reads=1,old_input_models_or_raw_copied=0')
ast.parse(post);(B/'remote201_postcopy_and_frozen_capture.txt').write_text(post,encoding='utf8',newline='\n')
install=(S/'install_capture200_final197_literal_jump_plane_once.py').read_text('utf8').replace(OLD,ROOT).replace('200','201')
install=install.replace('install_capture201_final197_literal_jump_plane_once','install_evaluate201_E0_final32066_same_plane_once')
install=install.replace("closed['roles']['h1_210']","closed['roles']['e0_72']").replace("closed['formals']['h1_210']","closed['formals']['e0_72']").replace("cpu['roles']['h1_210']","cpu['roles']['e0_72']")
install=install.replace("['saved_iteration']==5367","['saved_iteration']==32066")
install=install.replace("human_request='Show latest primary5367 in local MuJoCo; one new recorded original-JUMP plane episode'","human_request='Assess trained E0 branch32066 in one same-condition original-JUMP plane first episode; no GUI switch'")
ast.parse(install);(B/'install_evaluate201_E0_final32066_same_plane_once.py').write_text(install,encoding='utf8',newline='\n')
files=[]
for name in ('TASK201.json','evaluate201_E0_final32066_same_plane_once.py','zonglin2_app_launcher.py'):
    raw=(B/name).read_bytes();files.append(dict(relative=name,local_relative=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
files.append(dict(relative='input_E0_final_complete.pt',local_relative=formal['path'],bytes=formal['bytes'],SHA=formal['SHA'],
                  source='Already qualified NEW197 E0 formal, one task-necessary upload; no new local hash/decode'))
put(B/'FROZEN_EVAL201_COMPLETE_MANIFEST.json',dict(epoch=time.time(),schema='mod4.E0branch201.eval.inputs.v1',files=files,task=task))
sources=[]
for name in ('remote201_postcopy_and_frozen_capture.txt','install_evaluate201_E0_final32066_same_plane_once.py'):
    raw=(B/name).read_bytes();sources.append(dict(path=str(B/name),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
put(R/'FROZEN201_E0_SAME_CONDITION_HEADLESS_EVALUATION_SOURCE.json',dict(epoch=time.time(),source_AST_passed=True,
    human='支线e0跳跃如何了',task=task,files=files,root_sources=sources,
    actual_eval_not_yet_run=True,primary_visible_window_untouched=True,no_new_GUI=True,
    local_source_preparation_model_raw_NPZ_SDK_GPU_reads=0,
    actual_remote_before_use='freshCIM /solecontrollease /fresh72CNone thenCLOSE72 /strict210 freshUUID-rw/privateEX/lightresources',
    no_reward_command_physics_or_guard_change=True,no_training_or_account_write=True))
print(json.dumps(dict(passed_source=True,E0_model_SHA=formal['SHA'],iteration=32066,headless_only=True)))
