"""ROOT-only NEW source/SDK-package metadata admission;no old V5 fixture.

No Torch/SDK/App/actor imports,PT,NPZ,USD/raw reads or scene construction.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import argparse,ast,hashlib,importlib.metadata as md,importlib.util,json,sys,time,traceback
MODEL='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'
KIND='NEW_E2_FROM226_V3_LEXICAL_SOURCE_SDK_METADATA'


def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def H(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);a=p.parse_args();J=a.job_root.resolve()
 expected=read(J/'EXPECTED_E2_FROM226_V3_TARGET_METADATA.json');assert expected['kind']==KIND and expected['source_SHA']==MODEL
 put(J/'METADATA_E2_FROM226_V3_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose=KIND,model_reads=0,old_fixture_replays=0))
 try:
  receipt=read(J/'E2_INSTALLED226_SOURCE_ASSET_PRODUCER_RECEIPT.json')
  assert receipt['actual_postcopy_fullSHA_verified'] and receipt['job_root']==str(J)
  installed={x['relative']:x for x in receipt['files']}
  for row in expected['installed_rows']:
   assert installed[row['relative']]['SHA']==row['SHA'] and installed[row['relative']]['bytes']==row['bytes'],row['relative']
  checked={};w=None
  for row in expected['source_rows']:
   path=J/row['relative'];assert path.resolve().is_relative_to(J) and path.suffix in ('.py','.json','.txt')
   raw=path.read_bytes();assert len(raw)==row['bytes'] and H(raw)==row['SHA'],row['relative']
   checked[row['relative']]=H(raw)
   if row['relative'] in expected['AST_selected_rows']:ast.parse(raw.decode('utf8'),filename=str(path))
   if row['relative']=='E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json':w=json.loads(raw)
  assert w and w['passed'] and w['model']['SHA']==MODEL and w['model']['bytes']==14615089
  assert w['whole_model_all_tensors_finite'] and w['all_critical_D1_D7_and_E2_command_CPU_validated']
  assert w['actor9_critic8_STD6_original35_38'] and w['all17_Adam_and_original_nonLR_optimizer_settings']
  assert w['Adam_step']==859300 and w['stored_iteration']==42822 and w['adaptive_LR']==.00022500000000000002
  assert checked['E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json']==expected['CPU_witness_SHA'] and checked['evaluate_e2_world213.py']==expected['worker_SHA']
  versions={k:md.version(k) for k in expected['versions']};assert versions==expected['versions']
  origins={k:importlib.util.find_spec(k).origin for k in ('torch','rsl_rl','isaacsim','isaaclab','tensordict')}
  lab=Path(origins['isaaclab']).parent;rsl=Path(origins['rsl_rl']).parent
  for row in expected['RSL_sources']:
   raw=(rsl/row['relative']).read_bytes();assert len(raw)==row['bytes'] and H(raw)==row['SHA']
  assert H((lab/'utils/math.py').read_bytes())==expected['SDK_math_SHA']
  command=lab/'managers/command_manager.py';command_raw=command.read_bytes()
  sys.path.insert(0,str(J))
  from e2_early_original_resample_observer_v2_complete import validate_actual_target_source
  from original_flat_height_provider_v1 import validate_flat_height_source
  mod=J/'runtime/isaac/mod4'
  method=validate_actual_target_source(command_raw,(mod/'e2_directional_spin_runtime_v1.py').read_bytes(),
   (J/'e2_command_checkpoint_v1213.py').read_bytes(),(J/'sensor_resume_contract213.py').read_bytes(),expected['method_contract'])
  ground=validate_flat_height_source(mod/'mod4_task.py',expected['ground_provider_contract'])
  worker=J/'evaluate_e2_world213.py';tree=ast.parse(worker.read_bytes())
  def calls(code):
   key=ast.dump(ast.parse(code,mode='eval').body,include_attributes=False)
   return [n for n in ast.walk(tree) if isinstance(n,ast.Call) and ast.dump(n,include_attributes=False)==key]
  hook=calls('early.install(DirectionalSpinCommand,sensor_resume_contract,e2_command_checkpoint_v1)')
  invoke=calls("ns['main']()");actor=calls('runner.alg.actor(obs,stochastic_output=False)');step=calls('vec.step(action)')
  assert len(hook)==len(invoke)==len(actor)==len(step)==1 and (hook[0].lineno,hook[0].col_offset)<(invoke[0].lineno,invoke[0].col_offset) and (actor[0].lineno,actor[0].col_offset)<(step[0].lineno,step[0].col_offset)
  assert any(isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range' and ast.literal_eval(n.iter.args[0])==1200 for n in ast.walk(tree))
  for name in ('sensor_resume_contract213.py','feedback_delay_checkpoint213.py','action_delay_checkpoint213.py','spring_pressure_checkpoint213.py','gas_damping_checkpoint213.py','chassis_pd_checkpoint213.py','e2_command_checkpoint_v1213.py'):
   assert (J/name).read_text(encoding='utf8').startswith('from source_cache213 import cached_load,cached_H'),name
  result=dict(epoch=time.time(),kind=KIND,passed=True,source_SHA=MODEL,source213_worker_SHA=expected['worker_SHA'],
   expected226_SHA=H((J/'EXPECTED_E2_FROM226_V3_TARGET_METADATA.json').read_bytes()),actual_versions=versions,actual_module_origins=origins,
   checked_source_rows=checked,actual_CommandTerm_source_path=str(command),actual_CommandTerm_source_SHA=H(command_raw),
   method_source_proof=method,ground_source_proof=ground,source_early_hook_and_1200_mean_step_graph=True,
   actual_source_asset_install_receipt_checked_without_binary_reads=True,
   selected_CPU_witness_SHA=expected['CPU_witness_SHA'],qualified_fullstate_CPU_proof_reused=True,
   model_reads=0,model_decodes=0,old_fixture_replays=0,Torch_or_SDK_scene_imports=0,App_or_actor_constructions=0,GPU_calls=0,
   physical_binary_reads=0,no_account_or_GO=True,actual_new_model_fullrestore_native24_early_event='PENDING_ROOT_GPU_CASE',
   full_E2_skill=False,complete_SuperMimic=False)
  path=J/'E2_TARGET_SOURCE_SDK_METADATA_ACTUAL.json';put(path,result)
  print(json.dumps(dict(passed=True,report_path=str(path),report_SHA=H(path.read_bytes()),model_reads=0,SDK_scene=False)))
 except BaseException:
  put(J/('ORIGINAL_E2_FROM226_V3_TARGET_METADATA_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),
   no_model_GPU_scene_or_old_fixture_execution=True,no_automatic_retry=True));raise


if __name__=='__main__':main()
