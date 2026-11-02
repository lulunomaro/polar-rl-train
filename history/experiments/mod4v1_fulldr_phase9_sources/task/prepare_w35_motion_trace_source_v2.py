"""AST-located source-only trace insertion. Preserve unusedfailedV1; no source model/SDK read."""
from pathlib import Path
import ast,json,hashlib,textwrap
R=Path(__file__).resolve().parent;S=R/'staged_sources/W35_MOD4V1_POSTADAPT_EVAL_V1';D=R/'staged_sources/W35_MOD4V1_MOTION_TRACE_V2';assert not D.exists()
s=(S/'evaluate_mod4v1_w35.py').read_text(encoding='utf-8');original=s;s=s.replace("task['controls_max']==1600","task['controls_max']==200").replace('range(1600)','range(200)').replace('completed==1600','completed==200').replace('requested_max_controls=1600','requested_max_controls=200').replace("task['worker_seconds']==3600 and task['parent_seconds']==3780","task['worker_seconds']==900 and task['parent_seconds']==1200").replace('deadline=time.time()+3600','deadline=time.time()+900')
tree=ast.parse(s);parents={child:node for node in ast.walk(tree)for child in ast.iter_child_nodes(node)};loops=[n for n in ast.walk(tree)if isinstance(n,ast.For)and isinstance(n.iter,ast.Call)and isinstance(n.iter.func,ast.Name)and n.iter.func.id=='range'and any(isinstance(a,ast.Constant)and a.value==200 for a in n.iter.args)];assert len(loops)==1;loop=loops[0];anchor=loop
while not isinstance(anchor,ast.Try):anchor=parents[anchor]
lines=s.splitlines(keepends=True);prefix=lines[anchor.lineno-1][:len(lines[anchor.lineno-1])-len(lines[anchor.lineno-1].lstrip())];lp=lines[loop.body[2].lineno-1][:len(lines[loop.body[2].lineno-1])-len(lines[loop.body[2].lineno-1].lstrip())]
def block(text,p):return ''.join(p+x+'\n'if x else'\n'for x in textwrap.dedent(text).strip('\n').splitlines())
setup=block('''
motion_rows=[]
trace_ids=torch.arange(0,20000,625,device=real.device,dtype=torch.long)
wheel_ids,_=robot.find_joints(['left_wheel_spin','right_wheel_spin'],preserve_order=True)
def trace_tensor(x):return tensor(x).detach()
def trace_values(x):return trace_tensor(x)[trace_ids].cpu().tolist()
def trace_input(o):
 p=o['policy'] if isinstance(o,dict) or hasattr(o,'keys') else o
 command=real.command_manager.get_command('twist')
 return dict(actual_BODY_command=trace_values(command),policy_input35=trace_values(p),command_vs_policy_first3_max=float((trace_tensor(p)[:,:3]-trace_tensor(command)).abs().max()))
''',prefix)
a='action=runner.alg.actor(obs,stochastic_output=False);obs,reward_value,done,extra=vec.step(action);completed+=1';at=[i for i,l in enumerate(lines)if l.strip()==a];assert len(at)==1;i=at[0];actionprefix=lines[i][:len(lines[i])-len(lines[i].lstrip())]
replacement=block('''
trace_before=trace_input(obs) if i in (0,1,23,49,99,199) else None
action=runner.alg.actor(obs,stochastic_output=False);obs,reward_value,done,extra=vec.step(action);completed+=1
if trace_before is not None:
 wheels=real.action_manager.get_term('wheels')
 row=dict(control=i,env_ids=trace_ids.cpu().tolist(),before_actor=trace_before,raw_policy_action6=trace_values(action),processed_wheel_velocity_target=trace_values(wheels.processed_actions),wheel_measured_rad_s=trace_values(trace_tensor(robot.data.joint_vel)[:,wheel_ids]),wheel_applied_torque_Nm=trace_values(trace_tensor(robot.data.applied_torque)[:,wheel_ids]),body_linear_velocity_m_s=trace_values(robot.data.root_lin_vel_b),done_after_step=trace_values(done),reward=trace_values(reward_value))
 target=getattr(robot.data,'joint_vel_target',None)
 if target is not None:row['actual_robot_wheel_velocity_target']=trace_values(trace_tensor(target)[:,wheel_ids])
 motion_rows.append(row)
''',actionprefix)
lines[i]=replacement;lines[anchor.lineno-1]=setup+lines[anchor.lineno-1];s=''.join(lines)
a='facts=book.finish();book.finished=True';assert s.count(a)==1;s=s.replace(a,"put('MOTION_COMMAND_OBS_ACTION_ACTUAL_TRACE.json',dict(kind='OWN89ACA_SAME_COMMAND_REWARD_NO_PPO_TRACE200',source_SHA=MODEL,controls=completed,seconds=.02*completed,tracked_envs=32,rows=motion_rows,not_skill_graduation=True)); "+a);ast.parse(s)
D.mkdir();(D/'evaluate_mod4v1_w35.py').write_text(s,encoding='utf-8');s=(S/'postadapt_eval_contract.py').read_text(encoding='utf-8').replace('MOD4V1_W35_POSTADAPT_SAVEDMODEL_FULL32_EVAL_V1','MOD4V1_W35_POSTADAPT_MOTION_WIRING_TRACE200_V1').replace("t['controls_max']==1600","t['controls_max']==200").replace("t['worker_seconds']==3600 and t['parent_seconds']==3780","t['worker_seconds']==900 and t['parent_seconds']==1200").replace("t['original_eval_parent_holds_private_and_validation_EX']","t['actual_parent_privateEX_finiteSH']");ast.parse(s);(D/'postadapt_eval_contract.py').write_text(s,encoding='utf-8')
for name in('rm70_intervals227.py','positional_rows227.py','decode227_positional.py'):(D/name).write_bytes((S/name).read_bytes())
rows=[{'relative':p.name,'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()}for p in D.iterdir()if p.is_file()];v={'kind':'SOURCE_ONLY_OWN89ACA_MECHANISTIC_TRACE200_V2','files':rows,'source_checkpoint_reads':0,'SDK_or_canonical_calls':0,'newlearning':False,'nooriginalcommandrewardphysicschanged':True,'failedV1_preserved':'GeneratorASSERT beforetargetsourcecreated; baretry+inference textanchor notuniquelymatched, V2 ASTanchorsone200control loop, noSDK/PT/Task consumed','future_parent':'GPU0privateEX+finiteSH/freshresources, scope200/4s, worker900/parent1200, onecachedSource89aca purpose notfull32repeat'};(D/'SOURCE_INDEX.json').write_text(json.dumps(v,indent=2),encoding='utf-8');(R/'reports/W35_MOTION_TRACE_V1_STATIC_ANCHOR_ERROR_AND_V2_FIX.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
