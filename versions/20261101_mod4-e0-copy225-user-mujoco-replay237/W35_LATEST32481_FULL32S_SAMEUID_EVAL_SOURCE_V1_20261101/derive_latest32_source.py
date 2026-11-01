"""New bounded LOCAL source derivation;old B/222/227 models and artifacts untouched."""
from pathlib import Path
import ast,hashlib,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
B=T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/B_LOSSLESS_EVAL_SOURCE'
G=T/'E2_PLAN_MIMIC01_BEFORE_CONSTRUCTOR_REPAIR_V3_20261101'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def main():
 assert json.loads((R/'DERIVE_LATEST32_PURPOSE_FROZEN.json').read_bytes())['executions']==1
 assert ref(B/'INDEX227B_FROZEN.json')['SHA']=='8325c9949f3824b35b36f097a5a96fedb39630da548bf1f84e79da3dbf954ff6'
 put(R/'DERIVE_LATEST32_ONCE_CONSUMED.json',dict(epoch=time.time(),source_only=True))
 for name in ('rm70_intervals227.py','positional_rows227.py','decode227_positional.py'):
  with (N/name).open('xb') as f:f.write((B/name).read_bytes())
 guard=(G/'e2_guard01_before_constructor_v3.py').read_text(encoding='utf8').replace('E2_V3_PLANNED_MIMIC01_BEFORE_ENV_CONSTRUCTOR','W35_LATEST32481_PLANNED_MIMIC01_BEFORE_ENV_CONSTRUCTOR')
 guard+='''

def install_before_main(namespace,receipt_path):
 build=namespace['build_env'];glob=build.__globals__;old=glob['configure_intro']
 assert old.__module__=='config214_training' and old.__name__=='configure208'
 def configured(cfg):
  recipe=old(cfg)
  enforce_before_constructor(cfg,receipt_path)
  return recipe
 glob['configure_intro']=configured
 def uninstall():glob['configure_intro']=old
 return uninstall
'''
 write(N/'guard_latest32.py',guard)
 worker=(B/'evaluate227_CLOSED_W35_FULL_RM70_LOSSLESS_UNUSED_once.py').read_text(encoding='utf8')
 worker=worker.replace("MODEL='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'", "from contract_latest32 import SHA as MODEL,BYTES,ITER,ADAM,LR,UPDATES,validate_task")
 worker=worker.replace("assert task['kind']=='NEW227_W35_CLOSED_FULL_RM70_SKILL_ONLY'", "validate_task(task,admitted=True)")
 worker=worker.replace('17619269','17619333').replace('32404','32481').replace('649720','651260')
 worker=worker.replace("task['model_new_PPO_updates']==68", "task['model_new_PPO_updates']==77")
 worker=worker.replace('actual_current_CNone_private_shared_resources_admitted','actual_current_authority_private_shared_resources_admitted')
 worker=worker.replace('.00017085937500000009','.0002562890625000001').replace('qualified219_job_root','qualified_latest227D_job_root')
 worker=worker.replace("cache.state['actual_new_PPO_updates']==68", "cache.state['actual_new_PPO_updates']==77")
 worker=worker.replace('ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f','343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd')
 worker=worker.replace("OUT=job/'actual227'", "OUT=job/'actual_latest32'")
 worker=once(worker,"deadline=time.time()+3600;ns=book=cache=None", "deadline=time.time()+3600;ns=book=cache=None;guard_uninstall=None")
 worker=once(worker," entry=mod/'train_full214.py'", " entry=mod/'train_full214.py';assert H(entry)==task['original_entry_SHA']")
 worker=once(worker,"   import rescue_training", "   from guard_latest32 import install_before_main\n   guard_uninstall=install_before_main(ns,OUT/'BEFORE_CONSTRUCTOR_MIMIC01_ACTUAL.json')\n   import rescue_training")
 worker=once(worker,"    assert runner.current_learning_iteration==32481", "    assert real.cfg.terminations.closure.params['threshold']==.002 and real.cfg.terminations.mimic.params['threshold']==.01\n    guard=read(OUT/'BEFORE_CONSTRUCTOR_MIMIC01_ACTUAL.json');assert guard['passed'] and guard['planned_effective_mimic_radians']==.01 and guard['all_other_termination_params_unchanged_in_JSON_supported_projection']\n    assert runner.current_learning_iteration==32481")
 worker=once(worker,"     source_cache=cache.receipt(),original_rough_command_and_reward_unchanged=True)", "     source_cache=cache.receipt(),original_rough_command_and_reward_unchanged=True,guard_before_constructor=guard,actual_mimic_radians=.01,actual_closure_m=.002)")
 worker=once(worker,"feedback=48,optimizer_steps=0)", "feedback=48,optimizer_steps=0,actual_mimic_radians=.01,actual_closure_m=.002)")
 worker=once(worker,"      full_expert_skill='UNKNOWN'", "      explicit_mimic_guard_tightening_from_legacy05=True,actual_mimic_radians=.01,actual_closure_m=.002,full_expert_skill='UNKNOWN'")
 worker=once(worker,"   put('SOURCE227_FINAL_READ_COUNTS.json',cache.receipt())", "   put('SOURCE227_FINAL_READ_COUNTS.json',cache.receipt())\n   if guard_uninstall is not None:guard_uninstall()")
 write(N/'evaluate_latest32481_full32s_ROOT_ONLY_once.py',worker)
 put(R/'SOURCE_GUARD_CHAIN_AND_REUSE_FROZEN.json',dict(epoch=time.time(),old_B_INDEX=ref(B/'INDEX227B_FROZEN.json'),
  old_worker=ref(B/'evaluate227_CLOSED_W35_FULL_RM70_LOSSLESS_UNUSED_once.py'),
  unchanged_observer_writer_decoder=[ref(N/x) for x in ('rm70_intervals227.py','positional_rows227.py','decode227_positional.py')],
  source_guard_origin='Selected mod4_task.py30ce4112... mimic default803 and DoneTerm1797 .05;closure1794 .002;train_full214 configure137 then constructor140;config214 calls e1_scene_query_resource/e1_terrain_runtime,none overrides mimic. Original physical-term repr equality preserves it.',
  actual_old_W35_mimic05_source_scope=True,new_eval_explicit_before_constructor01=True,
  old_reports01_not_effective_configuration_proof=True,new32s_case_and_model_read_pending=True,
  source_reader_notes=['Initial222directoryguess absent;correct frozen W35_FULL_RM70_CLOSED_SKILL_SOURCE_V222_20261101 located.','Original contract222.py is under ROOT222_TASK_ACTUAL_32404;root path absent. No fixture/raw/model opened.'],
  model_asset_raw_Torch_SDK_network_Git=0))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'DERIVE_LATEST32_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
