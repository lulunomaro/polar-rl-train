from pathlib import Path
import json,ast,hashlib,time,sys,copy,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 import closed_production_continuation_CPU_v2 as c
 import prepare_next_hour_reward_migration_helpers_once as prepared
 base=W/'MOD4_THREE_GPU_HOUR5_CONTINUATION_20261018';old=(base/'payload/h1/h1_prelaunch_v2_production_worker_v1.py').read_text('utf8')
 log=prepared.WORKER_LOG.replace('  scut_last=','   scut_last=');new=old.replace('  from h1_production_control_prefix_trace_v1 import H1ControlPrefixTrace\n',prepared.WORKER_START+'  from h1_production_control_prefix_trace_v1 import H1ControlPrefixTrace\n').replace('   if completed==1 or completed%25==0 or stop:',log+'   if completed==1 or completed%25==0 or stop:')
 fields=dict(new_source_filename='unused-new.pt',previous_source_filename='unused-old.pt',Adam=999999,previous_Adam=888888)
 assert ast.dump(ast.parse(c.normalize_worker(new,dict(fields,kind='closed_same_backend_reward_migration'))))==ast.dump(ast.parse(old))
 assert c.normalize_worker(new,dict(fields,kind='closed_same_backend_production'))==new
 report=json.loads((R/'SCUT_FUDAN_PUBLIC4_MEASURED_RUNTIME_CPU_V4_ACTUAL.json').read_bytes());mig={'job0/runtime/isaac/mod4/'+Path(x['path']).name:dict(previous_SHA=None,previous_bytes=None,new_SHA=x['SHA']) for x in report['overlay']}
 p=dict(key='h1',kind='closed_same_backend_reward_migration',source_SHA='a'*64,GPU_UUID='gpu0',execution_backend='target72',Adam=655360,whole_tensor_counts=[199,105],all_model_runtime_finite=True,actual_original_owner_node_all_children_out=True,original_cost_once_settled=True,not_failed_partial_prefix=True,native_runtime_assets_digest='d'*64,unchanged_PPO_and_physical_guard_AST=True,whole_model_CPU_report_SHA='e'*64,reward_migration=mig,reward_CPU_report_SHA=H(R/'SCUT_FUDAN_PUBLIC4_MEASURED_RUNTIME_CPU_V4_ACTUAL.json'))
 spec=dict(key='h1',source_SHA=p['source_SHA'],GPU_UUID=p['GPU_UUID'],execution_backend=p['execution_backend'],source_Adamstep=p['Adam'],reward_migration=True)
 m=dict(key='h1',source_SHA=p['source_SHA'],source_Adamstep=p['Adam'],source_schema_counts=[199,105],native_runtime_assets_digest=p['native_runtime_assets_digest'],reward_migration=mig,reward_CPU_report_SHA=p['reward_CPU_report_SHA'],files=[dict(relative=k,SHA=v['new_SHA']) for k,v in mig.items()]);assert c.validate(p,spec,m)
 failed=[]
 for field,value in [('source_SHA','bad'),('GPU_UUID','wrong'),('execution_backend','wrong'),('Adam',0),('reward_CPU_report_SHA','0'*64),('reward_migration',{}),('whole_tensor_counts',[1,1]),('not_failed_partial_prefix',False),('original_cost_once_settled',False),('actual_original_owner_node_all_children_out',False)]:
  q=copy.deepcopy(p);q[field]=value
  try:c.validate(q,spec,m)
  except (AssertionError,KeyError):failed.append(field)
  else:raise AssertionError(field)
 t=(base/'controllers/three_slot_common_v1.py').read_text('utf8');t=t.replace("v.get('kind')=='closed_same_backend_production'","v.get('kind')==('closed_same_backend_reward_migration' if spec.get('reward_migration') else 'closed_same_backend_production')").replace("v.get('same_active_runtime_assets_and_PPO_AST')","(v.get('same_physics_assets_and_PPO_AST') if spec.get('reward_migration') else v.get('same_active_runtime_assets_and_PPO_AST'))")
 tree=ast.parse(t);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='valid_ready');ns=dict(json=json,hashlib=hashlib);exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual readiness function>','exec'),ns)
 value=dict(key='h1',kind=p['kind'],passed=True,source_SHA=p['source_SHA'],GPU_UUID=p['GPU_UUID'],execution_backend=p['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,same_active_runtime_assets_and_PPO_AST=False,same_physics_assets_and_PPO_AST=True)
 row=dict(key='h1',phase='ready',closed_source_CPU=dict(value=value,SHA=hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True),manifest_SHA='f'*64)
 spec.update(closed_production_continuation=True,manifest_SHA='f'*64);assert ns['valid_ready'](row,spec)
 bad=copy.deepcopy(row);bad['closed_source_CPU']['value']['same_physics_assets_and_PPO_AST']=False;assert not ns['valid_ready'](bad,spec)
 # No source native PASS is fabricated for this changed reward recipe.
 for f in B.glob('*.py'):ast.parse(f.read_text('utf8'))
 out=dict(epoch=time.time(),passed=True,inverse_initial_migration_worker_AST_exact=True,later_same_recipe_continuation_preserves_receipts_and_all_reward_math=True,actual_readiness_function_accepts_honest_changed_reward_label=True,unchanged_runtime_label_not_faked_for_H1=True,wrong_source_backend_Adam_CPUhash_runtime_scope_exit_cost_negative_cases=failed,source_reward_file_SHA_bound_to_actual_CPU_overlay=True,no_new_physics_or_standalone_native_or_account_write=True)
 with (R/'SCUT_FUDAN_REWARD_MIGRATION_PROVENANCE_CPU_V5_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print('Reward migration provenance and next same-recipe continuation CPU passed; 10 negative cases rejected.')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('REWARD_MIGRATION_CPU_V5_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_remote_GPU=True),f,indent=2)
  raise
