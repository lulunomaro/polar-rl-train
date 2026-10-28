from pathlib import Path
import importlib.util,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def load(mode):
 name='native103_'+mode;s=importlib.util.spec_from_file_location(name,B/('review_NEW103_'+mode+'_formal_initial_whole_CPU_UNUSED_once.py'));m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 mods=[load(mode) for mode in ['seed27','seed28']]
 for m in mods:m.closure(m.read(m.COLLECTED))
 with (R/'TWO103_INITIAL_TWO_FORMAL_CPU_CONSUMED_ACTUAL.json').open('x') as f:json.dump(dict(epoch=time.time(),both_closures_before_any_model_read=True,NEW_formals_planned2_shared86witness1=True),f,indent=2)
 import torch
 torch.set_num_threads(2);assert not torch.cuda.is_initialized();witness=torch.load(mods[0].B/'job0/source/H1_closed86_policy_only_update138.pt',map_location='cpu',weights_only=False)
 for m in mods:
  for name,other in list(sys.modules.items()):
   path=getattr(other,'__file__',None)
   if path and any(Path(path).is_relative_to(p.B) for p in mods):sys.modules.pop(name,None)
  m.main(witness)
 with (R/'TWO103_INITIAL_TWO_FORMAL_CPU_QUALIFIED_ACTUAL.json').open('x') as f:json.dump(dict(passed=True,NEW_formal_loads=2,shared_normal86_loads=1,input_native101_loads=0,actual270mm_task_and_physical_seeds_bound=True,no_actor_WM_forward_GPU_or_account=True),f,indent=2)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('TWO103_INITIAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),no_repeat_initial_model_load=True),f,indent=2)
  raise
