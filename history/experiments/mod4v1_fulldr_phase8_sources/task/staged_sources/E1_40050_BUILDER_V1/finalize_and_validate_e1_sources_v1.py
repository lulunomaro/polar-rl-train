"""Independent sourcefinal validation. Text/JSON/AST only, NO runtime imports/PT."""
from pathlib import Path
import ast,hashlib,json,math,time,traceback
B=Path(__file__).resolve().parent;T=B.parent.parent;RT='runtime/isaac/mod4/'

def H(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def asth(b):return H(ast.dump(ast.parse(b),include_attributes=False).encode())
def function(b,n):
 t=ast.parse(b);return next(x for x in t.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==n)
def main():
 plans=[];commonMocks=[B/'FOUR_LEAF_MIGRATION_MOCK_PROOF_v1.json',B/'CACHE_CLOCK_MOCK_PROOF_V1.json']
 for name in ['CURB141','SLOPE135']:
  root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V1');meta=load(root/'E1_CANONICAL_SOURCE_METADATA.json');mother=load(root/'EXACT_ORIGINAL_MOTHER_INPUTS.json');inputs={r['relative']:r for r in mother['inputs']};get=lambda rel:(root/rel).read_bytes();checks=[];art={}
  assert mother['original_count']==(424 if name=='CURB141' else 404) and mother['full_verified_text_count']==mother['original_count']-1 and not mother['missing_text']
  assert len(mother['binary_metadata_only'])==1 and mother['binary_metadata_only'][0]['original_source_SHA']=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
  entry=RT+meta['entry'];old=Path(inputs[entry]['original_input_path']).read_bytes();new=get(entry)
  for fn in ['build_env','describe','dry_run']:
   assert ast.dump(function(old,fn),include_attributes=False)==ast.dump(function(new,fn),include_attributes=False)
   checks.append(dict(relative=entry,function=fn,original_AST_identical=True,scope='Actual originalE1 ownfactory/observations/dryrun not H1/flat substitute'))
  critical=['retention_flat_runtime.py','retained_flat_command_math.py','retention_flat_runtime_named_owned.py','retention_command_state.py','directional_spin_runtime.py','e1_terrain_runtime.py','e1_rough_reset_tensor.py','e1_rough_ground.py','e1_reset_evidence_training_env.py','feedback_delay_mild.py','sensor_mild_math.py']
  critical += ['curb20_direction_runtime.py','curb20_direction_state.py','curb20_entry_v3_runtime.py','curb20_entry_v2_math.py','curb20_geometry.py','curb20_retention_runtime.py'] if name=='CURB141' else ['slope5_geometry.py','slope5_retention_runtime.py','slope5_current_state.py','slope5_command_migration.py']
  for fn in critical:
   rel=RT+fn;assert H(get(rel))==inputs[rel]['SHA'],rel;checks.append(dict(relative=rel,original_SHA_unchanged=True,SHA=H(get(rel)),scope='Original phase/geometry/reward/retention math/privateRNG or100Hzfeedbackmodel unchanged'))
  helper=load(root/'E1_FULLSTATE_REVERSE_CACHE_ADAPTER_AST_PROOF_V1.json');assert len(helper['checks'])==(9 if name=='CURB141' else 8) and all(r['reverse_adapter_AST_exact'] for r in helper['checks'])
  assert get(RT+'e1_four_leaf_migration_v1.py')==(B/'e1_four_leaf_migration_v1.template.py').read_bytes() and get(RT+'e1_pinned_source_v1.py')==(B/'e1_pinned_source_v1.template.py').read_bytes()
  # Exact fourleaf inverse proof and synthetic cache/clock results are explicitly MOCK.
  for m in commonMocks:assert load(m)['passed']
  puretree=ast.parse(get(RT+'e1_four_leaf_migration_v1.py'));assert not any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ('load','save','rand','randint','stat','read_bytes','write_bytes') for x in ast.walk(puretree))
  cachetree=ast.parse(get(RT+'e1_pinned_source_v1.py'));ct=next(x for x in cachetree.body if isinstance(x,ast.ClassDef) and x.name=='PinnedSourceE1');ctor=next(x for x in ct.body if isinstance(x,ast.FunctionDef) and x.name=='__init__');calls=[x for x in ast.walk(ctor) if isinstance(x,ast.Call)]
  count=lambda attr:sum(isinstance(x.func,ast.Attribute) and x.func.attr==attr for x in calls)
  assert count('read')==1 and count('sha256')==1 and count('original_load')==1 and count('stat')==0
  cachedStatic=dict(constructor_read_calls=1,constructor_SHA_calls=1,constructor_decode_calls=1,explicit_stat_calls=0,constructor_executed_now=False)
  for rel in ['runtime/physics_clock.py','runtime/physics_clock2000.py',RT+'physics_clock.py']:
   s=get(rel).decode();assert 'control_s=.02' in s and 'decimation=20000//us' in s and 'policy_hz=50.' in s
   before=Path(inputs[rel]['original_input_path']).read_bytes();assert ast.dump(function(before,'fragments'),include_attributes=False)==ast.dump(function(s,'fragments'),include_attributes=False)
  delivery=load(root/'runtime/train/deploy/contract_rm2025_later.json');old_delivery=load(inputs['runtime/train/deploy/contract_rm2025_later.json']['original_input_path']);assert delivery['policy_hz']==50;delivery_inverse=dict(delivery,policy_hz=100);assert delivery_inverse==old_delivery
  fb=get(RT+'feedback_delay_runtime.py').decode();assert 'tick % 4 == 0' in fb and 'self._feedback_100hz_tick = tick // 4' in fb and 'control_period_us=10000' in fb and 'requested_delay_us=[0, 10000]' in fb
  ad=get(RT+'action_delay_physics_queue.py').decode();assert 'control_us=20000' in ad and "state['control_us']==20000" in ad and 'control_period_us=20000' in ad and 'actual_transition_delay_us=[0,2500,5000]' in ad
  dependency=load(root/'ACTIVE_SOURCE_DEPENDENCY_CLOCK_REVIEW_V1.json');assert not dependency['possible_stale_active_clock_or_nominal']
  # Source-only JSON geometry proof; execute only original stdlib-only gashelper declarations.
  gas=get(RT+'gas400_reset_bank_exact_compatibility_v1.py');gn={'__name__':'stdlib_geometry_data_proof','__file__':str(root/(RT+'gas400_reset_bank_exact_compatibility_v1.py'))};exec(compile(gas,'exact_gas_scalar_source_proof','exec'),gn)
  old700=load(root/(RT+'RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json'));old400=load(root/(RT+'H1_TYPED400_ORIGINAL_IMPORT_CONTRACT_EXACT.json'));newcontract=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1\assets\import_contract.json');nb=newcontract.read_bytes();assert H(nb)=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755';newcontractj=json.loads(nb);bank=get(RT+'reset_bank.json');assert H(bank)=='48be349c9bae1ec089b8bfb46ccc79085576e14bf373f6cb514027c3c155e50f';poses=json.loads(bank);four=gn['validate_four_gas_scalars'](old700,old400);ranges=gn['pose_gas_ranges'](poses,newcontractj);assert ranges['all_poses']==133 and ranges['original_height_filter_selected_poses']==74
  assert old400['joints']==newcontractj['joints'] and old400['gas_springs']==newcontractj['gas_springs'];changed=[n for n in old400['bodies'] if old400['bodies'][n]!=newcontractj['bodies'][n]];assert set(changed)=={'chassis','left_shin','right_shin'}
  allowed={'mass_kg','com_m','diagonal_inertia_kg_m2','principal_axes_wxyz','enhancement_mass_basis'}
  for n in changed:assert all(old400['bodies'][n].get(k)==newcontractj['bodies'][n].get(k) for k in set(old400['bodies'][n])|set(newcontractj['bodies'][n]) if k not in allowed)
  bankproof=dict(kind='SOURCE_JSON_EXACT_700_517_BAE_GEOMETRY_COMPOSITION_NOT_ACTUAL_NPZ_OR_GPU',exact_original700_to400_four_gas_scalars=four,old400_to_new3body_nominal_changes=changed,all_neutral_geometry_jointframes_fixedSI_unchanged=True,flatbank_original133_height74=ranges,original_resetbank_SHA=H(bank),NPZ_saved_SHA_only='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83',NPZ_actual_stat_hash_read_decode_now=False,rough_selection_original_argminheight_not_flat74=True,actual_SDK_or_birthinertia_pass=False)
  variants=load(root/'EXPLICIT_FROZEN_VARIANTS_SCOPE_V2.json');vrows=variants['rows'];assert len(vrows)==6 and len({v['original_source_SHA'] for v in vrows})==6 and any(v['original_source_SHA'].startswith('df0c') and v['review_only_not_selected'] for v in vrows)
  assert {v['original_source_SHA'] for v in vrows}=={'df0c141d444a6a85b983e49eedad10e91e0b7b264f627bff972dbd7cb1f2c753','7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43','268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1','3d2b0b6d9260383031e0c198501224fdaedefef9c283b43ce588419319b5de88','24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411','aab6fb4b6bce2f0004d06fa9d78f964efafd470238e36d386113ff9fba955d0b'}
  interface=load(root/'PREPARED_NATIVE24_OUTPUT_INTERFACE_V1.json');assert interface['all_basenames_equal'] and not interface['actual_parent_dispatch_created'];assert len([n for n in ast.walk(ast.parse(get('prepared_e1_native24_noupdate_worker_v1.py'))) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range' and any(isinstance(a,ast.Constant) and a.value==24 for a in n.iter.args)])==1
  pyrows=[]
  for p in root.rglob('*.py'):
   raw=p.read_bytes();tree=ast.parse(raw);compile(tree,str(p),'exec');pyrows.append(dict(relative=p.relative_to(root).as_posix(),SHA=H(raw),AST_SHA=H(ast.dump(tree,include_attributes=False).encode())))
  clockreview=dict(kind='E1_CANONICAL_SOURCE_CLOCK_UNIT_REVIEW_NOT_GPU',canonical=name,active_module_count=len(dependency['nodes']),reviewed_active_timing_lines=dependency['timing_review_lines'],review=dict(policy='Only delivery_hz100->50; physics_clock20ms/8callbacks, 5mscontactfragments unchanged',feedback='Preserve10ms/0or10000us model+recipe/history; every4physical ticks sample independent100Hz',action='Only20ms decisionqueue clock; issue/due/history timestamps and physical0/2500/5000us delays notrescaled',phase='OriginalDirectionalSpinCommand _dt=env.step_dt; phase_elapsed+=_dt in real seconds, E1direction/retention/state math unchanged',episode='Originalcfg episode_length_s from RM_EPISODE_S and original12/16s command resampling retain seconds, not same100Hzcontrolcounts',reward='Original reward functions/coefficients/fixedSI unchanged; actualSDK rateintegration uses new.02 control_dt, futureactual pending',gamma_GAE='Source_config .99**2/.95**2 for samephysicaldiscount; no optimizerstate or LR changes',health='Actualcfg.decimation for expectedcallbacks; originallegacy2mmdiag separately retained, newclosure10mm onlyper-env; no newgate'),possible_stale_active_clock_or_nominal=[],actual_physical_or_UTC_counters_not_guessed=True)
  static=dict(kind='INDEPENDENT_SOURCE_SHA_AST_REVIEW_NOT_ACTUAL_MODEL_OR_SDK',passed=True,canonical=name,full_original_text_count=mother['full_verified_text_count'],original_source_rows=mother['original_count'],original_NPZ_metadata_only=True,python_files_compiled=len(pyrows),python_SHA_AST=pyrows,unchanged_factory_phase_reward_checks=checks,fullstate_helper_reverse_AST=helper,shared_cache_static=cachedStatic,MOCK_test_reports=[dict(path=str(p),SHA=H(p.read_bytes()),label='MOCK_NOT_PT_NOT_GPU') for p in commonMocks],all_original_explicit_variants_not_closed=True,PT_stat_reads_hashes_decodes_writes=0,Torch_SDK_task_or_training_runtime_imported_or_executed=False,pure_stdlib_source_helpers_executed_only_for_explicit_MOCK_and_JSON_geometry_proof=True,SSH_SDK_GPU_budget_ReadyGO_operations=0)
  dep=dict(kind='SOURCE_ONLY_INSTALL_AND_RESTORE_DEPENDENCY_GRAPH_NOT_TARGETREADY',canonical=name,original_full_source_rows=mother['original_count'],complete_text_original_mother_manifest='EXACT_ORIGINAL_MOTHER_INPUTS.json',binary_dependency=dict(relative='runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz',original_SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83',current_source_only_read_stat_hash=False,future_install_exact_original_required=True),newasset=dict(USD_SHA=meta['new_USD_SHA'],contract_SHA=meta['new_contract_SHA'],parent_future_asset_dir_required=True,all_USD_referenced_geometry_dependency_install_required=True,current_USD_binary_reads=False),future_source=dict(path='PARENT_TO_SUPPLY',original_SHA=meta['original_source_SHA'],bytes=meta['source_bytes'],savedLR=meta['original_saved_LR'],actual_counters_rule=meta['actual_future_counters'],load='Onephysicalread/hash/CPUdecode futureworkercache; fourleafpuremigration inRAM; no PTwrite'),restore_order=['Clear then restore original RMenv; bindexactnew2c/bae BEFORE mod4_task firstimport','OriginalE1entry build_env/truegeometry/reward/phase,50/100/2.5ms32,4/35,38,6','Capture newconstructor nominals before RSL/helperrestore','OriginalRSL actor/critic/STD17Adam/iter/savedLR from samecache','Original'+meta['restore_helper']+' ->loweroriginalD7,D6,D5,D4,D3,D1 helpers via samecache','ONE original sensor-level fullfreshreset; no extra reset/physics/RNG','Preparednative24 means24controls/192physics/48feedback NOUPDATE; separate actualpermission needed'],extra_variants='See EXPLICIT_FROZEN_VARIANTS_SCOPE_V2.json; distributed878/independent113/50 extra state/helper UNKNOWNpending, not dropped',dispatch_or_worker_executed=False)
  art['STATIC_SHA_AST_INDEPENDENT_REVIEW_V1.json']=static;art['EXACT_RESETBANK_700_517_BAE_SOURCE_PROOF_V1.json']=bankproof;art['ACTIVE_SOURCE_CLOCK_UNIT_REVIEW_FINAL_V1.json']=clockreview;art['INSTALL_AND_RESTORE_DEPENDENCY_GRAPH_V1.json']=dep
  for p in commonMocks:art['MOCK/'+p.name]=load(p)
  readme=f'''# {name} MOD4v1 50Hz400N SOURCE_FINAL\n\n- 原母包：{mother['original_count']}行；{mother['full_verified_text_count']}份文本逐SHA join。唯一NPZ仅保存原78af…身份，本轮无stat/read/hash/decode。\n- 真E1 factory/terrain/direction-entry/retention/privateRNG/reward/phase沿原源；不以H1/E0/W35为任务母本。H1仅复用刚实证的通用newnominal guard与精确资产bank几何兼容机制。\n- 纯函数接受未来一次加载的完整dict，只改四leaf：action-state/controlRecipe10k→20k、spring3500→2000及3150/3850→1800/2200。逆向证明、所有其他树/unknownextra/STD17Adam/RNG20k history/queue timestamp不变；receipt在checkpoint之外，不写PT。\n- 50policy/100feedback/2.5ms/TGS32,4/35,38,6；feedback10ms/0,10000us保持。原phase_elapsed和episode/resampling真实秒数不降速。\n- 新2c/bae首次taskimport前绑定；新constructor nominal guard；原complete restore→ONE原freshreset；闭链.01m单env reset/mimic.01rad，无额外精度/owner门。\n- flat133/height74 bank与rough collider bank均显式700→517c→bae组合，不伪装旧身份，不改q/selection/neutralgeometry。rough仍原argmin(root_height-.25)，不是flat74filter；原NPZ实际字节核验留未来。\n- 两套MOCK均明确假字节/假decoder/假tensor/符号clock；不是实际PT或GPU通过。native24接口仅prepared，不派发。future source路径由父指定，LR/iter/Adam从同cached完整dict实际读，不算术填。\n- 六个explicit frozen variants逐项保存；df0review-only不提升，protected878仍一actor/三rank状态片；113为G3 sibling，Slope50为24b后代。其他variant-specific额外state/helpers UNKNOWN/pending，不drop，不称全历史closed。\n- 本轮PT/stat/hash/decode/write、SSH/SDK/GPU/预算/ReadyGO均0；无productionGO/PPO、无新270/地形技能毕业，无独立backend/birth惯量/全硬件DR扩称；D6仍原gas damping。父统一追加Git归档待办，本子未commit/push。\n'''
  plans.append((root,art,readme))
 # All validations finished before sourcefinal seals are written.
 out=[]
 for root,art,readme in plans:
  for rel,value in art.items():
   p=root/rel;p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
  with (root/'README_SOURCE_FINAL.md').open('x',encoding='utf-8') as f:f.write(readme)
  rows=[]
  for p in sorted(root.rglob('*')):
   if p.suffix.lower() in ('.pt','.npz','.usd','.usdc','.zip','.onnx','.safetensors'):continue
   if not p.is_file():continue
   raw=p.read_bytes();row=dict(relative=p.relative_to(root).as_posix(),bytes=len(raw),SHA=H(raw))
   if p.suffix=='.py':row['AST_SHA']=asth(raw)
   rows.append(row)
  index=dict(kind='E1_CANONICAL_SOURCE_FINAL_ONLY_NOT_ACTUAL_SDK_OR_MODEL_PASS',root=str(root),sourcefinal=True,files=rows,explicit_variant_scope='EXPLICIT_FROZEN_VARIANTS_SCOPE_V2.json',validation='STATIC_SHA_AST_INDEPENDENT_REVIEW_V1.json',dependency_graph='INSTALL_AND_RESTORE_DEPENDENCY_GRAPH_V1.json',no_PT_or_SSH_SDK_GPU_budget_ReadyGO=True,unknownfuture_operational_sourcepath_and_variant_extrastate_not_guessed=True,all_source_errors_preserved_under_builder=str(B))
  p=root/'FINAL_SOURCE_INDEX.json'
  with p.open('x',encoding='utf-8') as f:json.dump(index,f,ensure_ascii=False,indent=2)
  out.append(dict(root=str(root),index=str(p),SHA=H(p.read_bytes()),files=len(rows)))
 with (B/'TWO_CANONICAL_SOURCEFINAL_HANDOFF_INDEX_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='TWO_E1_CANONICAL_SOURCE_FINAL_NO_EXECUTION',packages=out,builder_errors_preserved=True,all_historical_variants_closed=False,PT_SDK_SSH_GPU_operations=0),f,indent=2)
 print(json.dumps(dict(status='TWO_SOURCEFINALS_NOT_TARGET_OR_ACTOR_GRADUATION',packages=out),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('E1_SOURCEFINAL_ORIGINAL_REVIEW_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_SSH_GPU_operations=0),f,indent=2)
  raise
