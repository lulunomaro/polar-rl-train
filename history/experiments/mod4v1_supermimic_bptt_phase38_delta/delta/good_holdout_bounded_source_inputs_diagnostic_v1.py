"""NEW concentrated source/metadata diagnostic; never prepare, stage or native.
Whole pinned D4.native_boundary, original producer guard and vendor tree predicates
are reused. Native-root byte reads have an immutable same-byte logical cache.
"""
from pathlib import Path
import ast,hashlib,importlib.util,io,json,os,runpy,sys,time,traceback
D=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;H=lambda b:hashlib.sha256(b).hexdigest();cfg=json.loads((D/'INPUT.json').read_bytes());N=Path(cfg['native_root']);roles=('CURB_PROTECTED878','SLOPE135');V=N/'roles/E3/worker_sources/supermimic_vendor_v2';cache={};physical={};logical={};old_open=Path.open
for name,pin in cfg['program_inputs'].items():
 b=(D/name).read_bytes();assert(len(b),H(b))==(pin['bytes'],pin['SHA256'])
s=runpy.run_path(str(D/'stage_good_expert_holdout_v4.py'),run_name='_source_inputs_d4_no_main');assert s['SOURCE_DERIVATION_VERSION']==4
spec=importlib.util.spec_from_file_location('_original_producer_guard_source_only_v1',D/'producer_teacher_guard_v1.py');g=importlib.util.module_from_spec(spec);sys.modules[spec.name]=g;spec.loader.exec_module(g)
core={N/'roles'/r/rel for r in roles for rel in('TASK.json','INSTALL_MANIFEST.json',g.WORKER_REL,g.BRIDGE_REL)};upstream={N/x for x in('OWNER_PLAN.json','OWNER_EXIT_ACTUAL.json','COHORT_FINAL.json')}|{N/'roles'/r/x for r in roles for x in('PARENT_WAITED_ACTUAL.json','production/FINAL.json')}
names=[]
with os.scandir(V)as entries:
 for e in entries:
  if not s['denied'](e.name):names.append(e.name)
names=sorted(names);assert len(names)==7 and all(n.endswith('.py')and '/'not in n for n in names),'strict flat vendor7 names differ';core|={V/n for n in names};allowed=core|upstream
class NoNative:
 def find_spec(self,fullname,path=None,target=None):
  if fullname.split('.')[0]in('torch','isaaclab','isaacsim','warp','pxr'):raise AssertionError('native import forbidden')
sys.meta_path.insert(0,NoNative())
def cached_open(path,mode='r',*args,**kwargs):
 p=Path(os.path.abspath(path))
 if p.is_relative_to(N):
  assert p in allowed and mode in('r','rb'),'outside exact readonly source/metadata input set'
  logical[str(p)]=logical.get(str(p),0)+1
  if p not in cache:
   with old_open(p,'rb')as f:b=f.read(8*1024*1024+1)
   assert len(b)<=8*1024*1024;cache[p]=b;physical[str(p)]=1
  b=cache[p]
  return io.BytesIO(b)if mode=='rb'else io.StringIO(b.decode(kwargs.get('encoding')or'utf8'))
 return old_open(path,mode,*args,**kwargs)
v=dict(kind='ACTUAL_GOOD_HOLDOUT_CONCENTRATED_SOURCE_INPUT_DIAGNOSTIC_V1',epoch=time.time(),native_root=str(N),predicates_are_whole_original_pinned_functions=True,prepare_preflight_stage_parent_SDK_model_raw_bank_C_lock_signal_operations=0,Gate1='UNKNOWN',stage2_GO=False,errors=[],guards={})
Path.open=cached_open
try:
 try:producers,boundary=s['native_boundary'](N);v['native_closed_boundary']=boundary
 except BaseException as e:producers={};v['errors'].append(dict(component='original_native_boundary',type=type(e).__name__,message=str(e),traceback=traceback.format_exc()))
 for role in roles:
  try:v['guards'][role]=g.derive_producer_guard(producers[role])
  except BaseException as e:v['errors'].append(dict(component=role,type=type(e).__name__,message=str(e),traceback=traceback.format_exc()))
 try:
  vendor=s['tree'](V);digest=s['digest_tree'](vendor);assert set(vendor)==set(names)and(digest['files'],digest['SHA'])==s['VENDOR_PIN'];init=ast.parse((V/'__init__.py').read_bytes());assert len(init.body)==1 and isinstance(init.body[0],ast.Expr)and isinstance(init.body[0].value,ast.Constant)and type(init.body[0].value.value)is str;v['vendor']=dict(digest,actual_names=names,complete_python_AST_parsed=True,docstring_only_init=True)
  for name in names:ast.parse((V/name).read_bytes())
 except BaseException as e:v['errors'].append(dict(component='vendor7',type=type(e).__name__,message=str(e),traceback=traceback.format_exc()))
finally:Path.open=old_open
rows=[]
for p in sorted(cache,key=str):
 b=cache[p];row=dict(path=str(p),relative_to_native=p.relative_to(N).as_posix(),bytes=len(b),SHA256=H(b),physical_byte_reads=physical[str(p)],logical_byte_requests=logical[str(p)],core_source_input=p in core)
 if p in core:
  target=D/'captured_inputs'/p.relative_to(N);target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb')as f:f.write(b)
  row['captured_relative']=target.relative_to(D).as_posix()
 rows.append(row)
v.update(input_rows=rows,core_source_files_expected=15,core_source_files_read=sum(p in core for p in cache),upstream_metadata_files_read=sum(p in upstream for p in cache),all_original_paths_read_once=all(x==1 for x in physical.values()),status='PASS'if not v['errors']and core<=set(cache)and len(v['guards'])==2 else'FAIL')
with(D/'RESULT.json').open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2));assert v['status']=='PASS',v['errors']
