from pathlib import Path
import ast,hashlib,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';D=N/'package'
with (R/'SOURCE198_CPU_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(epoch=time.time(),checkpoint_raw_SDK_GPU_remote_reads=0),f)
groups=[]
try:
 O=T/'E0_82_LITERAL_FUDAN_JUMP_PLANE_400N50_START_V195_20261031/train_package'
 for name in ('literal_original_methods.py','literal_original_config.py','jump195_sdk.py','jump195_boundary.py','mod4_literal_math184.py','mod4_literal_math184_v2.py'):
  assert (D/name).read_bytes()==(O/name).read_bytes(),name
 groups.append(dict(name='literal_JUMP_reward_config_and_measured_bridge_byte_identity_to195',passed=True,no_old_fixture_rerun=True))
 task=json.loads((D/'TASK198.json').read_bytes())
 src=json.loads(Path(task['source_fullstate_CPU_report']).read_bytes())
 assert src['passed'] and src['model']['SHA']==task['source_SHA'] and src['model']['bytes']==14031973
 assert src['review']['actor9_critic8_STD6_actor35_critic38'] and src['review']['Adam_states']==17 and src['review']['Adam_step']==641200
 assert src['review']['stored_RSL_iteration']==31984 and src['review']['final_adaptive_optimizer_LR']==task['source_adaptive_LR']
 assert task['formal_source_model']=='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0/adaptation/final_valid_update82.pt'
 groups.append(dict(name='published_original72_E0_fullstate_metadata_reused_not_model_reread',passed=True))
 sys.path.insert(0,str(N));from e0_jump198_task_protocol import validate_go
 go=dict(role_key='e0_72',run_id='SOURCE198_ONLY',source_model_SHA=task['source_SHA'],literal_original_fudan_JUMP=True,
  max_parent_seconds=3900,exit_headroom_seconds=300,learning_started_epoch=1000.,save_deadline=4600.,nominal_end_epoch=4900.)
 assert validate_go(go,'SOURCE198_ONLY',task,1001.)
 negative=[]
 for k,value in dict(role_key='h1_210',run_id='foreign',source_model_SHA='0'*64,literal_original_fudan_JUMP=False,
  max_parent_seconds=7500,exit_headroom_seconds=0,save_deadline=4599.,nominal_end_epoch=4800.).items():
  try:validate_go({**go,k:value},'SOURCE198_ONLY',task,1001.)
  except AssertionError:negative.append(k)
  else:raise AssertionError('accepted '+k)
 try:validate_go(go,'SOURCE198_ONLY',task,4600.)
 except AssertionError:negative.append('expired')
 else:raise AssertionError('expired')
 groups.append(dict(name='e0_role_original3900_3600_300_GO_checks',passed=True,refusals=negative))
 text=(D/'run198_E0_JUMP72_400N50_worker.py').read_text('utf8');ast.parse(text)
 for s in ["ck['iter']==31984",'==14031973','==641200','==641220','iter=31984+updates','runner.current_learning_iteration=31985',"runner.alg.load(ck,None,True)","torch.equal(value,ck[name][key])",'typed_E0_JUMP198_task']:
  assert s in text,s
 assert "assert std==task['learned_STD6']" not in text
 groups.append(dict(name='worker_literal_full_actor_critic_STD_optimizer_LR_counter_restore_contract',passed=True))
 report=dict(epoch=time.time(),passed=True,groups=groups,source_CPU_only=True,negative_cases=len(negative),model_or_raw_byte_reads=0,
  actual_target72_source_GPU_and_fullstate_restore_still_required=True)
except BaseException:
 report=dict(epoch=time.time(),passed=False,groups=groups,error=traceback.format_exc(),not_physical_policy_failure=True);raise
finally:
 with (R/'SOURCE198_E0_FULLSTATE_LITERAL_JUMP_GO_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=True,groups=len(groups),refusals=len(negative),model_reads=0)))
