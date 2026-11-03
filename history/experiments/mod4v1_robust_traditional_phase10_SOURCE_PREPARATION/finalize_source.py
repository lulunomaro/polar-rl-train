"""Append-only PH10 source-preparation seal. No Git, SDK, raw/binary reads or tests."""
from pathlib import Path
import datetime,hashlib,json,re,traceback
P=Path(__file__).resolve().parent;WT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def new(p,v):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def meta(p):return {'path':str(p),'relative':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'SHA':sha(p)}
def main():
 assert not(P/'REVIEW_INDEX.json').exists(),'No replay of sealed stage'
 mf=load(P/'SOURCE_MANIFEST.json');gap=load(P/'MISSING_AND_EXCLUSIONS.json');reg=load(P/'CASE_AND_FAILURE_REGISTRY.json');ba=load(P/'SOURCE_BEFORE_AFTER_SHA.json');recovery=load(P/'UNRESOLVED_TEXT_BYTE_PRESERVATION.json')
 authority=mf['scope']['authority'];entries=json.loads(json.dumps(mf['entries']));by={e['source_relative']:e for e in entries};byabs={str(Path(e['path']).resolve()).lower():e for e in entries}
 assert len(authority['closed_roots_under_task'])==13 and ba['all_unchanged'] and not gap['source_changes']
 assert all(x['source_SHA_before']==x['source_SHA_after']for x in ba['checks'])
 for row in recovery['rows']:
  e=by[row['source_relative']];assert e['kind']=='undecodable_metadata_only' and e['observed_source_SHA_before']==row['SHA']==row['source_SHA_after']
  assert sha(WT/row['snapshot_path'])==row['SHA']
  e.update(source_SHA=row['SHA'],snapshot_path=row['snapshot_path'],snapshot_SHA=row['SHA'],kind='exact_small_source_bytes_unresolved_charset',source_encoding='UNRESOLVED_NOT_TRANSCODED',append_only_encoding_preservation_receipt='UNRESOLVED_TEXT_BYTE_PRESERVATION.json')
 checked=0;future=[]
 for e in entries:
  low=e['path'].lower().replace('\\','/')
  assert not any(x in low for x in ('startup_support_geometry_v1','takeoff_momentum_capture_method_v1','mod4_deployment_abi_scope_static_v7'))
  assert not re.search(r'/startup_stand_v(?:[4-9]|[1-9][0-9])(?:/|$)',low)
  assert not re.search(r'/mod4_deployment_[^/]*_v(?:[7-9]|[1-9][0-9])(?:/|$)',low)
  if e['snapshot_path']:assert sha(WT/e['snapshot_path'])==e['snapshot_SHA'];checked+=1
  st=Path(e['path']).stat()
  if (st.st_size,st.st_mtime_ns)!=(e['bytes'],e['mtime_ns']):future.append({'path':e['path'],'future_version_not_substituted':True})
 assert checked==mf['summary']['text_SHA_pairs_verified']+len(recovery['rows'])
 def captured(rel):
  e=by[rel];assert e['snapshot_path'],rel
  return load(WT/e['snapshot_path'])
 # Actual four scheduled attempts. V1 retains ERROR/no result, not a fabricated failed result.
 scheduled=[n for b in reg['batches'].values()for n in b['scheduled_case_names']]
 assert len(scheduled)==len(set(scheduled))==4
 wanted={'startup_front065_nominal_v1','startup_front065_coupled_v2_nominal1','startup_front065_tracking_v3a_nominal1','startup_front065_tracking_v3b_nominal1'};assert set(scheduled)==wanted
 observed=reg['physical_results']+reg['software_ERROR_records'];assert {x['case']for x in observed}==wanted and len(reg['physical_results'])==3 and len(reg['software_ERROR_records'])==1
 causal=captured('STARTUP_FRONT_CAUSAL_001/MINIMUM_OBSERVED.json');last=causal['final_control_row'];assert causal['original_consumption_controls']==601 and causal['original_consumption_physics_steps']==12020
 rows=[]
 for x in observed:
  v=x['original_payload'];case=x['case'];assert v['physics_steps']==20*v['controls']
  iserr=case=='startup_front065_nominal_v1'
  if iserr:
   assert 'runtime_receipt' in v['error']and 'AttributeError' in v['error']and v['controls']==601
   assert last['phase']['phase']=='INHIBIT' and 'timeout' in last['phase']['fault_reason']
   assert not any(e['source_relative']=='results/'+case+'/result.json'for e in entries)
   complete=None;gate=None;fault=last['phase']['fault_reason'];phase=last['phase']['phase'];stop='controller_timeout_then_postprocessing_API_error'
  else:
   assert v['complete']is False and v['startup_stand_original_v1_gate']is False and v['first_BALANCE_command_s']is None
   complete=v['complete'];gate=v['startup_stand_original_v1_gate'];fault=v['controller_fault_reason'];phase=v['controller_phase'];stop=v['stop']
  rows.append({'case':case,'evidence_path':x['path'],'evidence_SHA':x['source_SHA'],'evidence_type':'ERROR_AND_SAVED_CAUSAL_PREFIX_NO_RESULT'if iserr else'ORIGINAL_FORMAL_RESULT','controls':v['controls'],'physics_steps':v['physics_steps'],'complete_field':complete,'original_gate_field':gate,'first_BALANCE':None,'phase':phase,'fault':fault,'stop':stop,'formal_result_missing_not_backfilled':iserr,'known_standup_pass':False,'original_payload_retained':True})
 assert sum(x['controls']for x in rows)==2101 and sum(x['physics_steps']for x in rows)==42020
 passive=[]
 for rel,e in by.items():
  if rel.startswith('STARTUP_STAND_V1/passive_settle001/')and rel.endswith('/result.json'):
   v=captured(rel);assert v['complete']is True and v['physics_steps']==4000 and v['controller_calls']==0 and v['root_overwrites_after_initialization']==0 and v['assist_forces']==0
   passive.append({'path':e['path'],'SHA':e['source_SHA'],'case':v['case'],'classification':v['final_classification'],'physics_steps':v['physics_steps'],'controller_calls':v['controller_calls'],'final_rpy_rad':v['final_rpy_rad'],'final_root_xyz_m':v['final_root_xyz_m'],'stationary_tail_s':v['stationary_tail_s'],'not_standup_or_real_poweroff_electrical_validation':True})
 assert len(passive)==3 and sum(x['physics_steps']for x in passive)==12000
 new(P/'CASE_RECONCILIATION.json',{'status':'ORIGINAL_FOUR_CONTROLLED_ATTEMPTS_AND_THREE_PASSIVE_FIXTURES_SEPARATE_NOT_NEW_TRIALS','controlled':rows,'batches':reg['batches'],'controlled_attempts':4,'controlled_actual_controls':2101,'controlled_actual_physics_steps':42020,'controlled_full_duration_completions':0,'original_formal_gate_false_results':3,'missing_result_with_ERROR_prefix':1,'known_standup_passes':0,'not_a_robot_0ofN_reliability_estimate':True,'passive':passive,'passive_model_steps':12000,'passive_front065_front125_same_final_class_not_three_independent_pose_envelopes':True,'archive_added_physics_steps':0,'no_original_raw_open_or_hash':True})
 # Build dependency variants are one logical main.c TU, not three target-coverage TUs.
 builds=[]
 for rel in ['MOD4_DEPLOYMENT_TARGET_COMPILE_V3/COMPILE_RESULT_V3A_01.json','MOD4_DEPLOYMENT_TARGET_COMPILE_V4/COMPILE_RESULT_V4_01.json','MOD4_DEPLOYMENT_TARGET_COMPILE_V6/COMPILE_RESULT_V6_01.json']:
  z=captured(rel);assert z['C_compile_count']==1 and z['ASM_compile_count']==0 and len(z['TU_results'])==1
  tu=z['TU_results'][0];assert tu['id']==1 and tu['name']=='main.c'and tu['language']=='C'
  builds.append({'source_record':by[rel],'status':z['status'],'C_attempts':z['C_compile_count'],'ASM_attempts':z['ASM_compile_count'],'logical_TU':tu['name'],'source_now':tu['source_now'],'compiler_exit':tu['exit'],'object_exists':tu['object_exists'],'object':tu.get('object'),'unstarted_TUs':len(z['unstarted_TU_ids']),'target_links':z['target_links']})
 assert [x['compiler_exit']for x in builds]==[1,1,0]and [x['object_exists']for x in builds]==[False,False,True]
 v6=captured('MOD4_DEPLOYMENT_TARGET_COMPILE_V6/FACTS_V6_FINAL.json');v6rec=captured('MOD4_DEPLOYMENT_TARGET_COMPILE_V6/RECEIPT_V6_FINAL.json')
 assert v6rec['post_gate_accepted']==0 and v6rec['V6_unstarted']==162 and v6rec['V6_objects']==1 and v6rec['V6_links']==0 and not v6rec['ready_for_full_target_or_link_or_flash']
 new(P/'TARGET_VARIANT_RECONCILIATION.json',{'status':'V3A_V4_V6_ONE_MAIN_TU_THREE_DEPENDENCY_VARIANTS_NOT_TARGET_COMPLETION','variants':builds,'logical_unique_translation_units':1,'V6_saved_receipt':v6rec,'V6_original_FILE_gate_checks':v6['original_gate_checks'],'V6_object_scope':{k:v6['object_ELF_and_ABI_FILE_scope'][k]for k in ['ELF_class','ELF_data','ELF_type','ELF_machine','SHA','bytes']},'V6_original_gate_false_unchanged':True,'SECTION_wchar_enum_evidence_is_not_FILE_gate_acceptance_or_whole_link_certificate':True,'V5_metadata_only_not_compile':True,'no_C7_C8_or_new_object_read_compile_link_probe':True})
 # Preserve original/readable identities independently; no ZIP or original-program execution.
 selected=captured('DEPLOYED_BASELINE_AUDIT_V1/SELECTED_SOURCE_MANIFEST.json');assert len(selected['files'])==391
 encoding=[]
 for row in selected['files']:
  out={k:row[k]for k in ['member','CRC32','raw_bytes','raw_SHA','original_path','encoding','readable_path','readable_bytes','readable_SHA']}
  for prefix,pathkey,hashkey in [('original','original_path','raw_SHA'),('readable','readable_path','readable_SHA')]:
   e=byabs[str(Path(row[pathkey]).resolve()).lower()];assert e['source_SHA']==row[hashkey]
   out[prefix+'_archive_path']=e['snapshot_path'];out[prefix+'_byte_snapshot_verified']=e['snapshot_path']is not None
  encoding.append(out)
 assert all(x['original_byte_snapshot_verified']and x['readable_byte_snapshot_verified']for x in encoding)
 new(P/'ENCODING_AND_SOURCE_IDENTITY_REGISTRY.json',{'status':'RAW_TEXT_BYTES_AND_READABLE_UTF8_IDENTITIES_SEPARATE_NOT_ARCHIVE_HASH_RECOMPUTATION','selected_manifest_reference':by['DEPLOYED_BASELINE_AUDIT_V1/SELECTED_SOURCE_MANIFEST.json'],'selected_text_pairs':encoding,'selected_pair_count':len(encoding),'same_SHA_pairs':sum(x['raw_SHA']==x['readable_SHA']for x in encoding),'different_SHA_transcoded_pairs':sum(x['raw_SHA']!=x['readable_SHA']for x in encoding),'unresolved_small_source_charset_byte_receipt':recovery,'V6_compiler_used_raw_header_not_readable_UTF8':True,'crc_is_existing_producer_CRC_not_fresh_archive_SHA':True,'archive_Downloads_WeChat_git_or_embedded_code_reads_and_execution':0})
 raw=[e for e in entries if e['snapshot_path']is None];unknown=[e for e in raw if e.get('source_SHA')is None]
 remaining=[];binary=[]
 for c in gap['unresolved_version_claims']:
  (binary if Path(c['path']).suffix.lower()in {'.exe','.dll','.obj','.o','.jsonl','.npz','.zip','.lib'}else remaining).append(c)
 unique={(c['path'].lower(),c['expected_SHA'])for c in remaining};assert len(unique)==1 and next(iter(unique))[1]=='eea7bbf33028a3abaf697a3ec76c06fefdf53d68c8f551a6b9593fba157f048d'
 assert len(binary)==8 and len(unknown)==4
 previous=WT/'history/experiments/mod4v1_robust_traditional_phase9_SOURCE_PREPARATION/FINAL_GAPS_AND_EXCLUSIONS.json'
 new(P/'FINAL_GAPS_AND_EXCLUSIONS.json',{'status':'GAPS_PRESERVED_UNRESOLVED_CHARSET_BYTES_SAVED_APPEND_ONLY_NO_HISTORY_REBUILD','initial_missing_events':gap['missing'],'external_pointers_not_expanded':True,'actual_missing_saved_smalltext_claims':remaining,'missing_saved_smalltext_unique':len(unique),'historical_binary_claims':binary,'binary_claims8_are_two_artifacts_not8_missing_texts':True,'current_raw_unknowns':unknown,'current_raw_unknown_count':len(unknown),'unknown_libraries2_executables2_not_rehashed':True,'previous_phase_gap_reference':{'path':str(previous),'SHA':sha(previous),'commit':'7b7d2633a25dad356809a56ddfa2d546f1cded10'},'old_gap_overlap_not_summed_or_reconstructed':True,'original_reader_events':gap.get('original_json_or_syntax_reader_events',[]),'task_reader_events':load(P/'READER_EVENTS.json'),'encoding_byte_preservation':recovery,'exclusions':gap['exclusions'],'authority_exclusions':authority['explicit_exclusions'],'management_failure_files':[meta(p)for p in sorted(P.glob('*FAILURE*.txt'))],'source_capture_changes':gap['source_changes'],'postcapture_future_metadata_only':future,'parent_review_before_Git':True,'postcut_phase11_pending':True})
 qualification={'startup':'Four actual controlled attempts, zero full-duration completion/known pass. V1 controller timeout and subsequent missing runtime_receipt API reporting error separate. No replacement result or repeat trial. Passive settles are initial fixtures, not powered standup or electrically realistic poweroff.','controller':'Old V1/499, V2 and V3 synthetic math/API proof are not real convergence/stability; nested/Base comparators not robot episodes. V3 A good q tracking did not establish posture/support. B encoder rotation proxy exceeded .50m while true XY stayed below .50m; not proof of slip or chassis-limit violation.','gates':'Original 6s timeout, joint/observer/driver/signed DC/limits unchanged; true 2k double-wheel/no-other samples and 100Hz pose/error/height gates unchanged; no between-sample continuous-contact proof.','old_firmware':'Actually deployed package source and board/startup audits, not MOD4 hardware-bound code. Calibration/stand-up reachability and uninitialized-read/static pitfalls remain findings, not executed old-code faults. Source bytes vs readable UTF8 and raw/current CRC identities not merged.','target':'V3A and V4 main compilation failed; V6 same logical main TU compiled object then original FILE-only ABI gate stopped. SECTION-level wchar2/enum-smallest evidence is not accepted prefix, full target link, startup, board/HIL/WCET/flash. V5 metadata only.','open_goal':'Standup from other poses/DR, full-RM/270mm/contact-FSM, actual driver-power/unique-send/BSP/HIL/WCET remain open; H1/H2/H4/H5/Stage1/old scores unchanged.','cutoff':'New SUPPORT_GEOMETRY (separate approved 1compile/9forward/0step study), C7 and C8, future V4 implementation/proofs/gains/cases and paused momentum/R64 excluded. This worker archive0model/PHY is not all-session0model.','whole_goal':'active, no Goal action'}
 new(P/'QUALIFICATION_BOUNDARIES.json',qualification)
 summary={**mf['summary'],'initial_capture_summary_preserved':True,'new_text_copies':mf['summary']['new_text_copies']+len(recovery['rows']),'new_text_bytes':mf['summary']['new_text_bytes']+sum(x['bytes']for x in recovery['rows']),'text_SHA_pairs_verified':checked,'raw_metadata_only':len(raw),'raw_existing_producerSHA_known':sum(x.get('source_SHA')is not None for x in raw),'current_raw_unknowns':len(unknown),'exact_small_source_unresolved_charset_rows':len(recovery['rows']),'controlled_actual_controls':2101,'controlled_actual_steps':42020,'controlled_complete':0,'known_standup_passes':0,'passive_cases':3,'passive_actual_steps':12000,'target_unique_main_TU':1,'target_dependency_variants':3,'current_missing_saved_smalltext_unique':len(unique)}
 assert summary['new_text_copies']+summary['prior_Git_text_references']+summary['raw_metadata_only']==summary['source_entries']
 new(P/'FINAL_SOURCE_MANIFEST.json',{**mf,'entries':entries,'summary':summary,'initial_manifest_SHA':sha(P/'SOURCE_MANIFEST.json'),'append_only_encoding_preservation_SHA':sha(P/'UNRESOLVED_TEXT_BYTE_PRESERVATION.json'),'source_consistency_before_after':{'original_checks':len(ba['checks']),'original_receipt_SHA':sha(P/'SOURCE_BEFORE_AFTER_SHA.json'),'additional_exact_small_source_checks':len(recovery['rows']),'all_equal':True},'no_capture_refresh_or_active_scope_expansion':True})
 new(P/'FINAL_CONSISTENCY_RECEIPT.json',{'status':'PH10_LOCAL_SOURCE_PREPARATION_VERIFIED_WAIT_PARENT_REVIEW_NO_GIT','prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authority':mf['scope']['authority_path'],'authority_SHA':mf['scope']['authority_SHA'],'summary':summary,'text_snapshot_SHA_pairs_checked':checked,'small_source_before_after_checks':len(ba['checks'])+len(recovery['rows']),'all_before_capture_after_equal':True,'postcapture_future_metadata_only':future,'redactions':0,'record_stage_commit_tag_push_calls':0,'archive_worker_model_FK_PHY_QA_compile_Git_agents_GPU_realIO_calls':0,'large_raw_lib_obj_ZIP_USD_PDF_hash_reads':0,'only_additional_original_source_reads':'3 already-admitted 53KB C/header byte preservation, no charset claim','sourceRoot_oldexpertindex_main_helper_modified':False,'parent_review_before_Git':True,'postcut_phase11_pending':True})
 lines=['# PH10 SOURCE_PREPARATION — 父cutoff review待定；Git未授权/未调用','',
  '## 实际证据与计数',
  f"- {summary['source_entries']} entries = {summary['new_text_copies']} new small source/text ({summary['new_text_bytes']}B) + {summary['prior_Git_text_references']} PH1–9 exact refs + {len(raw)} metadata-only; {checked} snapshot及before/after SHA一致。",
  '- 四个controlled原attempt=2101 controls/42020 steps；0 full-duration complete、0 known original standup pass。3 formal result原gateFalse；V1保留ERROR/601+12020与timeout小诊断，缺result不回填、不把全部失败归为后处理错误。',
  '- 三个独立被动settle=12000历史steps、controller0；front065/front125同类自然settled，不是三种独立起立姿态或技能通过。不得合并为可靠性样本。',
  '- V3A/V4/V6是main.c同一logical TU的三个依赖变体；前两失败、V6一个object成功后原FILE-only ABI gateFalse/accepted0/162 unstarted，0link。SECTION证据另存，未改判，C7/C8未收。','',
  '## 原始字节、缺口、失败',
  '- 391 selected pairs分别保存original/readable SHA与路径/CRC/encoding。三个原本decode-failed小C/header已append-only按原字节保存，共159933B；不猜原charset、不转码替代编译输入；原metadata及错误不改。',
  '- 真实旧FSM savedtext SHA缺口1；旧binary8claims仅两exe。当前raw未知4=两lib+两exe，无重hash/重建。旧phase真实缺口引用保留且不相加；12个outside指针只保存已知metadata。',
  '- 根名与target REPORT.md猜测reader错误/生成器substring管理失败/编码补存首次“2个而实际3个”断言均保存原source+trace；均非机器人或compiler失败。原始V1报告API error、A分析KeyError、typed/preloop/proof失败与更正原样保留。','',
  '## 精确边界',
  '- 13closed roots+49显式根名及实际闭合import/provenance，不靠mtime。SUPPORT_GEOMETRY全部、C7/C8、未来STARTUP_STAND_V4+代码/QA/gain/cases、momentum/R64+均排除。封存V4_METHOD_PROPOSAL仅未执行方案。',
  '- 本archive worker0model/FK/PHY/旧QA/compile/GPU/newagent/realIO/Goal/Git动作；另已批准geometry1compile9forward是同session其他任务且EXCLUDED，绝不声称全session模型调用0。',
  '- 无Downloads/WeChat/原ZIP/.git/大raw/mesh/lib/obj内容读hash；无原始实验补跑/源或阈值分数修改/main/expertindex/helper写。归档不等于target固件/站起/硬件验收。Goal active。','',
  '## 审阅入口',
  '- [CASE_RECONCILIATION](<CASE_RECONCILIATION.json>) / [TARGET_VARIANT_RECONCILIATION](<TARGET_VARIANT_RECONCILIATION.json>) / [ENCODING](<ENCODING_AND_SOURCE_IDENTITY_REGISTRY.json>)',
  '- [FINAL_SOURCE_MANIFEST](<FINAL_SOURCE_MANIFEST.json>) / [CONSISTENCY](<FINAL_CONSISTENCY_RECEIPT.json>) / [GAPS](<FINAL_GAPS_AND_EXCLUSIONS.json>) / [QUALIFICATION](<QUALIFICATION_BOUNDARIES.json>) / [SOURCE_BEFORE_AFTER](<SOURCE_BEFORE_AFTER_SHA.json>)',
  '- [SCOPE](<SCOPE.md>) / [初始未更改清单](<SOURCE_MANIFEST.json>) / [byte-preservation erratum](<UNRESOLVED_TEXT_BYTE_PRESERVATION.json>)。REVIEW_INDEX本身独立SHA；等待父逐项review后另批一次Git，不自动record/stage/commit/tag/push。']
 assert len(lines)<=100
 (P/'REVIEW_HANDOFF.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 links=0
 for p in P.glob('*.md'):
  for link in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf-8')):
   assert(p.parent/link.split('#')[0]).exists(),(str(p),link);links+=1
 files=[meta(p)for p in sorted(P.rglob('*'))if p.is_file()and '__pycache__'not in p.parts and p.name!='REVIEW_INDEX.json']
 new(P/'REVIEW_INDEX.json',{'status':'PH10_LOCAL_SOURCE_ONLY_READY_FOR_PARENT_REVIEW_NO_RECORD_COMMIT_TAG_PUSH','files':files,'count':len(files),'review_handoff':meta(P/'REVIEW_HANDOFF.md'),'manifest':meta(P/'FINAL_SOURCE_MANIFEST.json'),'consistency':meta(P/'FINAL_CONSISTENCY_RECEIPT.json'),'gaps':meta(P/'FINAL_GAPS_AND_EXCLUSIONS.json'),'qualification':meta(P/'QUALIFICATION_BOUNDARIES.json'),'parent_review_required_before_Git':True,'review_link_count':links,'postcut_phase11_pending':True})
 print(json.dumps({'status':'PH10_SOURCE_ONLY_LOCALLY_SEALED_WAIT_PARENT_REVIEW','summary':summary,'artifacts':[meta(P/n)for n in ['REVIEW_HANDOFF.md','REVIEW_INDEX.json','FINAL_SOURCE_MANIFEST.json','FINAL_CONSISTENCY_RECEIPT.json']],'controlled_cases':[(x['case'],x['controls'],x['physics_steps'])for x in rows],'passive_steps':sum(x['physics_steps']for x in passive),'links':links,'Git_calls':0},ensure_ascii=True))
if __name__=='__main__':
 try:main()
 except BaseException:
  n=1
  while(P/f'FINALIZATION_FAILURE_{n:03d}.txt').exists():n+=1
  (P/f'FINALIZATION_FAILURE_{n:03d}.txt').write_text(traceback.format_exc(),encoding='utf-8')
  (P/f'FINALIZATION_FAILURE_SOURCE_{n:03d}.py').write_bytes(Path(__file__).read_bytes())
  raise
