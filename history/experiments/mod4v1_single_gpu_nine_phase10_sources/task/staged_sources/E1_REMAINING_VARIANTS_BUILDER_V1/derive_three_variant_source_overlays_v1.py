"""Explicitvariant SOURCE_ONLY implementation from each exactexecuted package.
Reuse only SAMEoriginalSHA common50Hz mechanism; factory/axis/reward untouched.
No model/binary/stat/hash/decode/SDK/SSH/GPU execution.
"""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent.parent;RT='runtime/isaac/mod4/'

def H(b):return hashlib.sha256(b).hexdigest()
def once(s,a,z):
 if s.count(a)!=1:raise ValueError('exactsource anchorcount '+str(s.count(a))+':'+a)
 return s.replace(a,z,1)
def addimport(s):
 a=ast.parse(s);last=0
 if a.body and isinstance(a.body[0],ast.Expr) and isinstance(a.body[0].value,ast.Constant) and isinstance(a.body[0].value.value,str):last=a.body[0].end_lineno
 for n in a.body:
  if isinstance(n,ast.ImportFrom) and n.module=='__future__':last=n.end_lineno
 lines=s.splitlines(keepends=True);lines.insert(last,'from e1_pinned_source_v1 import cached_H,cached_source_owns,runner_source_load_scope\n');return ''.join(lines)
def main():
 common=['e1_four_leaf_migration_v1.py','e1_pinned_source_v1.py','mod4v1_fresh_dr_guard.py','gas400_reset_bank_exact_compatibility_v1.py','mod4v1_e1_reset_bank_compat.py','mod4v1_e1_collision_bank_compat.py','H1_TYPED400_ORIGINAL_IMPORT_CONTRACT_EXACT.json','RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json']
 for name in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
  root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V1');join=json.loads((root/'EXACT_EXECUTED_SOURCE_PACKAGE_JOIN_V1.json').read_bytes());assert not join['missing_text'];canonical=T/'staged_sources'/('E1_'+join['baseline_canonical']+'_40050_MOD4V1_SOURCE_V1');ci=json.loads((canonical/'EXACT_ORIGINAL_MOTHER_INPUTS.json').read_bytes());cinputs={r['relative']:r for r in ci['inputs']};inputs={r['relative']:r for r in join['inputs']};changes=[];same=[];old={}
  def put(rel,raw,reason):
   p=root/rel
   if p.is_file():old[rel]=p.read_bytes()
   if isinstance(raw,str):raw=raw.encode()
   if rel.endswith('.py'):compile(ast.parse(raw),rel,'exec')
   p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);changes.append(dict(relative=rel,old_SHA=H(old[rel]) if rel in old else None,new_SHA=H(raw),reason=reason))
  # Never reuse canonicaltask unless exactoriginalfilebytes SHA proves same source.
  for rel,r in inputs.items():
   if rel in cinputs and r['SHA']==cinputs[rel]['SHA']:
    raw=(canonical/rel).read_bytes();same.append(dict(relative=rel,original_SHA=r['SHA'],canonical_original_SHA=cinputs[rel]['SHA']))
    if H(raw)!=r['SHA']:put(rel,raw,'SAMEoriginalSHA common50Hz/cache/nominal/bank adapter, not task substitution')
  for file in common:put(RT+file,(canonical/(RT+file)).read_bytes(),'Commonpurecache/nominal/bankidentity mechanism; no canonicalactor/factory substitution')
  put(RT+'variant_extra_state_runtime_v1.py',(B/'variant_extra_state_runtime_v1.template.py').read_bytes(),'OWNextra state loader/saver; retain allunknownaxisfields, no RNG/physics')
  # Explicitmetadata; currentweights not read. Unknown savediteration/LR remain unknown.
  manifest=json.loads((root/'original_run_manifest.json').read_bytes());meta=dict(kind='EXPLICIT_FROZEN_E1_VARIANT_SOURCE_ONLY_METADATA',variant=name,canonical=name,role=join['role'],original_source_SHA=join['original_source_SHA'],entry=join['entry'],original_helper=join['original_helper'],restore_helper='e1_variant_fullstate_checkpoint',original_env=manifest['env'],source_path='PARENT_FUTURE_EXACT_SOURCE_PATH_REQUIRED',source_bytes={'CURB_PROTECTED878':17617374,'CURB_INDEPENDENT113':18039234,'SLOPE_INDEPENDENT50':17958075}[name],saved_iteration='UNKNOWN_NOT_PROVEN_FROM_SAVED_METADATA',saved_LR=.00011390625149942935 if name=='CURB_PROTECTED878' else 'UNKNOWN_NOT_PROVEN_FROM_SAVED_METADATA',saved_17Adam={'CURB_PROTECTED878':660400,'CURB_INDEPENDENT113':645100,'SLOPE_INDEPENDENT50':643980}[name],scope='Protected878 ONEactor/three historicalrankfullstates, original20mmCURB notlatest' if name=='CURB_PROTECTED878' else ('IndependentCURB113 G3sibling NOT878descendant; storedreset_direction axis' if name=='CURB_INDEPENDENT113' else 'IndependentSlope50 from24b; fullramp+bothsupports explicitaxis not24b substitute'),extra_root_keys=['distributed_rank_contract'] if name=='CURB_PROTECTED878' else ['independent_expert_scope_state','independent_expert_task_contract'],unknown_root_or_extra_fields='Retained bypurefourleaf andfuturecache; fullsavednonTensorrootkeyinventory notobserved, no emptyextra assumption',future_actual_counters='From sameonce-loaded COMPLETE originaldict; no arithmetic/default LR/iteration guess',GPU_or_PT_operation_permission=False)
  with (root/'VARIANT_SOURCE_METADATA.json').open('x',encoding='utf-8') as f:json.dump(meta,f,indent=2)
  with (root/'E1_CANONICAL_SOURCE_METADATA.json').open('x',encoding='utf-8') as f:json.dump(dict(meta,scope=meta['scope']),f,indent=2)
  # Supplemental state wrapper delegates original helper unchanged -> ONEoriginalreset.
  wrapper='''"""Explicit frozenvariant fullstate wrapper; original lowerhelper ONEreset retained."""
from pathlib import Path
import copy,importlib,json
from e1_pinned_source_v1 import cached_load,cached_H,cached_source_owns
from variant_extra_state_runtime_v1 import restore_extra_before_original_reset,finish_extra_after_original_reset,merge_extra_into_own_save

def metadata():return json.loads((Path(__file__).resolve().parents[3]/'VARIANT_SOURCE_METADATA.json').read_bytes())
def resume_e1_new_episode(runner,env,path,log_dir):
 import torch
 from spring_pressure_checkpoint import exact
 meta=metadata();ck=cached_load(path,map_location='cpu',weights_only=False,purpose='variant.OWN_complete_extra_state_BEFORE_original_one_reset')
 before=restore_extra_before_original_reset(env,ck,variant=meta['variant'],torch_module=torch)
 original=importlib.import_module(meta['original_helper']);row=original.resume_e1_new_episode(runner,env,path,log_dir)
 after=finish_extra_after_original_reset(env,ck,variant=meta['variant'],torch_module=torch,exact=exact)
 report=dict(source_SHA=cached_H(path,purpose='variant.OWN_extra_identity'),variant=meta['variant'],before_original_reset=before,after_original_reset=after,all_complete_saved_extras_exact=True,original_lower_helper=meta['original_helper'],extra_reset_physics_RNG_calls=0,unknown_root_fields_retained_in_future_cache=True,not_actual_skill_or_birthinertia_gate=True)
 Path(log_dir,'VARIANT_EXTRA_FULLSTATE_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(report,indent=2));return row

def install_e1_save_contract(runner,env):
 import torch
 meta=metadata();original=importlib.import_module(meta['original_helper']);original.install_e1_save_contract(runner,env);old=runner.save
 def save(path,*args,**kwargs):
  if cached_source_owns(path):raise ValueError('Frozen selectedsource cannot be outputpath')
  old(path,*args,**kwargs);complete=cached_load(path,map_location='cpu',weights_only=False,purpose='variant.OWN_new_save_real_disk_roundtrip');merged=merge_extra_into_own_save(complete,env,variant=meta['variant']);torch.save(merged,path)
 runner.save=save
'''
  put(RT+'e1_variant_fullstate_checkpoint.py',wrapper,'OriginalE1fullhelper + sourceextra BEFORE + literalextra auditAFTER oneoriginalreset; OWNsave retained')
  # Exactexecuted own entry. Only clockdiscount+cache+extrahelper route; factory untouched.
  rel=RT+join['entry'];orig=(root/'original_exact'/rel).read_bytes();s=orig.decode('utf-8-sig');s=once(s,'gamma=0.99','gamma=0.9801');s=once(s,'lam=0.95','lam=0.9025');s=once(s,'        runner.load(warm)','        with runner_source_load_scope():\n            runner.load(warm)')
  s=once(s,'    def _sha256(path):\n        import hashlib','    def _sha256(path):\n        if cached_source_owns(path):return cached_H(path,purpose="variant.original_manifest_source_identity")\n        import hashlib')
  module=join['original_helper'];s=s.replace('from '+module+' import resume_e1_new_episode','from e1_variant_fullstate_checkpoint import resume_e1_new_episode').replace('from '+module+' import install_e1_save_contract','from e1_variant_fullstate_checkpoint import install_e1_save_contract');s=addimport(s)
  # Main may import combinedmethod; assert newwrapper isactually selected.
  assert 'from e1_variant_fullstate_checkpoint import resume_e1_new_episode' in s and 'from e1_variant_fullstate_checkpoint import install_e1_save_contract' in s
  oldfunc=next(n for n in ast.parse(orig).body if isinstance(n,ast.FunctionDef) and n.name=='build_env');newfunc=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name=='build_env');assert ast.dump(oldfunc,include_attributes=False)==ast.dump(newfunc,include_attributes=False)
  put(rel,s,'Own executedentry factory ASTidentical; only50Hzdiscount/cache andexplicitvarianthelper chain')
  # Preparedgeneric native24 interface calls metadataentry andOWNvarianthelper; notdispatch.
  worker=(canonical/'prepared_e1_native24_noupdate_worker_v1.py').read_text(encoding='utf-8');worker=worker.replace("str(root/'lib')","str(root/'producer/lib')")
  put('prepared_variant_native24_noupdate_worker_v1.py',worker,'FUTURE interface only; originalOWNfactory+VARIANTwrapper via metadata, no execution')
  with (root/'SAME_SHA_COMMON_OVERLAY_DERIVATION_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='SOURCE_ONLY_VARIANT_OVERLAY_NOT_ACTUAL_PT_OR_SDK',variant=name,same_original_SHA_to_canonical=same,changes=changes,own_build_env_AST_original=True,unknownextras_not_dropped=True,physical_gates_added=False,PT_SSH_SDK_GPU_operations=0),f,indent=2)
  print(json.dumps(dict(variant=name,same_original_SHA_files=len(same),derived_changes=len(changes),own_factory_AST_exact=True,extrahelper_implemented=True,PT_SDK_operations=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('DERIVE_VARIANT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_operations=0),f,indent=2)
  raise
