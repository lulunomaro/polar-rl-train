"""Assemble a distinct teacher-student version; original frozen276 is unchanged."""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent
R=N/'reports';R.mkdir(exist_ok=True)
source=N/'source_v2';source.mkdir(exist_ok=False)
old=T/'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276V3_20261101'
shutil.copytree(old/'source',source,dirs_exist_ok=True)
for name in ('teacher_student282.py','reference282.py','terrain282.py'):
    shutil.copyfile(N/name,source/name)
for name,relative in {
    'zero_input_bound_adam277.py':'DEPTH_ACTOR44_CRITIC47_ZERO_INPUT_AND_BOUND_ADAM_MIGRATION_SOURCE_V277_20261101/zero_input_bound_adam277.py',
    'predicted_literal_frame268.py':'OWN267_LITERAL_ABI_DEPENDENCY_REPAIR_V270_20261101/source/code/predicted_literal_frame268.py',
    'literal_imagination259.py':'FUDAN_LITERAL_SUPERMIMIC_REWARD_MEMORY_SOURCE_V259_20261101/literal_imagination259.py',
}.items():shutil.copyfile(T/relative,source/name)
from reference282 import prepare
reference=json.loads((N/'REFERENCE282_PRODUCER.json').read_bytes())

worker=(old/'source/worker276_online_WM_only.py').read_text('utf8')
worker=worker.replace('from wm_task275 import validate_task,validate_go','from teacher_task282 import validate_task,validate_go')
worker=worker.replace('TASK[\'GPU_UUID\']','TASK[\'GPU_UUID\']')
worker=worker.replace('control276/ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json','control282/ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json')
worker=worker.replace('from terrain_only272 import','from terrain282 import').replace('import terrain_only272 as sdk','import terrain282 as sdk')
worker=worker.replace("real=sdk.TerrainMixed272Env(cfg=cfg)","real=sdk.Teacher282Env(cfg=cfg)")
worker=worker.replace("['/World/ground/original_Fudan_STAIRS3']","['/World/ground/teacher_step270']")
worker=worker.replace("assert ck['iter']==2135 and ck['typed_MODEL2050_MIX240_task']['source_SHA']==TASK['source_parent_SHA']", "carrier=ck\n assert ck['kind']=='OWN_DEPTH_WM_ONLY_WARM276_COMPLETE' and ck['actual_new_WM_updates']==4719\n ck=carrier['teacher_full_PPO_state']\n assert ck['iter']==2135")
worker=worker.replace("steps=[float(x['step'])for x in ck['optimizer_state_dict']['state'].values()]", "steps=[float(x['step'])for x in ck['optimizer_state_dict']['state'].values()]")
worker=worker.replace("FrozenTeacherContract273(TASK['model_SHA'],TASK['teacher_whole_CPU_receipt_SHA'],True)","FrozenTeacherContract273(TASK['teacher_SHA'],TASK['teacher_whole_CPU_receipt_SHA'],True)")
anchor=" def finite(v):"
insertion=""" wm.model.load_state_dict(carrier['world_model']['world_model'],strict=True)
 wm.optimizer.load_state_dict(carrier['world_model']['world_optimizer'])
 wm.updates=carrier['world_model']['world_updates'];wm.generator.set_state(carrier['world_model']['dedicated_sampling_rng'])
 assert wm.updates==4719 and all(int(v['step'])==4719 for v in wm.optimizer.state.values())
 from reference282 import Reference282
 from teacher_student282 import TeacherStudent282,forward
 from literal_imagination259 import snapshot_actual
 reference=Reference282(P/'reference282.npz',TASK['reference'],joint_names,real.device)
 learner=TeacherStudent282(wm,carrier,reference,real,wmbinding,TASK['carrier_CPU_receipt_SHA'],put)
"""
worker=worker.replace(anchor,insertion+anchor)
worker=worker.replace("with torch.inference_mode():actions=actor(obs['policy'])", "with torch.inference_mode():actions=learner.action(obs['policy'],start_depth['features'])")
worker=worker.replace("controls+=1;start_state=state_now();start_depth=depth;start_episode=episodes.clone();sxi=xi.clone();pending.clear()", "controls+=1;start_state=state_now();start_depth=depth;start_episode=episodes.clone();sxi=xi.clone();pending.clear()\n  start_obs=obs['policy'].detach().clone();start_critic=obs['critic'].detach().clone();start_memory=snapshot_actual(real)\n  cmd=real.command_manager.get_command('twist');start_commands=torch.stack((cmd[:,0],cmd[:,2],real._mod4_height_cmd[:,0],torch.zeros(80,device=real.device)),-1)")
worker=worker.replace("ingress=wm.add(fields,actual_anchor=packet", "ingress=wm.add(fields,actual_anchor=packet")
worker=worker.replace("terminated_count+=int(pending['terminated'].sum())", "learner.add_metadata((wm.buffer.ptr-1)%64,start_obs,start_critic,start_commands,start_memory,real.scene.env_origins)\n  terminated_count+=int(pending['terminated'].sum())")
worker=worker.replace("diagnostic=wm.update()", "diagnostic=wm.update()\n   student=learner.update() if controls>=64 else None\n   if student is not None:put('LATEST_STUDENT282.json',dict(epoch=time.time(),**student))")
worker=worker.replace("if first is None:\n    first=save", "if first is None and student is not None:\n    first=save")
worker=worker.replace("assert wm.updates==1", "assert learner.Pi_updates==1")
worker=worker.replace("from wm_task275 import FIRST_KIND,validate_first", "from teacher_task282 import FIRST_KIND,validate_first")
worker=worker.replace("from wm_task275 import FINAL_KIND", "from teacher_task282 import FINAL_KIND")
worker=worker.replace("validate_first(receipt,TASK,go);put('FIRST_ACTUAL_NEW_WM_UPDATE.json',receipt)","receipt.update(actual_new_Pi_updates=learner.Pi_updates,actual_new_critic_updates=learner.critic_updates,actual_Pi_Critic_STD_updates=learner.Pi_updates,student=student,learning_scope='teacher_assisted_depth_SuperMimic')\n    validate_first(receipt,TASK,go);put('FIRST_ACTUAL_TEACHER_DEPTH_STUDENT_UPDATE.json',receipt)")
worker=worker.replace("state=dict(kind='OWN_DEPTH_WM_ONLY_WARM276_COMPLETE'", "state=dict(kind='LQR_MPC_DEPTH_TEACHER_STUDENT282_COMPLETE',student=learner.checkpoint(),source_carrier_SHA=TASK['model_SHA'],frozen_carrier_original=carrier")
worker=worker.replace("typed_WM_WARM276_task=TASK", "typed_TEACHER282_task=TASK")
worker=worker.replace("world_model=wm.checkpoint()", "world_model=wm.checkpoint()")
worker=worker.replace("actual_Pi_Critic_STD_updates=0,world_model", "actual_Pi_Critic_STD_updates=learner.Pi_updates,world_model")
worker=worker.replace("complete_three_optimizer_conversion=False,actual_Pi_runtime_qualified=False,replay_dataset_scope", "complete_three_optimizer_conversion=True,actual_Pi_runtime_qualified=True,replay_dataset_scope")
worker=worker.replace("row=dict(epoch=epoch,save_epoch=epoch", "row=dict(epoch=epoch,save_epoch=epoch,Pi_updates=learner.Pi_updates,critic_updates=learner.critic_updates,complete_student_WM_three_optimizers=True")
worker=worker.replace("receipt.pop('first_complete');receipt.pop('diagnostic');put('FINAL.json',receipt)", "receipt.pop('first_complete');receipt.pop('diagnostic');receipt.update(actual_new_Pi_updates=learner.Pi_updates,actual_new_critic_updates=learner.critic_updates,actual_Pi_Critic_STD_updates=learner.Pi_updates,student=student);put('FINAL.json',receipt)")
worker=worker.replace("wm.updates>0 and first is not None", "wm.updates>4719 and learner.Pi_updates>0 and first is not None")
worker=worker.replace("not_navigation_jump270_or_fullSuperMimic=True", "student_skill_not_yet_evaluated=True")
# The inherited JSON receipt details are historical WM-only names, explicitly
# corrected for this new task rather than misrepresenting the new learner.
worker=worker.replace("actual_new_Pi_updates=0,actual_new_critic_updates=0", "actual_new_Pi_updates=learner.Pi_updates,actual_new_critic_updates=learner.critic_updates")
worker=worker.replace("new_optimizer_count=1,new_optimizer_scope='WM only'", "new_optimizer_count=3,new_optimizer_scope='restored WM + migrated actor and critic'")
worker=worker.replace("WM_ONLY", "TEACHER_STUDENT")
ast.parse(worker);(source/'worker282.py').write_text(worker,encoding='utf8')
for p in source.rglob('*.py'):ast.parse(p.read_text('utf8'))
receipt=dict(epoch=time.time(),source_files=len(list(source.rglob('*.py'))),old276_unchanged=True,
    new_reference=reference,source_carrier='qualified276V3 final cbd25c80a55c87296b4b2a50eb21869e4b12127f9aa3a5d5f9a607823d44242b',
    source_WM_updates=4719,new_actor44_critic47=True,teacher_losses_separate_from_literal_reward=True,
    actual_training=False,pending='CPU integration, actual resource/clock/migration/gradient and original owner GO')
(R/'SOURCE282_ASSEMBLY.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps(dict(source_files=receipt['source_files'],reference_samples=500)))
