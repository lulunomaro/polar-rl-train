from pathlib import Path
import importlib.util,sys,json,os,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def load(mode):
 name='new99_'+mode;spec=importlib.util.spec_from_file_location(name,B/('review_NEW99_'+mode+'_formal_initial_whole_CPU_UNUSED_once_v2.py'));module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);module.COLLECTED=module.C/'reports/TWO99_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_V2_ACTUAL.json';return module
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 mods=[load(mode) for mode in ['continue97','restart0']]
 for m in mods:
  m.closure(m.read(m.COLLECTED))
  assert not any(m.R.glob('NATIVE99_'+('continue97' if m is mods[0] else 'restart0')+'_NEW_FORMAL_INITIAL_WHOLE_CPU_STARTED_ACTUAL.json'))
 with (R/'TWO99_COMBINED_INITIAL_CPU_V3_CONSUMED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),both_closure_guards_passed_before_PT=True,NEW_formal_loads_planned=2,normal86_witness_loads_planned=1),f,indent=2)
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
 with (R/'TWO99_COMBINED_INITIAL_CPU_V3_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,NEWformal_loads=2,normal86_witness_loads=1,input_native97_or_native0_loads=0,no_actor_WM_forward_GPU_or_account=True),f,indent=2)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('TWO99_COMBINED_INITIAL_CPU_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_repeat_initial_model_load=True),f,indent=2)
  raise
