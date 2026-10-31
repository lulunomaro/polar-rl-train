"""Freeze a single-factor evaluation: original rewards/plant, yaw command set to0."""
from pathlib import Path
import ast,hashlib,json,re,time
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
S=T/'JUMP197_FINAL5367_USER_MUJOCO_V200_20261031_V2'
N=T/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_PRIMARY_E0_EVAL_ONLY_ZERO_YAW_20261031v207'
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
c=read(N/'reports/ROOT197_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json');cpu=read(N/'reports/ROOT197_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')
assert c['passed_collection'] and c['owner_closed']['canonical_None'] and all(x['passed'] for x in cpu['roles'].values())
roles={};files=[]
for key,iteration,source_key,task_key in (('primary',5367,'source_resume194_SHA','typed_JUMP197_resume_task'),('e0',32066,'source_E0_SHA','typed_E0_JUMP198_task')):
    k='h1_210' if key=='primary' else 'e0_72';formal=c['formals'][k];row=c['roles'][k]['formal']
    assert cpu['roles'][k]['saved_iteration']==iteration and cpu['roles'][k]['SHA']==formal['SHA']
    model_path=formal['source'] if key=='primary' else '/mnt/mod4_linux_durable_20261013/MOD4_E0_FINAL32066_SAME_PLANE_HEADLESS_20261031v201/input_E0_final_complete.pt'
    task=read(S/'TASK200.json');task.update(schema='mod4.eval207.only_yaw0.two_qualified_policies.v1',epoch=time.time(),role=key,
        model_path=model_path,model_SHA=formal['SHA'],model_bytes=formal['bytes'],model_iteration=iteration,
        input_source_SHA=row['source_SHA'],source_key=source_key,task_key=task_key,
        qualified197_package_root='/mnt/mod4_linux_durable_20261013/MOD4_JUMP194_REMAINING_PARALLEL_20261031v197/h1_210',
        human_request='为什么这些机器人边跳边转圈；独立评测转向指令0是否仍会转',
        EVAL_only_yaw_command_range=[0.,0.],original_training_yaw_range=[-2.,2.],
        sole_changed_eval_factor='command yaw range only, unchanged reward/weights, vx range/height/reset/DR/seed27/50Hz/physics',
        no_new_GUI=True,no_learning_or_account_write=True)
    del task['input197_SHA'];task['counts']['raw_artifact_transfers']=0;task['counts']['local_visual_byte_passes']=0;task['counts']['npz_member_reads_each']=0
    D=B/key;D.mkdir();put(D/'TASK207.json',task)
    (D/'zonglin2_app_launcher.py').write_bytes((S/'zonglin2_app_launcher.py').read_bytes())
    roles[key]=task
    for name in ('TASK207.json','zonglin2_app_launcher.py'):
        raw=(D/name).read_bytes();files.append(dict(relative=key+'/'+name,local_relative=key+'/'+name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
worker=re.sub(r'(?<![0-9])200(?![0-9])','207',(S/'capture200_final197_literal_jump_plane_once.py').read_text('utf8'))
worker=worker.replace('import hashlib,io,json,os,runpy,sys,time,traceback','import argparse,hashlib,io,json,os,runpy,sys,time,traceback')
worker=worker.replace("P=Path(__file__).resolve().parent\nTASK=json.loads((P/'TASK207.json').read_bytes())", "parser=argparse.ArgumentParser();parser.add_argument('--task',type=Path,required=True);args=parser.parse_args()\nP=args.task.resolve().parent\nTASK=json.loads(args.task.read_bytes())")
anchor="cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=1;cfg.seed=27;cfg.sim.device='cuda:0';sdk.configure(cfg)"
assert worker.count(anchor)==1;worker=worker.replace(anchor,anchor+"\n    cfg.commands.twist.ranges.ang_vel_z=(0.,0.)  # Evaluation command only; no reward or training change.")
old="assert ck['iter']==5367 and ck['source_resume194_SHA']==TASK['input197_SHA'] and ck['typed_JUMP197_resume_task']['reward_weights_and_functions_no_edits']"
new="assert ck['iter']==TASK['model_iteration'] and ck[TASK['source_key']]==TASK['input_source_SHA'] and ck[TASK['task_key']]['reward_weights_and_functions_no_edits']"
assert old in worker;worker=worker.replace(old,new)
worker=worker.replace('source_iteration=5367','source_iteration=TASK[\'model_iteration\']').replace('model_iteration=5367','model_iteration=TASK[\'model_iteration\']')
worker=worker.replace("binding=real.binding_receipt(),policy35_critic38=True", "binding_original_training_scope=real.binding_receipt(),actual_eval_yaw_range=[0.,0.],policy35_critic38=True")
anchor="contact=np.stack([x['wheel_forces_z'] for x in frames]);flight=np.array([x['flight_flag'] for x in frames])"
metric="""
    cmds=np.stack([x['command'] for x in frames]);assert float(np.max(np.abs(cmds[:,2])))==0.
    qx,qy,qz,qw=(root[:,i] for i in (3,4,5,6))
    yaw=np.unwrap(np.arctan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz)))
    yaw_delta=yaw-yaw[0]
    metrics=dict(observed_command_yaw_max_abs=0.,observed_command_vx_range=[float(cmds[:,0].min()),float(cmds[:,0].max())],
        final_world_heading_delta_rad=float(yaw_delta[-1]),max_abs_world_heading_excursion_rad=float(np.max(np.abs(yaw_delta))),
        mean_abs_root_world_angular_z=float(np.mean(np.abs(root[:,12]))),max_abs_root_world_angular_z=float(np.max(np.abs(root[:,12]))),
        maximum_common_wheel_center_world_z_50Hz=float(pos[:,wheels,2].min(1).max()),
        center_height_not_wheel_clearance=True,one_case_not_population_or_stable_landing_certification=True)
"""
assert anchor in worker;worker=worker.replace(anchor,anchor+metric)
worker=worker.replace("controls=completed,physics_callbacks=completed*8,feedback=completed*2,seconds=completed*.02,", "controls=completed,physics_callbacks=completed*8,feedback=completed*2,seconds=completed*.02,role=TASK['role'],eval_only_zero_yaw=metrics,")
worker=worker.replace("NN_policy='final197 deterministic PPO mean'","NN_policy='qualified same-model deterministic PPO mean, eval yaw command0'")
worker=worker.replace('CLOSED197 TRAINING / NEW207 PLANE EVAL; recorded actual, not live learning','CLOSED TRAINING /NEW207 EVAL ONLY ZERO YAW, original rewards retained')
ast.parse(worker)
assert 'nominal_stiffness_N_m\']==2000' in worker and 'queue.control_us=20000' in worker and "CONTROL_US']='20000'" in worker
assert '==2070' not in worker and '20700' not in worker
(B/'evaluate207_qualified_actor_zero_yaw_once.py').write_text(worker,encoding='utf8',newline='\n')
raw=(B/'evaluate207_qualified_actor_zero_yaw_once.py').read_bytes();files.append(dict(relative='evaluate207_qualified_actor_zero_yaw_once.py',local_relative='evaluate207_qualified_actor_zero_yaw_once.py',bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
put(B/'FROZEN207_TWO_QUALIFIED_MODELS_ZERO_YAW_MANIFEST.json',dict(epoch=time.time(),files=files,roles=roles,
    no_model_copied_or_local_decode=True,total_model_GPU_reads=2,total_model_GPU_decodes=2,
    total_maximum_controls=2000,total_original_reward_calls_max=2000,artifact_transfers=0,
    actual_eval_yaw_zero_readback_required=True,original_primary200_E0201_nonzero_yaw_not_replayed=True))
put(R/'FROZEN207_USER_ZERO_YAW_NEW_EVAL_PURPOSE_SOURCE.json',dict(epoch=time.time(),source_AST_passed=True,
    human='所以为什么我看了这么多机器人一直在边跳边转圈',roles=roles,files=files,
    eval_difference='Only commanded yaw0, original reward/function/config/weights/plant/guards unchanged',
    one_genuine_new_N1_first_episode_per_model=True,old_raw_NPZ_or_input_models_read=0,
    new_source_local_GPU_or_model_read=0,no_training_or_account_write=True,no_GUI_switch=True,
    original_private_EX_and_fresh_resources_each_worker=True,worker_seconds=840,parent_wait_each_seconds=900,
    actual_execution_not_yet_run=True))
print(json.dumps(dict(passed_source=True,roles=list(roles),eval_yaw_command_zero=True,reward_and_physics_unchanged=True)))
