"""Freeze a finite, model-free reset-hold comparison without changing the plant."""
from pathlib import Path
import ast,hashlib,json,re,shutil,subprocess,sys,time,traceback

P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
S=T/'MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102'
D=T/'MPC_PLANNED_INITIAL_QUEUE_HOLD_V363_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def replace_once(s,old,new):
    assert s.count(old)==1,(old[:120],s.count(old));return s.replace(old,new,1)

try:
    assert not D.exists();assert read(R/'ACTUAL362_SAVED_ACTUATOR_ORDER_RESET_HOLD_DIAGNOSIS.json')['passed']
    D.mkdir();(D/'reports').mkdir()
    rename=lambda s:re.sub(r'(?<=[A-Za-z_])357(?!\d)','363',s)
    for path in sorted(S.rglob('*')):
        rel=path.relative_to(S)
        if not path.is_file()or'__pycache__'in rel.parts or any(x in rel.parts for x in('reports','replay','RECORDED357_NATIVE_FRAMES'))or path.name.startswith('INDEX357'):continue
        dest=D/rename(str(rel));dest.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix in('.py','.json'):dest.write_text(rename(path.read_text('utf8')),encoding='utf8')
        else:shutil.copyfile(path,dest)
    helper='''"""Seed only the held target after a caller writes a fresh physical pose.
No reset method, RNG, lag, episode count, control clock or PD is changed.
"""
import torch
def seed_planned_leg_hold(queue,ids,actual_leg_q):
    ids=torch.as_tensor(ids,device=queue.device,dtype=torch.long)
    if not len(ids):return
    g=queue.groups['legs']
    assert actual_leg_q.shape==(len(ids),4)and actual_leg_q.dtype==torch.float32
    assert bool(torch.isfinite(actual_leg_q).all())
    assert not bool(g['pending_valid'][ids].any())and not bool(g['applied_valid'][ids].any())
    assert bool((g['last_submit_tick'][ids]==-1).all())
    g['applied'][ids]=actual_leg_q
    g['pending'][ids]=actual_leg_q
'''
    (D/'source/planned_hold363.py').write_text(helper,encoding='utf8')
    w=(D/'source/evaluate363.py').read_text('utf8')
    w=replace_once(w,'jointorder=[source_names.index(aliases.get(n,n))for n in robot.joint_names]',
        "jointorder=[source_names.index(aliases.get(n,n))for n in robot.joint_names]\n from planned_hold363 import seed_planned_leg_hold\n reset_leg_ids=[robot.joint_names.index(n)for n in('left_crank','left_hip','right_crank','right_hip')]")
    w=replace_once(w,'robot.write_root_state_to_sim(root,env_ids=ids);robot.write_joint_state_to_sim(q,dq,env_ids=ids)',
        "robot.write_root_state_to_sim(root,env_ids=ids);robot.write_joint_state_to_sim(q,dq,env_ids=ids)\n   selected_mask=ids>=40;selected_ids=ids[selected_mask]\n   if len(selected_ids):seed_planned_leg_hold(real._physics_action_delay.queue,selected_ids,q[selected_mask][:,reset_leg_ids])")
    w=replace_once(w,"controllers=[SourceEventMPC353(dict(bundle,actual_command_MPC_dt=.01 if i<40 else.02))for i in range(80)]",
        "controllers=[SourceEventMPC353(dict(bundle,actual_command_MPC_dt=.02))for i in range(80)]")
    w=w.replace("group0_39='currentstateMPCsource.01prediction50Hzhold',group40_79='currentstateMPCactual.02prediction50Hzhold'",
        "group0_39='legacy_default_q_queue_hold',group40_79='planned_actual_q_queue_hold'")
    w=w.replace('group_prediction_dt=[.01,.02],group_horizon=[15,8]','group_prediction_dt=[.02,.02],group_horizon=[8,8]')
    w=w.replace('group_MPC_prediction_dt=[.01,.02]','group_MPC_prediction_dt=[.02,.02]')
    w=w.replace('source10ms_prediction_hold20ms','legacy_default_q_queue_hold').replace('actual20ms_prediction_hold20ms','planned_actual_q_queue_hold')
    w=replace_once(w,'selected=[0,1,40,41];old_scene_update=real.scene.update',
        '''selected=[0,1,40,41];old_scene_update=real.scene.update
 actuator_rows=[];actuator_binding={}
 def joint_indices(a):
  value=a.joint_indices
  if isinstance(value,slice):return list(range(len(robot.joint_names)))[value]
  if hasattr(value,'torch'):value=value.torch
  return value.detach().cpu().tolist()if torch.is_tensor(value)else list(value)
 for key in('legs','wheels'):
  actuator=robot.actuators[key];ids=joint_indices(actuator)
  actuator_binding[key]=dict(joint_indices=ids,joint_names=[robot.joint_names[i]for i in ids],stiffness=tensor(actuator.stiffness).cpu().tolist(),damping=tensor(actuator.damping).cpu().tolist(),episode_scale=tensor(actuator.episode_scale).cpu().tolist(),step_scale=tensor(actuator.step_scale).cpu().tolist())
 def instrument_actuator(key):
  a=robot.actuators[key];original=a.compute;names=actuator_binding[key]['joint_names']
  def compute(control_action,joint_pos,joint_vel):
   before=dict(q=tensor(joint_pos)[selected].detach().cpu().tolist(),dq=tensor(joint_vel)[selected].detach().cpu().tolist(),position_target=tensor(control_action.joint_positions)[selected].detach().cpu().tolist(),velocity_target=tensor(control_action.joint_velocities)[selected].detach().cpu().tolist())
   result=original(control_action,joint_pos,joint_vel)
   if len(actuator_rows)<4000:actuator_rows.append(dict(group=key,tick=int(real._sim_step_counter),control=current_control,selected_envs=selected,joint_names=names,active=active[selected].cpu().tolist(),**before,computed_effort=tensor(a.computed_effort)[selected].detach().cpu().tolist(),applied_effort=tensor(a.applied_effort)[selected].detach().cpu().tolist()))
   return result
  a.compute=compute
 for key in('legs','wheels'):instrument_actuator(key)
 # Names come from actual actuator indices; policy channel order is distinct.
 applied_names=actuator_binding['legs']['joint_names']+actuator_binding['wheels']['joint_names']
 put('ACTUAL363_NAMED_ACTUATOR_AND_RESET_PARAMETER_MEMORY.json',dict(actuators=actuator_binding,applied_effort_order=applied_names,policy_order=['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin'],joint_names=list(robot.joint_names),body_names=list(robot.body_names),D0_factor=tensor(real._mild_dr.factor).cpu().tolist(),D0_nominal=tensor(real._mild_dr.nominal).cpu().tolist(),D0_mu=tensor(real._mild_dr.mu).cpu().tolist(),D0_nominal_mass=tensor(real._mild_dr.mass).cpu().tolist(),D0_nominal_inertia=tensor(real._mild_dr.inertia).cpu().tolist(),D0_nominal_COM=tensor(real._mild_dr.com).cpu().tolist(),D2_bias=tensor(real._sensor_mild.bias).cpu().tolist(),D3_delay=tensor(real._feedback_delay_mild.delay).cpu().tolist(),D4={k:{n:tensor(v).cpu().tolist()for n,v in g.items()}for k,g in real._physics_action_delay.queue.groups.items()},D5_gas_stiffness=tensor(robot.data.joint_stiffness)[:,real._spring_pressure.ids].cpu().tolist(),D6_gas_damping=tensor(robot.data.joint_damping)[:,real._gas_damping.ids].cpu().tolist(),D7_COM_delta=tensor(real._chassis_com.component.delta_m).cpu().tolist(),baseline_buffer_memory_not_independent_backend_qualification=True,initial_physical_q=tensor(robot.data.joint_pos).cpu().tolist(),default_q=tensor(robot.data.default_joint_pos).cpu().tolist(),only_group40_79_heldtarget_seeded_to_actual_pose=True,DR_same_distribution_not_exactpaired=True))
 full_cross=torch.zeros(80,2,dtype=torch.bool,device=real.device);full_clear_ever=torch.zeros_like(active);previous_rear=low[:,:,0].clone()''')
    w=replace_once(w,'global flight,first_air,up,cross,land,stable,stable_peak,success,cross_ever,flight_ever,previous,previous_air,support_seen,phys_calls',
        'global flight,first_air,up,cross,land,stable,stable_peak,success,cross_ever,flight_ever,previous,previous_air,support_seen,phys_calls,full_cross,full_clear_ever,previous_rear')
    w=replace_once(w,'cross|=crossing&airborne[:,None]&first[:,None]',
        'cross|=crossing&airborne[:,None]&first[:,None]\n  full_cross|=((previous_rear<0)&(low[:,:,0]>=0)&(low[:,:,2]>=.27))&airborne[:,None]&first[:,None]\n  full_clear_ever|=full_cross.all(-1)&up&first\n  previous_rear=low[:,:,0].clone()')
    w=replace_once(w,'land=torch.where(ontop&cross_ever&first,land+1,torch.zeros_like(land))',
        'land=torch.where(ontop&full_clear_ever&first,land+1,torch.zeros_like(land))')
    w=w.replace("order='leg_crankhip_crankhip_thenwheels'","order=applied_names")
    w=replace_once(w,'first_flight_both_cross=bool(cross_ever[i]),',
        'first_flight_both_cross=bool(cross_ever[i]),first_flight_whole_footprint_clear=bool(full_clear_ever[i]),')
    w=replace_once(w,"cross=sum(r['first_flight_both_cross']for r in results if r['kind']==g),strict=", 
        "cross=sum(r['first_flight_both_cross']for r in results if r['kind']==g),whole_footprint=sum(r['first_flight_whole_footprint_clear']for r in results if r['kind']==g),strict=")
    w=replace_once(w,"put('ACTUAL363_CURRENT_STATE_MPC_CONTROL_TRACE.json'", 
        "put('ACTUAL363_NAMED_ACTUATOR_INPUT_EFFORT_TRACE.json',dict(rows=actuator_rows,inputs_before_compute=True,efforts_after_original_compute=True,order_is_actual_names=True,unchanged_original_compute=True))\n put('ACTUAL363_CURRENT_STATE_MPC_CONTROL_TRACE.json'")
    w=w.replace("group_horizon=[15,8]","group_horizon=[8,8]")
    ast.parse(w);(D/'source/evaluate363.py').write_text(w,encoding='utf8')
    task=read(D/'TASK363_FROZEN.json');task.update(kind='MPC_PLANNED_INITIAL_QUEUE_HOLD_COMPARISON363',worker_SHA=H(D/'source/evaluate363.py'),group_prediction_dt=[.02,.02],group_horizon=[8,8],reset_hold_groups=['legacy_default_q_queue_hold','planned_actual_q_queue_hold'],diagnostic_actuator_names_from_actual_indices=True,source_MPC_prediction_dt=.02,human_request='Finite same plant MPC control handoff repair:40legacydefaultheldtarget vs40plannedactualqheldtarget. Record original actual actuator name/PD/lag/firsteffort, fullDRunpaired, noNN/model/training/account.')
    (D/'TASK363_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
    c=(D/'contract363.py').read_text('utf8').replace('MPC_ACTUAL20MS_PREDICTION_CLOCK_COMPARISON363','MPC_PLANNED_INITIAL_QUEUE_HOLD_COMPARISON363')
    (D/'contract363.py').write_text(c,encoding='utf8')
    for p in D.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
    ns={};exec(compile(c,str(D/'contract363.py'),'exec'),ns);assert ns['validate_task'](task)
    cpu='''from pathlib import Path
import importlib.util,json,sys,torch
D=Path(sys.argv[1]);runtime=Path(sys.argv[2]);sys.path[:0]=[str(runtime),str(D/'source')]
from action_delay_physics_queue import PhysicsActionQueue
from planned_hold363 import seed_planned_leg_hold
q=PhysicsActionQueue(80,'cpu',9137,True);neutral=torch.zeros(80,4)
ids=torch.arange(80);q.reset('legs',ids,neutral);q.reset('wheels',ids,torch.zeros(80,2))
before=q.state_dict();actual=torch.tensor([-.04044726,.45523674,-.04044726,.45523674]).expand(40,4).clone()
globalrng=torch.get_rng_state().clone();seed_planned_leg_hold(q,torch.arange(40,80),actual);after=q.state_dict()
assert torch.equal(globalrng,torch.get_rng_state())
for group in before['groups']:
 for field,old in before['groups'][group].items():
  now=after['groups'][group][field]
  if group=='legs'and field in('applied','pending'):
   assert torch.equal(now[:40],old[:40])and torch.equal(now[40:],actual)
  else:assert torch.equal(now,old),(group,field)
 assert torch.equal(before['rng'][group],after['rng'][group])
selected=q.apply('legs',0);hold=q.groups['legs']['lag_steps']>0
assert torch.equal(selected[40:][hold[40:]],actual[hold[40:]])
assert torch.equal(selected[:40],torch.zeros(40,4))
print(json.dumps(dict(passed=True,changed_only_two_selected_target_buffers=True,lag_rng_episode_clock_exact=True,physics=0,SDK=0,NN=0)))
'''
    (D/'cpu363_queue_hold_no_step.py').write_text(cpu,encoding='utf8')
    cp=subprocess.run(['C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe','-B','-X','utf8',str(D/'cpu363_queue_hold_no_step.py'),str(D),str(T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4')],capture_output=True,text=True,encoding='utf8')
    put(D/'reports/CPU363_QUEUE_HOLD_NO_STEP.json',dict(epoch=time.time(),returncode=cp.returncode,stdout=cp.stdout,stderr=cp.stderr,passed=cp.returncode==0))
    assert cp.returncode==0,cp.stderr
    # No runtime, evaluation, writer or SSH is started by this preparation.
    files=[p for p in sorted(D.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
    put(D/'INDEX363_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
    put(R/'STATIC363_PLANNED_INITIAL_QUEUE_HOLD_COMPARISON.json',dict(epoch=time.time(),passed=True,root=str(D),INDEX_SHA=H(D/'INDEX363_SOURCE_TASK_CALLERS_FROZEN.json'),workerSHA=H(D/'source/evaluate363.py'),pyAST_passed=True,CPU_no_step_passed=True,NN=0,SDK=0,network=0,GO=0,original50action100feedback400physics_PD_limits_DR_preserved=True,only_group40_79_resetheldtarget_seed=True))
    print(json.dumps(dict(prepared=True,root=str(D),INDEX_SHA=H(D/'INDEX363_SOURCE_TASK_CALLERS_FROZEN.json'),CPU_no_step_passed=True,GO=False)))
except BaseException:
    put(R/('LOCAL363_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),network=0,SDK=0,NN=0,GO=0,no_auto_runtime_retry=True));raise
