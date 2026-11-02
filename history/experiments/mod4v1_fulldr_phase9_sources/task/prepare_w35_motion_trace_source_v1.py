"""SOURCE_ONLY mechanistic trace of existing new89aca mean policy, no commands/reward/actions changed.
New scope is200 controls/4simseconds, not replayed full32 graduation or another PPOwindow.
"""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parent;S=R/'staged_sources/W35_MOD4V1_POSTADAPT_EVAL_V1';D=R/'staged_sources/W35_MOD4V1_MOTION_TRACE_V1';assert not D.exists();D.mkdir()
s=(S/'evaluate_mod4v1_w35.py').read_text(encoding='utf-8');s=s.replace('task[\'controls_max\']==1600','task[\'controls_max\']==200').replace('range(1600)','range(200)').replace('completed==1600','completed==200').replace('requested_max_controls=1600','requested_max_controls=200').replace("task['worker_seconds']==3600 and task['parent_seconds']==3780","task['worker_seconds']==900 and task['parent_seconds']==1200").replace('deadline=time.time()+3600','deadline=time.time()+900')
a="     try:\n      with torch.inference_mode():"
b="""     motion_rows=[]
     trace_ids=torch.arange(0,20000,625,device=real.device,dtype=torch.long)
     wheel_ids,_=robot.find_joints(['left_wheel_spin','right_wheel_spin'],preserve_order=True)
     def trace_tensor(x):return tensor(x).detach()
     def trace_values(x):return trace_tensor(x)[trace_ids].cpu().tolist()
     def trace_input(o):
      p=o['policy'] if isinstance(o,dict) or hasattr(o,'keys') else o
      command=real.command_manager.get_command('twist')
      return dict(actual_BODY_command=trace_values(command),policy_input35=trace_values(p),command_vs_policy_first3_max=float((trace_tensor(p)[:,:3]-trace_tensor(command)).abs().max()))
     try:
      with torch.inference_mode():"""
assert s.count(a)==1;s=s.replace(a,b)
a="        action=runner.alg.actor(obs,stochastic_output=False);obs,reward_value,done,extra=vec.step(action);completed+=1"
b="""        trace_before=trace_input(obs) if i in (0,1,23,49,99,199) else None
        action=runner.alg.actor(obs,stochastic_output=False);obs,reward_value,done,extra=vec.step(action);completed+=1
        if trace_before is not None:
         wheels=real.action_manager.get_term('wheels')
         row=dict(control=i,env_ids=trace_ids.cpu().tolist(),before_actor=trace_before,raw_policy_action6=trace_values(action),processed_wheel_velocity_target=trace_values(wheels.processed_actions),wheel_measured_rad_s=trace_values(trace_tensor(robot.data.joint_vel)[:,wheel_ids]),wheel_applied_torque_Nm=trace_values(trace_tensor(robot.data.applied_torque)[:,wheel_ids]),body_linear_velocity_m_s=trace_values(robot.data.root_lin_vel_b),done_after_step=trace_values(done),reward=trace_values(reward_value))
         target=getattr(robot.data,'joint_vel_target',None)
         if target is not None:row['actual_robot_wheel_velocity_target']=trace_values(trace_tensor(target)[:,wheel_ids])
         motion_rows.append(row)
"""
assert s.count(a)==1;s=s.replace(a,b)
a="      facts=book.finish();book.finished=True"
b="""      put('MOTION_COMMAND_OBS_ACTION_ACTUAL_TRACE.json',dict(kind='OWN89ACA_NO_COMMAND_OR_REWARD_PATCH_NO_PPO_MECHANISTIC_TRACE',source_SHA=MODEL,controls=completed,seconds=.02*completed,tracked_envs=32,rows=motion_rows,trace_scope='Actualsamplercommands andraw35input/mean6action/processedwheel target/measuredomega/torque/rootvelocity; noextraactorcalls/RNGdraws/physicssetters',not_skill_graduation=True))
      facts=book.finish();book.finished=True"""
assert s.count(a)==1;s=s.replace(a,b);ast.parse(s);(D/'evaluate_mod4v1_w35.py').write_text(s,encoding='utf-8')
s=(S/'postadapt_eval_contract.py').read_text(encoding='utf-8').replace('MOD4V1_W35_POSTADAPT_SAVEDMODEL_FULL32_EVAL_V1','MOD4V1_W35_POSTADAPT_MOTION_WIRING_TRACE200_V1').replace("t['controls_max']==1600","t['controls_max']==200").replace("t['worker_seconds']==3600 and t['parent_seconds']==3780","t['worker_seconds']==900 and t['parent_seconds']==1200").replace("t['original_eval_parent_holds_private_and_validation_EX']","t['actual_parent_privateEX_finiteSH']");ast.parse(s);(D/'postadapt_eval_contract.py').write_text(s,encoding='utf-8')
for name in('rm70_intervals227.py','positional_rows227.py','decode227_positional.py'):(D/name).write_bytes((S/name).read_bytes())
rows=[{'relative':p.name,'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()}for p in D.iterdir()if p.is_file()];(D/'SOURCE_INDEX.json').write_text(json.dumps({'kind':'SOURCE_ONLY_OWN89ACA_MECHANISTIC_TRACE200','files':rows,'source_checkpoint_reads':0,'SDK_or_canonical_calls':0,'newlearning':False,'nooriginalcommandrewardphysicschanged':True,'scope':'One future newpurpose trace only, notfull32repeat; actual parent needed forGPU0privateEX+finiteSH/freshresource+sourcebinding; originalall20k restore notsliced'},indent=2),encoding='utf-8');print(json.dumps({'source_dir':str(D),'files':rows},indent=2))
