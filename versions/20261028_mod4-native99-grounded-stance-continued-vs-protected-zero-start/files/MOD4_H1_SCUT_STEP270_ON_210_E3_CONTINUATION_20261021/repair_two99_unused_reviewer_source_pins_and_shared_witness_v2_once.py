from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
B=L/'TWO99_NEW_TWO_NATIVE_FORMAL_INITIAL_CPU_SOURCE_V1';R=B/'reports'
(R/'V1_UNUSED_REVIEWER_SOURCE_PIN_KEY_REFUSAL_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),original_v1_never_executed=True,before_any_model_load=True,error="SOURCE_PINS has final/native_args/native_contract; counters are in migration.SOURCES['h1'], not SOURCE_PINS['source_progress']",preserve_original_v1=True),indent=2),encoding='utf8')
entries=[]
for mode in ['continue97','restart0']:
 p=B/f'review_NEW99_{mode}_formal_initial_whole_CPU_UNUSED_once_v1.py';s=p.read_text()
 s=s.replace('verify_saved_migration,NATIVE_CONTRACT,SOURCE_PINS','verify_saved_migration,NATIVE_CONTRACT,SOURCE_PINS,SOURCES')
 s=s.replace("SOURCE_PINS['source_progress']","SOURCES['h1']")
 s=s.replace('def main():','def main(shared_witness=None):')
 old="witness=torch.load(B/'job0/source/H1_closed86_policy_only_update138.pt',map_location='cpu',weights_only=False)"
 assert s.count(old)==1;s=s.replace(old,"witness=shared_witness if shared_witness is not None else torch.load(B/'job0/source/H1_closed86_policy_only_update138.pt',map_location='cpu',weights_only=False)")
 s=s.replace('dict(NEWformal=1,frozen_normal86=1,input_native97_or_native0=0)','dict(NEWformal=1,frozen_normal86=1 if shared_witness is None else 0,shared_normal86_reused=shared_witness is not None,input_native97_or_native0=0)')
 ast.parse(s);q=B/f'review_NEW99_{mode}_formal_initial_whole_CPU_UNUSED_once_v2.py';q.write_text(s,encoding='utf8');entries.append(q)
combined='''from pathlib import Path
import importlib.util,sys,json,os,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def load(mode):
 name='new99_'+mode;spec=importlib.util.spec_from_file_location(name,B/('review_NEW99_'+mode+'_formal_initial_whole_CPU_UNUSED_once_v2.py'));module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 mods=[load(mode) for mode in ['continue97','restart0']]
 for m in mods:
  m.closure(m.read(m.COLLECTED))
  assert not any(m.R.glob('NATIVE99_'+('continue97' if m is mods[0] else 'restart0')+'_NEW_FORMAL_INITIAL_WHOLE_CPU_STARTED_ACTUAL.json'))
 with (R/'TWO99_COMBINED_INITIAL_CPU_CONSUMED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),both_closure_guards_passed_before_PT=True,NEW_formal_loads_planned=2,normal86_witness_loads_planned=1),f,indent=2)
 import torch
 torch.set_num_threads(2);assert not torch.cuda.is_initialized()
 witness=torch.load(mods[0].B/'job0/source/H1_closed86_policy_only_update138.pt',map_location='cpu',weights_only=False)
 for m in mods:
  # Each branch uses distinct payload imports; evict only its source module names.
  roots=[str(m.B),str(m.B/'source'),str(m.B/'source/sm_deps'),str(m.B/'job0/runtime/isaac/mod4')]
  for name,module in list(sys.modules.items()):
   path=getattr(module,'__file__',None)
   if path and any(Path(path).is_relative_to(other.B) for other in mods):sys.modules.pop(name,None)
  sys.path[:]=[p for p in sys.path if not any(p==str(other.B/sub) for other in mods for sub in ['.','source','source/sm_deps','job0/runtime/isaac/mod4'])]
  m.main(witness)
 with (R/'TWO99_COMBINED_INITIAL_CPU_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,NEWformal_loads=2,normal86_witness_loads=1,input_native97_or_native0_loads=0,no_actor_WM_forward_GPU_or_account=True),f,indent=2)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('TWO99_COMBINED_INITIAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_repeat_initial_model_load=True),f,indent=2)
  raise
'''
ast.parse(combined);q=B/'review_TWO_NEW99_formals_one_shared_witness_initial_CPU_UNUSED_once_v2.py';q.write_text(combined,encoding='utf8');entries.append(q)
(B/'FROZEN_TWO99_INITIAL_CPU_REVIEWERS_INDEX_V2.json').write_text(json.dumps(dict(epoch=time.time(),unused=True,V1_refused_before_execution=True,combined_entry=q.name,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in entries]),indent=2),encoding='utf8')
print(json.dumps(dict(prepared_v2=True,combined_entry=str(q),no_model_run=True)))
