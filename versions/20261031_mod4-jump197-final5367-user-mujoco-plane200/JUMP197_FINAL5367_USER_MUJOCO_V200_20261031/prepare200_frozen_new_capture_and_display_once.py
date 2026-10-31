"""Independent local source preparation while the original197 collector waits."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
S=T/'STAIRS188_ORIGINAL_COURSE_USER_MUJOCO_V193_20261031'
N=T/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_JUMP197_FINAL5367_USER_VIEW_20261031v200'
OLD='/mnt/mod4_linux_durable_20261013/MOD4_STAIRS188_ORIGINAL_COURSE_USER_VIEW_20261031v193'
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
status=json.loads((N/'reports/CURRENT_ACTUAL199_PRIMARY197_COMPLETE_SAVED_STATUS_NO_JUMP_SKILL_CLAIM.json').read_bytes())
assert status['primary_exit_code']==0 and status['saved_iteration']==5367
meta=status['complete_final_producer_metadata']
task=dict(schema='mod4.user200.final197.literalJUMP.plane.recorded.v1',epoch=time.time(),
    human_request='mujoco给我放一下',model_path=meta['path'],model_SHA=meta['SHA'],model_bytes=meta['bytes'],model_iteration=5367,
    input197_SHA=meta['source_SHA'],qualified197_package_root='/mnt/mod4_linux_durable_20261013/MOD4_JUMP194_REMAINING_PARALLEL_20261031v197/h1_210',
    num_envs=1,maximum_controls=1000,policy_Hz=50,physics_Hz=400,feedback_Hz=100,
    original_reward_snapshot='jump/wheel_legged_gym/envs/base/legged_robot.py',original_JUMP19_config16_and_plane_unmodified=True,
    physics='ownMOD4 nominal400N/k2000/D0white_v3 D1-D7/2.5ms TGS32-4 F32/perenv2mm/mimic.01',
    purpose='One deterministic final5367 first episode in original training plane, for user new local MuJoCo view; not live learning or270 certification',
    counts=dict(model_GPU_byte_reads=1,model_GPU_decodes=1,CPU_model_decodes=0,old_raw_or_reference_reads=0,
        actual_body_pose_buffer_reads_max=1000,extra_PhysX_contact_view_getters=0,original_reward_calls_per_control=1,
        raw_artifact_transfers=1,transfer_integrity_SHA_passes=1,local_visual_byte_passes=1,npz_member_reads_each=1),
    first_episode_only=True,no_learning_or_account_write=True,no_state_force_velocity_injection=True,
    original_caps=dict(worker_seconds=840,parent_wait_seconds=900),
    display='277 original meshes /31 bodies, gray actual endpoint. PPO has no fabricated blue WM or orange teacher.',
    contact_scope='Contact z/was_in_flight and wheel-center z at50Hz are diagnostics, not a certified stable landing or wheel clearance.')
put(B/'TASK200.json',task)
(B/'zonglin2_app_launcher.py').write_bytes((S/'zonglin2_app_launcher.py').read_bytes())
post=(S/'remote193_postcopy_and_frozen_eval.txt').read_text('utf8').replace(OLD,ROOT).replace('193','200')
post=post.replace('capture200_original_Fudan_course_latest188_once.py','capture200_final197_literal_jump_plane_once.py')
ast.parse(post);(B/'remote200_postcopy_and_frozen_capture.txt').write_text(post,encoding='utf8',newline='\n')
install=(S/'install_capture193_original_course_frozen_once.py').read_text('utf8').replace(OLD,ROOT).replace('193','200')
install=install.replace('install_capture200_original_course_frozen_once','install_capture200_final197_literal_jump_plane_once')
install=install.replace("remote200_postcopy_and_frozen_eval.txt","remote200_postcopy_and_frozen_capture.txt")
anchor="def main():\n query="
gates="""def main():
 source=N.parent/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'
 closed=json.loads((source/'reports/ROOT197_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
 cpu=json.loads((source/'reports/ROOT197_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes())
 task=json.loads((N/'TASK200.json').read_bytes())
 assert closed['passed_collection'] and closed['owner_closed']['canonical_None'] and closed['owner_closed']['shared_locks_free']
 assert closed['roles']['h1_210']['qualified_formal'] and cpu['passed'] and cpu['roles']['h1_210']['passed']
 assert closed['formals']['h1_210']['SHA']==cpu['roles']['h1_210']['SHA']==task['model_SHA']
 assert cpu['roles']['h1_210']['saved_iteration']==5367
 query="""
assert install.count(anchor)==1;install=install.replace(anchor,gates)
oldquery="'install_capture200_original_course_frozen_once|admit_delivered185|capture_delivered185|inspect_user_delivered_forward|find_existing_forwarded210_jump|inspect_forward210_|install_and_probe_A_original_fudan|collect_E3_source210|run_ROOT180_latest|run_ONE178_selected|collect_ONE178_original|install_NATIVE178|run_ROOT171_secure|collect188_original_formal_cost_normal900_UNUSED_once|run189_W35_saved_cycle_single_pass_once|start190_|install190_'"
newquery="'install_capture200_final197_literal_jump_plane_once|collect197_original_two_role_formals|launch197_unified_194_remaining|human199_main197_one_saved_status|install198_E0_72_source_CPU|request197_original194_saved|collect194_original|start195_literal|collect195_original|install195_literal'"
assert oldquery in install;install=install.replace(oldquery,newquery)
install=install.replace("human_request='Do not resume; check total-plan DR/400N/50Hz and actual270mm, then continue total plan'","human_request='Show latest primary5367 in local MuJoCo; one new recorded original-JUMP plane episode'")
ast.parse(install);(B/'install_capture200_final197_literal_jump_plane_once.py').write_text(install,encoding='utf8',newline='\n')

view=(S/'view193_latest188_original_Fudan_true_MOD4_V2.py').read_text('utf8').replace('193','200')
view=view.replace("case['model_iteration']==5065 and case['original_Fudan_STAIRS3_reward_and_course']","case['model_iteration']==5367 and case['original_Fudan_JUMP_reward_and_plane']")
view=view.replace('Latest188 original Fudan stairs3 actual PhysX recorded motion','Final197 literal Fudan JUMP plane actual PhysX recorded motion')
view=view.replace('MOD4 latest188 PPO5065 | actual PhysX | original Fudan stairs3 | recorded NEW200','MOD4 final197 PPO5367 | actual PhysX | original Fudan JUMP plane | recorded NEW200')
view=view.replace('model_iteration=5065','model_iteration=5367')
view=view.replace('source200_capture_epoch','source200_capture_epoch')
start=view.index("        heading=f'CLOSED188 TRAINING")
end=view.index("        helptext=",start)
heading='''        forces=packet['wheel_contact_z'][index]
        heading=f'CLOSED197 TRAINING / NEW200 PLANE EVAL | FINAL PPO5367\\nGRAY: actual original PhysX endpoint t={(index+1)*.02:.2f}s / {duration:.2f}s | END: {end}'
        heading+='\\nOriginal Fudan JUMP19 +original16 weights +original flat plane; unchanged'
        heading+=f'\\nTrue MOD4 /400N engineering /50Hz policy /400Hz PhysX /TGS32-4 /D0-D7\\nCommand vx={command[0]:.2f}m/s, yaw={command[2]:.2f}rad/s; speed {state["speed"]:.2f}x'
        heading+=f'\\n50Hz wheel force-z L/R={forces[0]:.1f}/{forces[1]:.1f}N | original flight flag={bool(packet["original_flight_flag"][index])}'
        heading+='\\nContact flight flag is not stable-landing certification. Original termination is retained.'
        heading+='\\nMuJoCo DISPLAY ONLY /recorded actual /no mj_step or local neural CUDA; PPO has no WM prediction'
'''
view=view[:start]+heading+view[end:]
ast.parse(view);(B/'view200_final197_literal_jump_true_MOD4.py').write_text(view,encoding='utf8',newline='\n')
launch=(S/'launch193_user_visible_MuJoCo_V2_once.py').read_text('utf8').replace('193','200').replace('source_iteration=5065','source_iteration=5367')
launch=launch.replace('view200_latest188_original_Fudan_true_MOD4_V2.py','view200_final197_literal_jump_true_MOD4.py')
launch=launch.replace('original_course=True','original_JUMP_plane=True')
ast.parse(launch);(B/'launch200_user_visible_MuJoCo_once.py').write_text(launch,encoding='utf8',newline='\n')
files=[]
for name in ('TASK200.json','capture200_final197_literal_jump_plane_once.py','zonglin2_app_launcher.py'):
    raw=(B/name).read_bytes();ast.parse(raw) if name.endswith('.py') else None
    files.append(dict(relative=name,local_relative=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
put(B/'FROZEN_EVAL200_COMPLETE_MANIFEST.json',dict(epoch=time.time(),schema='mod4.user200.capture.inputs.v1',files=files,task=task))
source=[]
for name in ('remote200_postcopy_and_frozen_capture.txt','install_capture200_final197_literal_jump_plane_once.py','view200_final197_literal_jump_true_MOD4.py','launch200_user_visible_MuJoCo_once.py'):
    raw=(B/name).read_bytes();source.append(dict(path=str(B/name),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
put(R/'FROZEN200_SOURCE_AND_ONE_NEW_DISPLAY_PURPOSE.json',dict(epoch=time.time(),passed_source_preparation=True,
    caller_requires_actual197_closed_and_NEW_formal_CPU=True,task=task,files=files,root_local_sources=source,
    source_AST_parse_only_not_actual_GPU_or_visual_test=True,local_model_raw_NPZ_reads=0,
    extra_contact_view_getters=0,one_original_reward_call_per_control=True,
    old193_source_reused_but_no_old_case_or_entry_replayed=True,
    independent_LOCAL_CPU_preparation_while_original197_collector_waits=True))
print(json.dumps(dict(passed_source=True,model_iteration=5367,root=ROOT,source_files=len(files)+len(source),model_raw_or_SDK_reads=0)))
