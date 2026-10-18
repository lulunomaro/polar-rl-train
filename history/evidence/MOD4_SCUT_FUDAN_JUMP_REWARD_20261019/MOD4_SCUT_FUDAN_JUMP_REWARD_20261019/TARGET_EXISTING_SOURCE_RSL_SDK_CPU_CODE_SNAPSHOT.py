
from pathlib import Path
import sys,os,json,time,hashlib,ast,importlib.util
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch;torch.set_num_threads(2);B=Path(sys.argv[1]);mf=B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';m=json.loads(mf.read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rng=torch.get_rng_state().clone()
for r in m['files']:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and not p.is_symlink() and p.stat().st_size==r['bytes'] and H(p)==r['SHA'],r['relative']
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
source=B/'job0/source'/m['source_filename'];assert H(source)==m['source_SHA'];s=torch.load(source,map_location='cpu',weights_only=False);counts=[0,0]
def finite(x):
 if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for v in x.values():finite(v)
 elif isinstance(x,(tuple,list)):
  for v in x:finite(v)
finite(s);assert counts==m['source_schema_counts'] and len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8 and len(s['optimizer_state_dict']['state'])==17 and {int(z['step']) for z in s['optimizer_state_dict']['state'].values()}=={m['source_Adamstep']};rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)));actual=[]
for r in m['expected_actual_RSL_sources']:
 p=rsl/r['relative'];assert p.stat().st_size==r['bytes'] and H(p)==r['SHA'];actual.append(dict(path=str(p),SHA=H(p)))
sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))/'utils/math.py';assert H(sdk)==m['expected_actual_SDK_math_SHA'];assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();v=dict(epoch=time.time(),passed_CPU_only=True,key=m['key'],source_SHA=m['source_SHA'],source_schema_counts=counts,all17Adam=m['source_Adamstep'],all_target_manifest_SHA_AST_passed=True,manifest_SHA=H(mf),actual_RSL_sources=actual,actual_SDK_math=dict(path=str(sdk),SHA=H(sdk)),CPU_RNG_unchanged0CUDA0optimizer=True,native_and_PPO_not_yet_passed=True);(B/'TARGET_FULL_SOURCE_INSTALLED_RSL_SDK_CPU_ADMITTED_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
