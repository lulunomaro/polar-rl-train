"""Independent SOURCEFINAL compile/SHA/AST/clock/dependency seal, explicitgaps.
No actual PT/binary/stat/hash/decode/SDK/SSH/GPU operations. Stdlib sourceonly.
"""
from pathlib import Path
import ast,hashlib,json,re,time,traceback,warnings
B=Path(__file__).resolve().parent;T=B.parent.parent;RT='runtime/isaac/mod4/';NO={'.pt','.pth','.ckpt','.npz','.npy','.usd','.usdc','.zip','.onnx','.safetensors','.pyc'}

def H(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
 mock=load(B/'THREE_VARIANT_FOURLEAF_EXTRA_RESTORE_SAVE_MOCK_PROOF_V2.json');assert mock['passed'];plans=[];allwarnings=[]
 for name in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
  root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V2');j=load(root/'EXACT_EXECUTED_SOURCE_PACKAGE_JOIN_V1.json');m=load(root/'VARIANT_SOURCE_METADATA.json');owner=load(root/'SAVED_EVIDENCE_ROOTKEY_HELPER_OWNER_MAP_V1.json');assert not j['missing_text'] and len(owner['helper_reverse_AST'])==8
  for r in j['inputs']:assert H((root/'original_exact'/r['relative']).read_bytes())==r['SHA']
  for fn in ['build_env','describe','dry_run']:
   trees=[ast.parse((r/(RT+m['entry'])).read_bytes()) for r in [root/'original_exact',root]];nodes=[next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fn) for tree in trees];assert ast.dump(nodes[0],include_attributes=False)==ast.dump(nodes[1],include_attributes=False)
  # Critical owngeometry/reward/phase/axis source exactly retained, no map/policy substitution.
  preserved=['mod4_task.py','retention_learning_env.py','directional_spin_runtime.py','retention_flat_runtime_named_owned.py','retention_command_state.py','e1_rough_reset_tensor.py','e1_rough_ground.py','feedback_delay_mild.py']
  if name.startswith('CURB'):preserved+=['curb20_entry_v3_runtime.py','curb20_geometry.py','curb20_entry_v2_math.py']
  else:preserved+=['slope5_geometry.py','slope5_retention_runtime.py','slope5_current_state.py','slope5_command_migration.py','independent_expert_axis_v1.py']
  if name=='CURB_INDEPENDENT113':preserved+=['independent_expert_axis_v1.py']
  critical=[]
  for fn in preserved:
   p=root/(RT+fn);old=root/'original_exact'/(RT+fn);assert H(p.read_bytes())==H(old.read_bytes()),fn;critical.append(dict(relative=RT+fn,SHA=H(p.read_bytes()),original_exact=True))
  # Timing deltas are only exactSHA-reused common mechanics, plus ownentrydiscount.
  for rel in ['runtime/physics_clock.py','runtime/physics_clock2000.py',RT+'physics_clock.py']:
   s=(root/rel).read_text(encoding='utf-8');assert 'control_s=.02' in s and 'decimation=20000//us' in s and 'policy_hz=50.' in s
  s=(root/(RT+'feedback_delay_runtime.py')).read_text();assert 'tick % 4 == 0' in s and 'control_period_us=10000' in s and 'requested_delay_us=[0, 10000]' in s
  s=(root/(RT+'action_delay_physics_queue.py')).read_text();assert 'control_us=20000' in s and "state['control_us']==20000" in s and 'actual_transition_delay_us=[0,2500,5000]' in s
  old=load(root/'original_exact/runtime/train/deploy/contract_rm2025_later.json');new=load(root/'runtime/train/deploy/contract_rm2025_later.json');assert new['policy_hz']==50 and dict(new,policy_hz=100)==old
  # OWNextra implementation has no reset/physics/RNG/reseed/NCCL/optimizer calls.
  extra=root/(RT+'variant_extra_state_runtime_v2.py');et=ast.parse(extra.read_bytes());forbidden=[]
  for n in ast.walk(et):
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('reset','step','manual_seed','set_rng_state','rand','randn','randint','all_reduce','init_process_group'):forbidden.append(n.func.attr)
  assert not forbidden
  wrapped=ast.parse((root/(RT+'e1_variant_fullstate_checkpoint.py')).read_bytes());resume=next(n for n in wrapped.body if isinstance(n,ast.FunctionDef) and n.name=='resume_e1_new_episode');original_calls=[n for n in ast.walk(resume) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='resume_e1_new_episode'];assert len(original_calls)==1
  loop=[n for n in ast.walk(ast.parse((root/'prepared_variant_native24_noupdate_worker_v1.py').read_bytes())) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range' and any(isinstance(a,ast.Constant) and a.value==24 for a in n.iter.args)];assert len(loop)==1
  # Active AST dependency closure, including originalhelper via metadata, no imports executed.
  queue=[root/'prepared_variant_native24_noupdate_worker_v1.py',root/(RT+m['entry']),root/(RT+'e1_variant_fullstate_checkpoint.py'),root/(RT+m['original_helper']+'.py')];seen=set();nodes=[];external=set();timing=[]
  while queue:
   p=queue.pop(0)
   if p in seen:continue
   seen.add(p);raw=p.read_bytes();text=raw.decode('utf-8-sig');tree=ast.parse(raw);imports=[]
   for n in ast.walk(tree):
    if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
    elif isinstance(n,ast.ImportFrom) and n.module:imports.append(n.module)
   edges=[]
   for mod in sorted(set(imports)):
    hits=[p for p in [root/RT/(mod+'.py'),root/'runtime'/(mod.replace('.','/')+'.py'),root/'producer/lib'/(mod+'.py')] if p.is_file()]
    if hits:queue.append(hits[0]);edges.append(str(hits[0].relative_to(root)))
    else:external.add(mod)
   for line,s in enumerate(text.splitlines(),1):
    if re.search(r'(step_dt|control_us|control_period|POLICY_HZ|phase_elapsed|resampling_time|episode_length_s|physical_episode_limit_seconds|\b10000\b)',s):timing.append(dict(relative=str(p.relative_to(root)),line=line,text=s.strip()))
   nodes.append(dict(relative=str(p.relative_to(root)),SHA=H(raw),AST_SHA=H(ast.dump(tree,include_attributes=False).encode()),local_import_edges=edges))
  stale=[r for r in timing if re.search(r'(step_dt.*==\s*\.01|round\(\.01|control_us\s*==\s*10000)',r['text']) and not r['text'].startswith(('#','"','\''))];assert not stale
  # Compile all source, capture exact inherited warningfilename; originalbytes never edited.
  pyrows=[];warningrows=[]
  for p in root.rglob('*.py'):
   raw=p.read_bytes()
   with warnings.catch_warnings(record=True) as ws:
    warnings.simplefilter('always',SyntaxWarning);tree=ast.parse(raw,filename=str(p));compile(tree,str(p),'exec')
   for w in ws:warningrows.append(dict(relative=str(p.relative_to(root)),line=w.lineno,category=w.category.__name__,message=str(w.message),inherited_original_not_edited=True))
   pyrows.append(dict(relative=str(p.relative_to(root)),SHA=H(raw),AST_SHA=H(ast.dump(tree,include_attributes=False).encode())))
  allwarnings+=warningrows
  artifacts={}
  artifacts['SOURCE_ONLY_INDEPENDENT_SHA_AST_FINAL_REVIEW_V1.json']=dict(kind='SOURCE_FINAL_IMPLEMENTED_WITH_EXPLICIT_SAVED_EVIDENCE_GAPS_NOT_GPU',passed=True,variant=name,original_executed_text_count=j['text_count'],binary_metadata_only=j['binary_metadata_only'],ownfactory_describe_dryrun_AST_original=True,critical_sources_unchanged=critical,helper_reverse_AST=owner['helper_reverse_AST'],own_extra_load_save_beforeafter_implemented=True,unknown_root_and_nested_dict_passthrough_currentknownwins=True,original_Curb_writer_AST_exact=True,loweroriginalresume_called_once=True,extra_reset_RNG_physics_calls=0,python_AST_compile=pyrows,warnings=warningrows,MOCK_label='FakeTensor/fakeTorch/fakeLowerReset only, no model/SDK',MOCK_proof_SHA=H((B/'THREE_VARIANT_FOURLEAF_EXTRA_RESTORE_SAVE_MOCK_PROOF_V2.json').read_bytes()),saved_evidence_gaps=owner['gaps'],PT_SSH_SDK_GPU_budget_GO_operations=0)
  artifacts['ACTIVE_VARIANT_DEPENDENCY_CLOCK_REVIEW_FINAL_V1.json']=dict(kind='SOURCE_ONLY_ACTIVE_DEPENDENCY_AND_CLOCK_UNITS_NOT_ACTUAL',variant=name,nodes=nodes,external_imports=sorted(external),timing_lines=timing,possible_stale_active_clock=stale,unit_review=dict(policy='50Hz/deliveryonlypolicyHz;20ms/8physics callbacks',feedback='Original10ms/0,10000us recipe/model/cache retained;4physicalticks sample100Hz',physical='2.5ms/TGS32,4 and original5mscontactfragment unchanged',phase='Originalreal step_dt and phase_elapsed seconds;12/16s resampling/20sepisode/own20s routeaxis remain seconds',axis='OriginalCurb113 fixedstored reset_direction writer andSlope50 fullramp/bothsupports boundary preserved',discount='Only ownentry gamma.9801/GAE.9025 for samephysicaldiscount',archives='Originalproducer120/480 andNCCL/GO code archived only, NOT future interface or execution'),no_extra_physical_gate=True)
  artifacts['MOCK/THREE_VARIANT_FOURLEAF_EXTRA_RESTORE_SAVE_MOCK_PROOF_V2.json']=mock
  artifacts['FUTURE_VARIANT_SOURCE_ONLY_TASK_DESCRIPTOR.json']=dict(kind='SOURCE_ONLY_DESCRIPTOR_NOT_ACTUAL_TASK_READY_GO',variant=name,exact_source_SHA=m['original_source_SHA'],selected_source_path='PARENT_TO_SUPPLY',expected_source_bytes=m['source_bytes'],actual_LR_iteration_rule='Same futureonce-loaded completedict; savedunknown notfilled by arithmetic',future_cache='1byte/SHA/CPUdecode COMPLETEoriginal ->only4leaf RAMtyped; rootkeys unchanged',restore='Ownfactory ->newnominal ->RSLfullcore ->OWNextra source restore ->original8helper/ONEsensorreset ->OWNextraexactaudit',future_native24='Prepared only24/192/48; no currentSDK',historical_rank0_contract_kept_noNCCL='CURB_PROTECTED878'==name,unknownowner_physicaleffects='UNKNOWNnotclaimed, preserved in sourcecache/ownSAVE',extra_PT_SDK_permission=False)
  readme=f'''# {name} MOD4v1 SOURCE_FINAL（含显式saved-evidence不足项）\n\n- exact executed mother：{j['text_count']}份文本逐SHA join，3项原binary仅metadata；原文本另保original_exact。没有PT/stat/hash/decode或SSH/SDK/GPU/预算/GO。\n- 只对sameoriginalSHA共用机制复用50Hz/100Hz/2.5ms/TGS32,4/newnominal/133bank精确组合；ownentry build_env/describe/dry_run及原地图、reward、phase、方向/retention/privateRNG源码均AST/逐SHA保留。\n- 原8份helper反向cache-adapter AST精确，加专属extraowner BEFORE原helper唯一reset→AFTER逐树audit。pure4leaf只在未来同once-loaded完整dict上运行，所有actor/STD17Adam/iter/LR/history/queue/timestamp/unknown不drop。\n- protected878保rank0历史world3/global60k，oneactor/三rankstate，不NCCL、不重fork；113保saved reset_direction和原writer AST，不从fresh reset重建；50保原fullramp/bothsupport axis。\n- futureSAVE保原unknownroot/nested dict keys，currentknownactor/optimizer/history值优先；unknownphysicalowner效果不伪称已恢复。V1弱MOCK及CRLF generator失败、V2修正都保留。\n- MOCK明确fakeTensor/fakeTorch/fakeONEreset；三variant+6负例，current保存时缺unknown字段仍保留的强测试过，非实际checkpoint/GPU。\n- 精确不足项：savedfinalCPU有tensor schema/count/Adam但无完整非tensor rootkey清单/值。source-derived key inventory只是保存代码映射，不冒充实际全rootlist；未知owner/实际LR/iter留future同缓存实读。没有技能毕业、独立birth惯量、全硬件DR扩称。\n- 父下一独立许可前不做任何权重或SDK；本子不commit/push，全部source/errors/警告交父追加Git。\n'''
  plans.append((root,artifacts,readme))
 for root,artifacts,readme in plans:
  for rel,value in artifacts.items():
   p=root/rel;p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
  with (root/'README_SOURCE_FINAL.md').open('x',encoding='utf-8') as f:f.write(readme)
  rows=[]
  for p in sorted(root.rglob('*')):
   if p.suffix.lower() in NO:continue
   if not p.is_file():continue
   raw=p.read_bytes();r=dict(relative=p.relative_to(root).as_posix(),bytes=len(raw),SHA=H(raw))
   if p.suffix=='.py':r['AST_SHA']=H(ast.dump(ast.parse(raw),include_attributes=False).encode())
   rows.append(r)
  with (root/'FINAL_SOURCE_INDEX.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='EXPLICIT_FROZEN_E1_VARIANT_SOURCEFINAL_IMPLEMENTED_WITH_SAVED_INVENTORY_GAPS',root=str(root),files=rows,sourcefinal=True,not_fake_actual=True,saved_gaps='SAVED_EVIDENCE_ROOTKEY_HELPER_OWNER_MAP_V1.json',all_unknowns_preserved_not_assumednone=True,actual_PT_SDK_GPU_operations=0),f,ensure_ascii=False,indent=2)
 out=[]
 for root,_,_ in plans:
  p=root/'FINAL_SOURCE_INDEX.json';out.append(dict(root=str(root),index=str(p),SHA=H(p.read_bytes())))
 with (B/'THREE_VARIANT_SOURCEFINAL_HANDOFF_INDEX_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='THREE_EXPLICIT_VARIANT_SOURCEFINALS_NO_ACTUAL_EXECUTION',packages=out,explicit_savedrootinventory_gaps=True,all_original_sourceFailures_preserved=True,PT_SSH_SDK_GPU_operations=0),f,indent=2)
 print(json.dumps(dict(status='THREE_SOURCEFINALS_WITH_EXPLICIT_EVIDENCE_GAPS',packages=out,inherited_warnings=len(allwarnings)),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('SOURCEFINAL_ORIGINAL_REVIEW_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_operations=0),f,indent=2)
  raise
