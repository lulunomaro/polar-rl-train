"""Independent AST/SHA-only review; never import/execute target modules or binaries."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;O=B.parent/'H1_NORMAL_MOD4V1_SOURCE_V1';RT='job0/runtime/isaac/mod4/'

def raw(p):
 p=Path(p);assert p.suffix.lower() in ('.py','.json','.md','.patch','.log');return p.read_bytes()
def H(r):return hashlib.sha256(r).hexdigest()
def ld(n):return json.loads(raw(O/n).decode('utf-8-sig'))
def ast_hash(node):return H(ast.dump(node,include_attributes=False).encode())
def write(n,v):
 with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)

def main():
 idx=ld('FINAL_SOURCE_INDEX.json');manifest=ld('MOTHER453_INPUT_MANIFEST.json');by={r['relative']:r for r in manifest['files']}
 for row in idx['outputs']:
  data=raw(O/row['relative']);assert len(data)==row['bytes'] and H(data)==row['SHA'],row['relative']
  if row['relative'].endswith('.py'):assert ast_hash(ast.parse(data))==row['AST_SHA'];compile(data,row['relative'],'exec')
 class ReverseCache(ast.NodeTransformer):
  def __init__(self,sensor=False):self.sensor=sensor
  def visit_ImportFrom(self,node):
   return None if node.module=='h1_pinned_source_v1' else node
  def visit_Call(self,node):
   node=self.generic_visit(node)
   if isinstance(node.func,ast.Name) and node.func.id=='cached_load':
    node.func=ast.Attribute(value=ast.Name(id='torch',ctx=ast.Load()),attr='load',ctx=ast.Load());node.keywords=[k for k in node.keywords if k.arg!='purpose']
   elif isinstance(node.func,ast.Name) and node.func.id=='cached_H':
    expr='hashlib.sha256(p.read_bytes()).hexdigest()' if self.sensor else 'hashlib.sha256(Path(path).read_bytes()).hexdigest()'
    return ast.parse(expr,mode='eval').body
   return node
 helpers=['sensor_resume_contract.py','feedback_delay_checkpoint.py','action_delay_checkpoint.py','spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py','sensor_a0_runtime.py','h1_fullstate_checkpoint_v1.py']
 results=[]
 for rel in [RT+x for x in helpers]+['h1_step270_fullstate_checkpoint_candidate_uninstalled.py']:
  old=raw(by[rel]['local_path']);assert H(old)==by[rel]['SHA'];original=ast.parse(old)
  derived=ast.parse(raw(O/rel));rev=ReverseCache(sensor=rel.endswith('/sensor_resume_contract.py')).visit(derived);ast.fix_missing_locations(rev)
  assert ast.dump(rev,include_attributes=False)==ast.dump(original,include_attributes=False),rel
  results.append(dict(relative=rel,reverse_cache_only_AST_matches_original=True,original_AST_SHA=ast_hash(original)))
 driverbase=ast.parse(raw(by['target_normal_H1_CUDA_fullrestore_frozen_native24_once_v1.py']['local_path']))
 driver=ast.parse(raw(O/'worker_mod4v1_normal_h1.py'))
 def native24_loop(tree):
  found=[n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range' and len(n.iter.args)==1 and isinstance(n.iter.args[0],ast.Constant) and n.iter.args[0].value==24]
  assert len(found)==1;return found[0]
 assert ast_hash(native24_loop(driverbase))==ast_hash(native24_loop(driver))
 cfgbase=ast.parse(raw(by[RT+'train_H1_ground_prelaunch_fullstate_v2.py']['local_path']));cfgnew=ast.parse(raw(O/(RT+'train_H1_ground_prelaunch_fullstate_v2.py')))
 for name in ('build_env','runner_config','describe','dry_run'):
  a=next(n for n in cfgbase.body if isinstance(n,ast.FunctionDef) and n.name==name);z=next(n for n in cfgnew.body if isinstance(n,ast.FunctionDef) and n.name==name);assert ast_hash(a)==ast_hash(z),name
 guardbase=next(x for x in idx['input_texts'] if x['path'].endswith('E3_MOD4V1_SOURCE_FINAL\\runtime\\isaac\\mod4\\mod4v1_fresh_dr_guard.py'))
 assert H(raw(O/(RT+'mod4v1_fresh_dr_guard.py')))==guardbase['SHA']
 c=ld('MOD4V1_H1_THREE_BODY_ASSET_DIFF.json');assert len(c['body_changes'])==3 and c['unchanged_other_body_count']==28 and c['same_gas_spring_recipe']
 cacheast=ast.parse(raw(O/(RT+'h1_pinned_source_v1.py')))
 cacheclasses=[n for n in cacheast.body if isinstance(n,ast.ClassDef) and n.name=='PinnedSourceH1'];assert len(cacheclasses)==1
 init=next(n for n in cacheclasses[0].body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
 one_read=sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='stream' and n.func.attr=='read' for n in ast.walk(init));assert one_read==1
 one_decode=sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='original_load' for n in ast.walk(init));assert one_decode==1
 one_hash=sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='hashlib' and n.func.attr=='sha256' for n in ast.walk(init));assert one_hash==1
 assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='stat' for n in ast.walk(cacheast))
 review=dict(kind='INDEPENDENT_H1_SOURCE_REVERSE_AST_REVIEW_NOT_SDK',passed_static=True,source_index_SHA=H(raw(O/'FINAL_SOURCE_INDEX.json')),all_index_outputs_SHA_and_AST_match=True,helper_reverse_AST=results,original_native24_loop_AST_exact=True,native24_loop_AST_SHA=ast_hash(native24_loop(driver)),original_config_reward_buildenv_AST_unchanged=True,new_nominal_guard_exact_mechanism_reuse=True,actual3body_deltas_and_same400N_recipe=True,future_cache_AST_counts=dict(physical_byte_reads=one_read,source_SHA_calculations=one_hash,CPU_decodes=one_decode,explicit_PT_stat_calls=0),future_cache_constructor_NOT_EXECUTED=True,all_model_SDK_GPU_SSH_budget_operations=0,no_Ready_or_GO_or_Task_instance_generated=True,not_new_asset_runtime_or_skill_admission=True)
 write('INDEPENDENT_STATIC_REVIEW_v1.json',review)
 files=[]
 for root in (O,B):
  for p in sorted(root.rglob('*')):
   if not p.is_file():continue
   assert p.suffix.lower() in ('.py','.json','.md','.patch','.log'),str(p)
   if p.name=='FINAL_SOURCE_HANDOFF_v1.json':continue
   data=raw(p);files.append(dict(path=str(p),bytes=len(data),SHA=H(data)))
 parentloc=ld('SOURCE_LOCATION_METADATA_FROM_PARENT.json')
 write('FINAL_SOURCE_HANDOFF_v1.json',dict(kind='H1_NORMAL_MOD4V1_SOURCE_FINAL_CHILD_HANDOFF',source_index=dict(path=str(O/'FINAL_SOURCE_INDEX.json'),SHA=H(raw(O/'FINAL_SOURCE_INDEX.json'))),actual_mother=ld('ACTUAL_MOTHER453_IDENTITY.json'),independent_static_review=dict(path=str(O/'INDEPENDENT_STATIC_REVIEW_v1.json'),SHA=H(raw(O/'INDEPENDENT_STATIC_REVIEW_v1.json'))),parent_source_location_metadata=parentloc['parent_report'],local_source_existence_only_from_parent=True,current72_old_declared_path_exists=False,new_remote_selected_source_path='UNKNOWN_PARENT_SPECIFIES_AFTER_SEPARATE_TRANSPORT_PERMISSION',output_and_builder_files=files,no_PT_or_GPU_SDK_SSH_budget=True,resource_GO_or_training_permission=False,archive_status='Pending parent append-only archive; all reader/generator failures included; no child Git commit/push'))
 print(json.dumps(dict(status='H1_SOURCE_FINAL_STATIC_REVIEW_PASSED',source_index_SHA=H(raw(O/'FINAL_SOURCE_INDEX.json')),handoff_SHA=H(raw(O/'FINAL_SOURCE_HANDOFF_v1.json')),reverse_helper_AST_count=len(results),native24_loop_AST_exact=True,files_including_builder_errors=len(files),PT_reads=0),indent=2))

if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('H1SRC_REVIEW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(traceback=traceback.format_exc(),PT_GPU_SDK_SSH_budget=0),f,ensure_ascii=False,indent=2)
  raise
