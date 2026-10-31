from pathlib import Path
import copy,hashlib,json,sys,time
N=Path(__file__).resolve().parent;R=N/'reports';sys.path.insert(0,str(N/'control'))
with (R/'TASK194_CONTROLLER_CPU_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(epoch=time.time()),f)
import jump194_protocol as p
manifest=hashlib.sha256((N/'TRAIN194_COMPLETE_MANIFEST.json').read_bytes()).hexdigest()
spec=dict(key='h1_210',execution_backend='source210',max_parent_seconds=7500,exit_headroom_seconds=300,source_SHA='5932295297ed93b65fd88fe142d6fc66099c0a936f23091a79a3b2752c51dfa4',num_envs=20000,literal_jump194_400N50=True,no_comparison_arms=True,manifest_SHA=manifest)
assert p.validate_schedule(dict(experts={'h1_210':spec}))
v=dict(passed=True,kind='JUMP194_LITERAL_400N50_ACTUAL_CPU_NATIVE8_AND_DELIVERY4999_FULLSTATE_REUSE',source_SHA=spec['source_SHA'],source_iteration=4999,Adam_step=100020,all_actor_critic_optimizer_tensors_finite=True,actual_35_38_6_shapes=True,target_CPU_actual_waited_RC=0,target_GPU0PT_actual_waited_RC=0,actual_native_controls=8,actual_physics_callbacks=64,literal_reward_text_identity19=True,manifest_SHA=manifest,target64_private_EX_released=True)
def row(v):return dict(key='h1_210',manifest_SHA=manifest,phase='ready',original_error=False,closed_source_CPU=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()))
assert p.valid_ready(row(v),spec)
negatives=[]
for key,bad in dict(passed=False,kind='OLD_STAIRS3',source_SHA='0'*64,source_iteration=0,Adam_step=0,all_actor_critic_optimizer_tensors_finite=False,actual_35_38_6_shapes=False,target_CPU_actual_waited_RC=1,target_GPU0PT_actual_waited_RC=1,actual_native_controls=0,actual_physics_callbacks=32,literal_reward_text_identity19=False,manifest_SHA='0'*64,target64_private_EX_released=False).items():
 x={**v,key:bad};assert not p.valid_ready(row(x),spec),key;negatives.append(key)
for field,bad in [('max_parent_seconds',3900),('num_envs',4096),('source_SHA','0'*64),('literal_jump194_400N50',False)]:
 try:p.validate_schedule(dict(experts={'h1_210':{**spec,field:bad}}))
 except AssertionError:negatives.append('schedule.'+field)
 else:raise AssertionError(field)
with (R/'ROOT194_TaskGO_CONTROLLER_CPU_NEGATIVES_ACTUAL.json').open('x') as f:json.dump(dict(epoch=time.time(),passed=True,positive=2,rejections=len(negatives),cases=negatives,no_GO_account_model_or_network=True),f,indent=2)
print(json.dumps(dict(passed=True,rejections=len(negatives))))
