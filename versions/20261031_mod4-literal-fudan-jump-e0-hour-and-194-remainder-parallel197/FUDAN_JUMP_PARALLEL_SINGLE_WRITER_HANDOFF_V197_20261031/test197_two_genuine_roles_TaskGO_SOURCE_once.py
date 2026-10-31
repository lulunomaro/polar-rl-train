from pathlib import Path
import copy,hashlib,json,sys,time
N=Path(__file__).resolve().parent;R=N/'reports';sys.path.insert(0,str(N))
with (R/'ROOT197_TWO_ROLE_SOURCE_CPU_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(epoch=time.time(),model_raw_GPU_remote_reads=0),f)
import parallel197_protocol as p
e=dict(key='e0_72',execution_backend='target72',GPU_UUID=sorted(p.GPUS72)[0],max_parent_seconds=3900,exit_headroom_seconds=300,
 source_SHA=p.E0,source_iteration=31984,source_Adamstep=641200,num_envs=20000,literal_original_fudan_JUMP=True,no_reward_or_physics_change=True,manifest_SHA='e'*64)
h=dict(key='h1_210',execution_backend='source210',GPU_UUID=p.GPU210,max_parent_seconds=1900,exit_headroom_seconds=300,
 remaining_primary_seconds=1600,old194_requested_seconds=7200,old194_used_seconds=5600,source_SHA='a'*64,source_iteration=5200,source_Adamstep=104040,
 num_envs=20000,literal_original_fudan_JUMP=True,no_reward_or_physics_change=True,manifest_SHA='h'*64)
schedule=dict(experts=dict(e0_72=e,h1_210=h));assert p.validate_schedule(schedule)
negative=[]
for role,changes in [('e0_72',dict(source_SHA='b'*64)),('e0_72',dict(max_parent_seconds=7500)),('e0_72',dict(GPU_UUID=p.GPU210)),
 ('h1_210',dict(source_Adamstep=100020)),('h1_210',dict(remaining_primary_seconds=0)),('h1_210',dict(old194_used_seconds=0)),('h1_210',dict(max_parent_seconds=3900))]:
 s=copy.deepcopy(schedule);s['experts'][role].update(changes)
 try:p.validate_schedule(s)
 except AssertionError:negative.append(dict(role=role,bad=changes))
 else:raise AssertionError(changes)
for role,spec in schedule['experts'].items():
 v=dict(passed=True,kind='LITERAL_JUMP_PARALLEL197_READY',source_SHA=spec['source_SHA'],source_iteration=spec['source_iteration'],Adam_step=spec['source_Adamstep'],
  all_actor_critic_optimizer_tensors_finite=True,actual_35_38_6_shapes=True,actual_original_JUMP19_text_identity=True,source_fullstate_CPU_passed=True,
  actual_target0PT_waited_RC=0,actual_target0PT_controls=8,actual_target0PT_physics=64,actual_target0PT_feedback=16,target0PT_private_EX_released=True,manifest_SHA=spec['manifest_SHA'])
 def row(v):return dict(key=role,phase='ready',manifest_SHA=spec['manifest_SHA'],original_error=False,closed_source_CPU=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()))
 assert p.valid_ready(row(v),spec)
 for key,bad in dict(passed=False,kind='UNPREPARED',source_SHA='0'*64,source_iteration=0,Adam_step=0,all_actor_critic_optimizer_tensors_finite=False,
  actual_35_38_6_shapes=False,actual_original_JUMP19_text_identity=False,source_fullstate_CPU_passed=False,actual_target0PT_waited_RC=1,actual_target0PT_controls=0,
  actual_target0PT_physics=0,actual_target0PT_feedback=0,target0PT_private_EX_released=False,manifest_SHA='0'*64).items():
  assert not p.valid_ready(row({**v,key:bad}),spec);negative.append(dict(role=role,bad_field=key))
  
with (R/'ROOT197_TWO_ROLE_TaskGO_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,positive_cases=3,negative_cases=len(negative),cases=negative,
 one_canonical_writer_only=True,no_runtime_or_skill_claim=True),f,indent=2)
print(json.dumps(dict(passed=True,negative_cases=len(negative))))
