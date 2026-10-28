"""Strict text-only nominal400N asset/runtime candidate generator.

No existing payload is mutated; no USD/PT/raw asset is opened or hashed.
Creates only isolated Python/JSON copies and a tiny USDA override layer.
All changes are exact paths/tokens; original physics/command/save code stays.
"""
from pathlib import Path,PurePosixPath
import ast,copy,hashlib,json,re

K=2000.;QHI=.020639440248416612
GAS=('left_gas_slide','right_gas_slide')
RT='job0/runtime/isaac/mod4/'
SPECS={
 'spring_pressure_index_runtime.py':[(b'3500N/m',b'2000N/m',1),(b'self.nominal=torch.tensor([3500.,3500.],device=env.device)',b'self.nominal=torch.tensor([2000.,2000.],device=env.device)',1)],
 'spring_pressure_audit_runtime.py':[(b'(nominal==3500)',b'(nominal==2000)',1)],
 'spring_nominal_sdk_readback.py':[(b"values['physx_stiffness_N_m']==3500",b"values['physx_stiffness_N_m']==2000",1)],
 'spring_pressure_training_env.py':[(b'nominal_stiffness_N_m=3500',b'nominal_stiffness_N_m=2000',1),(b'actual_stiffness_bounds_N_m=[3150,3850]',b'actual_stiffness_bounds_N_m=[1800,2200]',1)]}
REPLACEMENTS={RT+n for n in SPECS}|{'job0/assets/import_contract.json',RT+'import_contract.json','job0/runtime/reports/SOURCE_FREEZE.json'}
OLD_PY_SHA={'spring_pressure_index_runtime.py':'b03152dd24fb70aabc0cc16ab7274d8030d4aaf4c7768e156fcb0705f18ef154','spring_pressure_audit_runtime.py':'559cfc159312e94a5d9fe572d0a8ec65482835eb0d0afb3de99cf31baa44779b','spring_nominal_sdk_readback.py':'f6c14e7178d4844ae227b515a0f8eb00cf4b94835be5ad80ef9da2d2240d4145','spring_pressure_training_env.py':'c91694490a844daaf7bd5ba9cf77c0769aedaff39775dd0cdc1cf598d270f594'}
OLD_CONTRACT_SHA='cbcdacdf2b15d6a5fb1e5650e418443ff376ee23334e47e1ef36fcb79c32719f'
def require(v,msg):
 if not v:raise ValueError(msg)
def SHA(raw):return hashlib.sha256(raw).hexdigest()
def source_path(root,relative):
 root=Path(root).resolve();p=(root/relative).resolve();require(p.is_relative_to(root),'source path escape');return p
def scalar_spans(text):
 """JSON scalar offsets with named paths, rejecting duplicate object keys."""
 dec=json.JSONDecoder();spans={}
 def space(i):
  while i<len(text) and text[i].isspace():i+=1
  return i
 def walk(i,path):
  i=space(i)
  if text[i]=='{':
   i=space(i+1);seen=set()
   if text[i]=='}':return i+1
   while True:
    key,j=dec.raw_decode(text,i);require(type(key) is str and key not in seen,'duplicate/invalid JSON key');seen.add(key);i=space(j);require(text[i]==':','JSON colon');i=walk(i+1,path+(key,));i=space(i)
    if text[i]=='}':return i+1
    require(text[i]==',','JSON comma');i=space(i+1)
  if text[i]=='[':
   i=space(i+1);index=0
   if text[i]==']':return i+1
   while True:
    i=walk(i,path+(index,));index+=1;i=space(i)
    if text[i]==']':return i+1
    require(text[i]==',','JSON array comma');i=space(i+1)
  value,end=dec.raw_decode(text,i);spans[path]=(i,end,value);return end
 end=walk(0,());require(space(end)==len(text),'JSON trailing data');return spans
def replace_json_scalars(raw,changes):
 text=raw.decode('utf8');require(text.encode('utf8')==raw,'JSON encoding changed');spans=scalar_spans(text);edits=[]
 for path,(old,new) in changes.items():
  a,b,value=spans[path];require(type(value) is type(old) and value==old,'unexpected old JSON scalar '+repr(path));edits.append((a,b,json.dumps(new,ensure_ascii=False,allow_nan=False)))
 for a,b,new in sorted(edits,reverse=True):text=text[:a]+new+text[b:]
 result=text.encode('utf8');json.loads(result);return result
def contract_overlay(raw):
 require(SHA(raw)==OLD_CONTRACT_SHA,'exact R5 asset contract required')
 c=json.loads(raw);changes={}
 for name in GAS:
  require(c['joints'][name]['type']=='slide' and c['joints'][name]['limits_si']==[-.0267046843609,.0352033350025],'old gas type/range differs')
  require(c['gas_springs'][name]['stiffness_n_m']==3500. and c['gas_springs'][name]['damping_n_s_m']==3.,'old gas nominal differs')
  changes[('gas_springs',name,'stiffness_n_m')]=(3500.,2000.)
  changes[('joints',name,'limits_si',1)]=(.0352033350025,QHI)
 result=replace_json_scalars(raw,changes)
 return result,changes
def patch_python(name,raw):
 require(name in SPECS and SHA(raw)==OLD_PY_SHA[name],'unapproved Python source/version')
 for old,new,count in SPECS[name]:
  require(raw.count(old)==count,'exact Python token count differs: '+name);raw=raw.replace(old,new)
 ast.parse(raw);return raw
def usda_override(base_relative='source_700N/robot.usd'):
 p=PurePosixPath(base_relative)
 require(not p.is_absolute() and '..' not in p.parts and re.fullmatch(r'[A-Za-z0-9_./-]+',base_relative) and p.suffix=='.usd','new layer needs exact safe relative old asset dependency')
 # Raw attribute names and X slide convention are in the pinned old exporter
 # and audit_import source. No USD is parsed or authored through SDK here.
 lines=['#usda 1.0','(','    defaultPrim = "Robot"','    subLayers = [@'+base_relative+'@] ',')','over "Robot"','{','    over "joints"','    {']
 for name in GAS:
  lines += ['        over "'+name+'"','        {','            float drive:linear:physics:stiffness = 2000','            float physics:upperLimit = '+repr(QHI),'        }']
 lines += ['    }','}','']
 return '\n'.join(lines).encode('utf8')
def prepare(B,dest):
 """Generate source overlay only. Dest must be NEW and outside the source tree."""
 B=Path(B).resolve();dest=Path(dest).resolve();require(not dest.exists() and not dest.is_relative_to(B),'new isolated destination required');dest.mkdir(parents=True)
 output={};before={}
 def read(relative):
  require(relative in REPLACEMENTS,'not a reviewed text source');raw=source_path(B,relative).read_bytes();before[relative]=SHA(raw);return raw
 try:
  for name in SPECS:output[RT+name]=patch_python(name,read(RT+name))
  for relative in ('job0/assets/import_contract.json',RT+'import_contract.json'):output[relative],_=contract_overlay(read(relative))
  relative='job0/runtime/reports/SOURCE_FREEZE.json';raw=read(relative);freeze=json.loads(raw);changes={}
  for name in [*SPECS,'import_contract.json']:
   key='isaac/mod4/'+name;expected=before[RT+name]
   require(freeze['sha256'][key]==expected,'old SOURCE_FREEZE current selected entry mismatch')
   changes[('sha256',key)]=(expected,SHA(output[RT+name]))
  output[relative]=replace_json_scalars(raw,changes)
  require(set(output)==REPLACEMENTS,'exact source replacement set')
  rows=[]
  for relative,raw in output.items():
   path=source_path(dest,relative);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);rows.append(dict(relative=relative,old_SHA=before[relative],new_SHA=SHA(raw),bytes=len(raw)))
  layer=dest/'job0/assets/NOMINAL400_GAS_ONLY_OVERLAY_NOT_ADMITTED.usda';layer.write_bytes(usda_override())
  result=dict(prepared=True,source_only=True,replacements=rows,asset_override_text=dict(relative=layer.relative_to(dest).as_posix(),bytes=layer.stat().st_size,SHA=SHA(layer.read_bytes()),old_binary_read_or_copied=False,actual_USD_composition_verified=False),
   physical_migration=True,same_physics_continuation=False,old_geometry_binary_must_remain_byteexact=True,original_clock_solver_reward_command_success_save_unchanged=True,actual_SDK_or_GPU_admitted=False,models_read=False)
  (dest/'CANDIDATE_SOURCE_CHANGESET_NOT_ADMITTED.json').write_text(json.dumps(result,indent=2),'utf8');return result
 except BaseException:
  # Retain partial candidates and caller's original error; never mutate source.
  raise
