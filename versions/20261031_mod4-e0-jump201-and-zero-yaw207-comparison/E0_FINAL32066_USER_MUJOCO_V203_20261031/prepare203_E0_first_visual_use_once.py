"""Fresh user requested E0 display; reuse already-returned201 poses, no new eval."""
from pathlib import Path
import ast,hashlib,json,re,time
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
S=T/'JUMP197_FINAL5367_USER_MUJOCO_V200_20261031_V2'
C=T/'JUMP_E0_FINAL32066_HEADLESS_SAME_PLANE_V201_20261031_V2'
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
receipt=json.loads((C/'reports/ROOT201_ONE_NEW_CAPTURE_TRANSFER_TWO_HOST_SHA_ACTUAL.json').read_bytes())
remote=json.loads((C/'reports/ROOT201V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json').read_bytes())
assert receipt['passed'] and receipt['two_host_SHA_equal'] and remote['passed_execution']
assert remote['result']['model_iteration']==32066
original=(S/'view200_final197_literal_jump_true_MOD4.py').read_text('utf8')
view=re.sub(r'(?<![0-9])200(?![0-9])','203',original)
view=view.replace("case['model_iteration']==5367","case['model_iteration']==32066").replace('model_iteration=5367','model_iteration=32066')
view=view.replace("receipt=json.loads((base/'reports/ROOT203_ONE_NEW_CAPTURE_TRANSFER_TWO_HOST_SHA_ACTUAL.json').read_bytes())","capture_base=base.parent/'JUMP_E0_FINAL32066_HEADLESS_SAME_PLANE_V201_20261031_V2'\n    receipt=json.loads((capture_base/'reports/ROOT201_ONE_NEW_CAPTURE_TRANSFER_TWO_HOST_SHA_ACTUAL.json').read_bytes())")
view=view.replace("remote=json.loads((base/'reports/ROOT203V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json').read_bytes())","remote=json.loads((capture_base/'reports/ROOT201V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json').read_bytes())")
view=view.replace('Final197 literal Fudan JUMP plane actual PhysX recorded motion','E0 branch final32066 original Fudan JUMP plane actual PhysX recorded201')
view=view.replace('MOD4 final197 PPO5367 | actual PhysX | original Fudan JUMP plane | recorded NEW203','E0 JUMP BRANCH PPO32066 | actual PhysX | original Fudan JUMP plane | recorded201 NEW203 VIEW')
view=view.replace('CLOSED197 TRAINING / NEW203 PLANE EVAL | FINAL PPO5367','E0 JUMP BRANCH CLOSED TRAINING | FINAL PPO32066 | NEW203 VIEW OF201 CASE')
view=view.replace('R replay this NEW203 case','R replay this201 case').replace('source203_capture_epoch','source201_capture_epoch')
nums=lambda s:[n.value for n in ast.walk(ast.parse(s)) if isinstance(n,ast.Constant) and isinstance(n.value,(int,float))]
assert nums(view)==[32066 if x==5367 else x for x in nums(original)]
assert 'PPO5367' not in view and 'case[\'model_iteration\']==32066' in view
(B/'view203_E0_final32066_true_MOD4.py').write_text(view,encoding='utf8',newline='\n')
launch=(S/'launch200_user_visible_MuJoCo_once.py').read_text('utf8')
launch=re.sub(r'(?<![0-9])200(?![0-9])','203',launch)
launch=launch.replace("receipt=json.loads((R/'ROOT203_ONE_NEW_CAPTURE_TRANSFER_TWO_HOST_SHA_ACTUAL.json').read_bytes())","capture_base=B.parent/'JUMP_E0_FINAL32066_HEADLESS_SAME_PLANE_V201_20261031_V2'\nreceipt=json.loads((capture_base/'reports/ROOT201_ONE_NEW_CAPTURE_TRANSFER_TWO_HOST_SHA_ACTUAL.json').read_bytes())")
launch=launch.replace('view203_final197_literal_jump_true_MOD4.py','view203_E0_final32066_true_MOD4.py').replace('source_iteration=5367','source_iteration=32066')
ast.parse(launch);(B/'launch203_user_visible_E0_MuJoCo_once.py').write_text(launch,encoding='utf8',newline='\n')
source=[]
for name in ('view203_E0_final32066_true_MOD4.py','launch203_user_visible_E0_MuJoCo_once.py'):
    raw=(B/name).read_bytes();source.append(dict(path=str(B/name),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
put(R/'FROZEN203_FRESH_USER_E0_FIRST_VISUAL_READ_PURPOSE.json',dict(epoch=time.time(),human_exact='e0分支的mujoco播放给我看',
    source201_capture=receipt,model_SHA=remote['result']['model_SHA'],model_iteration=32066,
    source=source,source_AST_numeric_constants_preserved_except_iteration=True,
    visual_byte_passes=1,npz_member_reads_each=1,visual_integrity_passes=1,
    original201_artifact_no_previous_numerical_or_visual_reads=True,old200_primary_artifact_reads=0,
    model_raw_other_than_selected201_pose_reads=0,new_GPU_SDK_neural_or_training_calls=0,
    display_only_true277_meshes31bodies=True,preserve_primary65960_window_no_reopen_or_kill=True,
    window_bound_seconds=7200,labels='E0 separate trained jump branch32066 /recorded actual201, original frozenE0_82 not modified',
    original_Fudan_JUMP_reward_400N50DR_unchanged=True))
print(json.dumps(dict(passed_source=True,model_iteration=32066,primary_window_untouched=True,NEW_GPU_calls=0)))
