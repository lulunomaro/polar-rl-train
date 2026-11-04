"""NEW parent-approved saved-only closure. Read798 snapshots/prior metadata/ParentExpected; never recapture sources/raw/map/controller."""
from pathlib import Path
import collections,hashlib,json,ntpath,os,re,subprocess,traceback
D=Path(__file__).resolve().parent;W=D.parents[2];R=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102');P10=W/'history/experiments/mod4v1_robust_traditional_phase10_SOURCE_PREPARATION';H='e176d2a6401fafb9d618a042acba8190023c3273'
HEX=re.compile(r'^[0-9a-fA-F]{64}$');ABS=re.compile(r'^[A-Za-z]:[\\/]');RAW={'.o','.obj','.a','.lib','.exe','.axf','.elfbin','.elf','.bin','.hex','.zip','.7z','.gz','.usd','.usda','.usdc','.stl','.npy','.npz','.pt','.pth','.onnx','.png','.jpg','.pdf','.mp4'}
def norm(p):return ntpath.normcase(ntpath.normpath(str(p)))
def digest(b):return hashlib.sha256(b).hexdigest()
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=digest(b))
def load(p):return json.loads(p.read_bytes())
def save(n,v):
 with(D/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def rawrole(p):return p.suffix.lower()in RAW or p.name.lower()in('trace.jsonl','physics.jsonl')or '/MODEL_AUDIT/'in p.as_posix()
def excluded(p):
 s=str(p).replace('\\','/');return bool(re.search(r'STARTUP_STAND_V6|body_crouch_v6|run_startup_stand_case_v8|CONTINUATION_V6_|MOD4_DEPLOYMENT_[^/]*_V(?:1[89]|[2-9][0-9])(?:/|$)|/xwechat_files/|/\.git/|/expert/|/canonical/|/credentials/',s,re.I))
def walk(o):
 todo=[(o,'$')];seen=0
 while todo:
  v,loc=todo.pop();seen+=1
  assert seen<=3000000,'Bounded metadatawalker capacity'
  if isinstance(v,dict):
   hs=[]
   for k in ['SHA','sha','SHA256','sha256','source_SHA','raw_SHA','expected_SHA','snapshot_SHA','hash']:
    z=v.get(k)
    if isinstance(z,str)and HEX.fullmatch(z):hs.append(z.lower())
    elif isinstance(z,list):hs.extend(a.lower()for a in z if isinstance(a,str)and HEX.fullmatch(a))
   if isinstance(v.get('source_pin'),dict):
    z=v['source_pin'].get('SHA')
    if isinstance(z,str)and HEX.fullmatch(z):hs.append(z.lower())
   for k in ['path','source','source_path','source_absolute','source_absolute_path','file_path','output_object','object_path','filename','artifact']:
    a=v.get(k)
    if isinstance(a,str)and ABS.match(a):yield a,sorted(set(hs)),loc+'.'+k,v.get('bytes',v.get('size'))
   for k,z in v.items():
    if isinstance(k,str)and ABS.match(k)and isinstance(z,str)and HEX.fullmatch(z):yield k,[z.lower()],loc+'.<path_key>',None
    if isinstance(z,(dict,list)):todo.append((z,loc+'.'+str(k)))
  elif isinstance(v,list):todo.extend((x,loc+'['+str(i)+']')for i,x in enumerate(v)if isinstance(x,(dict,list)))
def git(label,*args):
 out=D/(label+'.stdout.txt');err=D/(label+'.stderr.txt');env=dict(os.environ);env['GIT_OPTIONAL_LOCKS']='0'
 with(D/'GIT_READONLY_LEDGER.jsonl').open('a',encoding='utf-8')as f:f.write(json.dumps(dict(event='reserved',label=label,argv=['git','-C',str(W),*args],allowed_readonly=True,index_mutation=False))+'\n')
 with out.open('xb')as a,err.open('xb')as b:q=subprocess.run(['git','-C',str(W),*args],stdin=subprocess.DEVNULL,stdout=a,stderr=b,env=env)
 with(D/'GIT_READONLY_LEDGER.jsonl').open('a',encoding='utf-8')as f:f.write(json.dumps(dict(event='returned',label=label,rc=q.returncode,stdout=rec(out),stderr=rec(err)))+'\n')
 assert q.returncode==0;return out.read_text(encoding='utf-8').strip()
def main():
 assert not(D/'SOURCE_MANIFEST.json').exists()and (D/'SOURCE_CAPTURE_SCHEMA_FAILURE_RECEIPT_001.json').is_file()
 prefix=load(D/'CAPTURE_FIRST_STOP.json');rows=prefix['copied_text_records'];fs=load(D/'FILESET_ALLOWLIST.json');assert len(rows)==len({x['snapshot_path']for x in rows})==798
 scope_entry=next(x for x in rows if x['source_relative']=='ARCHIVE_PHASE11_V5_FIRST_LINK_V17_CUTOFF_FINAL.json');scope=load(W/scope_entry['snapshot_path']);pins=load(D/'PRIOR_CONTEXT_PINS.json')
 priorpath=P10/'FINAL_SOURCE_MANIFEST.json';assert rec(priorpath)==pins['PH10_manifest'];prior=load(priorpath)
 expected_path=R/'PH11_PARENT_CLOSED_EXPECTED_FACTS_V1.json';expected=load(expected_path);assert expected['status']=='PASS_PARENT_INDEPENDENT_SMALL_CLOSED_JSONS_NOT_CONTROLLER_QA'
 save('SAVED_CLOSURE_STARTED_001.json',dict(status='NEW_SAVED_ONLY_CLOSURE_ENTERED_BEFORE_READER',immutable798=rec(D/'CAPTURE_FIRST_STOP.json'),schema_event=rec(D/'SOURCE_CAPTURE_SCHEMA_FAILURE_RECEIPT_001.json'),parent_expected=rec(expected_path),no_original_source_payload_or_capture_rerun=True))
 docs=[];by_path={};by_sha=collections.defaultdict(list);snapshot_verified=[];enc=[];saved_json_decode_gaps=[]
 for x in rows:
  p=W/x['snapshot_path'];assert p.resolve().is_relative_to((D/'snapshot').resolve())and not excluded(Path(x['path']))and not rawrole(Path(x['path']))
  b=p.read_bytes();assert len(b)==x['bytes']and digest(b)==x['source_SHA']==x['snapshot_SHA'],('STOP savedbyte mismatch',x['snapshot_path'])
  snapshot_verified.append(dict(snapshot_path=x['snapshot_path'],bytes=len(b),SHA=digest(b),equals_captured_source_before=True));by_path[norm(x['path'])]=x;by_sha[x['source_SHA']].append(x)
  if x['encoding'].startswith('UNRESOLVED'):enc.append(dict(path=x['path'],raw_SHA=x['source_SHA'],encoding=x['encoding'],readable_SHA=None,original_bytes_retained=True))
  if Path(x['path']).suffix.lower()=='.json':
   try:docs.append((x['path'],json.loads(b.decode('utf-8-sig'))))
   except (UnicodeDecodeError,json.JSONDecodeError)as ex:saved_json_decode_gaps.append(dict(path=x['path'],snapshot_path=x['snapshot_path'],error=str(ex),original_bytes_preserved=True,no_repair=True))
 docmap={norm(p):v for p,v in docs}
 # Six already-authorized bounded ParentExpected inputs are compared to saved bytes, not live originalfiles.
 for e in expected['sources']:
  x=by_path[norm(e['path'])];assert x['source_SHA']==e['SHA']and x['bytes']==e['bytes'],('ParentExpected savedinput mismatch',e['path'])
 cases=[]
 for name,n,steps in zip(scope['new_physical_registry']['ids'],scope['new_physical_registry']['controls'],scope['new_physical_registry']['physics_steps']):
  result=docmap[norm(R/'results'/name/'result.json')];batch=docmap[norm(R/'batches'/name/'BATCH_RESULT.json')]
  for k in ['complete','startup_stand_original_v1_gate']:assert k in result and type(result[k])is bool and result[k]is False,(name,k)
  assert type(result['controls'])is int and type(result['physics_steps'])is int and result['controls']==n and result['physics_steps']==steps
  assert 'first_BALANCE_command_s'in result and result['first_BALANCE_command_s']is None and 'software_failure'in batch and type(batch['software_failure'])is bool and batch['software_failure']is False
  ep=next(x for x in expected['cases']if x['case_id']==name);assert ep['controls']==n and ep['physics_steps']==steps and ep['original_gate']is False and ep['complete']is False and ep['software_failure']is False
  cases.append(dict(case_id=name,controls=n,physics_steps=steps,complete=False,original_gate=False,formal_result_present=True,software_failure=False,first_BALANCE_command_s=None,stop=result['stop'],fault=result['controller_fault_reason'],end_stable_s=result['end_stable_s'],trace_producer=result['trace_artifact'],physical_producer=result['physical_artifact'],raw_payload_open_or_hash=False))
 assert sum(x['controls']for x in cases)==expected['new_cutoff_controls']==381 and sum(x['physics_steps']for x in cases)==expected['new_cutoff_physics_steps']==7620
 c16=docmap[norm(R/'MOD4_DEPLOYMENT_FIRST_LINK_V16/RESULT.json')];ids=docmap[norm(R/'MOD4_DEPLOYMENT_FIRST_LINK_V16/CURRENT_INPUT_IDENTITIES.json')]
 assert c16['link_calls']==1 and c16['returncode']==0 and c16['output_bytes']==629048 and c16['latest_MOD4_C3_startup_integration']is False and c16['full_hardware_firmware_qualified']is False
 assert ids['objects']==163 and ids['opaque_user_libs']==2 and ids['current_payload_hashes']==len(ids['records'])==165
 claims=[]
 for p,o in docs:
  for a,hs,l,sz in walk(o):claims.append(dict(path=a,SHAs=hs,producer=p,location=l,producer_bytes=sz))
 pm=collections.defaultdict(list);pv={}
 for e in prior['entries']:
  pm[norm(e['path'])].append(e)
  for h in [e.get('source_SHA'),e.get('snapshot_SHA')]:
   if isinstance(h,str)and HEX.fullmatch(h):pv[(norm(e['path']),h)]=e
 for e in prior['source_version_claims_resolved']:
  if e.get('snapshot_path')and isinstance(e.get('expected_SHA'),str):pv[(norm(e['path']),e['expected_SHA'])]=dict(path=e['path'],source_SHA=e['expected_SHA'],snapshot_SHA=e['expected_SHA'],snapshot_path=e['snapshot_path'],kind='PH10_resolved_saved_version')
 tree={}
 for line in (D/'git07_prior_bounded_tree.stdout.txt').read_bytes().split(b'\0'):
  if not line:continue
  a,p=line.split(b'\t',1);mode,typ,oid,n=a.decode('ascii').split()
  if typ=='blob':tree[p.decode('utf-8')]=dict(blob_oid=oid,bytes=int(n),mode=mode)
 refs=[];versions=[];excludedrefs=[];gaps=[];raw={};seen=set()
 def addraw(path,hs,producer,location,sz):
  k=norm(path);v=raw.setdefault(k,dict(path=str(path),kind='raw_metadata_only',archive_payload_opened=False,archive_SHA_recomputed=False,producer_claims=[],preflight_stat=None))
  item=dict(SHAs=hs,producer=producer,location=location,producer_bytes=sz)
  if item not in v['producer_claims']:v['producer_claims'].append(item)
 for f in fs['files']:
  if rawrole(Path(f['path'])):
   addraw(f['path'],[],fs['scope']['path'],'finiteallowlist_stat_only',f['bytes']);raw[norm(f['path'])]['preflight_stat']=dict(bytes=f['bytes'],mtime_ns=f['mtime_ns'])
 for q in claims:
  p=Path(q['path']);k=norm(p)
  for h in q['SHAs']or[None]:
   ident=(k,h)
   if ident in seen:continue
   seen.add(ident);cl=dict(path=str(p),expected_SHA=h,producer=q['producer'],location=q['location'])
   if excluded(p):excludedrefs.append(dict(**cl,reason='declared_activeV6_future_or_unrelated_context_not_missing_original'));continue
   if rawrole(p):addraw(p,[]if h is None else[h],q['producer'],q['location'],q['producer_bytes']);continue
   if k in by_path and (h is None or h==by_path[k]['source_SHA']):versions.append(dict(**cl,resolution='captured_closedepoch_exact_saved_bytes',snapshot_path=by_path[k]['snapshot_path']));continue
   e=pv.get((k,h))if h else next((a for a in pm[k]if a.get('snapshot_path')),None)
   rp=e.get('snapshot_path')if e else None
   if rp and rp in tree:
    t=tree[rp];refs.append(dict(**cl,kind='exact_prior_Git_reference',prior_commit=H,repo_path=rp,Git_blob_oid=t['blob_oid'],archived_bytes=t['bytes'],prior_source_SHA=e.get('source_SHA'),prior_snapshot_SHA=e.get('snapshot_SHA'),prior_encoding=e.get('encoding'),identity_basis='PreviouslycommittedPH10map+savedactualboundedHEADtree; no originalsource/blob reread',historical_kind=e.get('kind')));continue
   if h in by_sha:versions.append(dict(**cl,resolution='exact_saved_content_digest_version',snapshot_path=by_sha[h][0]['snapshot_path'],pathname_not_inferred=True));continue
   if e and e.get('kind')=='raw_metadata_only':addraw(p,[]if h is None else[h],q['producer'],q['location'],q['producer_bytes']);continue
   if not(p.is_relative_to(R)or p.is_relative_to(R.parent/'traditional_control_20261101')):excludedrefs.append(dict(**cl,reason='external_tool_primary_web_temp_context_metadata_only_no_file_access'));continue
   # No new livefiles or substitute versions permitted in this saved closure.
   if h:gaps.append(dict(**cl,kind='declared_historical_version_not_in_saved_or_prior_map',current_live_file_not_read_or_substituted=True,UNKNOWN=True))
   else:excludedrefs.append(dict(**cl,reason='path_without_version_context_only_not_executable_admission'))
 # All late C16 identities stay supplemental to historical PH10 fourunknowns; no sourcegap reconstruction.
 save('SOURCE_MANIFEST.json',dict(status='PH11_NEW_SAVED_SOURCE_ONLY_READY_FOR_PARENT_REVIEW_NOT_RECORD',scope_snapshot=scope_entry,snapshot_entries=rows,prior_Git_text_references=refs,source_version_resolutions=versions,raw_metadata_only=list(raw.values()),selected_epoch_snapshot_bytes_equal=True,original_live_after_SHA_NOT_RECHECKED=True,original_capture_not_rerun=True))
 save('SOURCE_SNAPSHOT_IDENTITY_PINS.json',dict(snapshot_records=snapshot_verified,verified798=True,original_source_before_pins_from_first_capture=True,original_live_after_full_SHA_check='NOT_REACHED_before_firstschemaerror_and_NOT_RERUN_under_saved_only_grant',snapshot_refresh_or_replacement=False))
 save('CASE_AND_TARGET_REGISTRY.json',dict(new_physical_cases=cases,new_cutoff_case_count=2,new_cutoff_controls=381,new_cutoff_physics_steps=7620,formalFalse=2,complete0=2,old_gate_passes=0,cumulative_context=scope['cumulative_context'],old_V1_ERROR_has_no_result_no_backfill=True,passive_cases_separate=3,passive_steps_separate=12000,not_independent_0of6_qualification_rate=True,target=dict(unique_C162_segmented=[1,39,122],cleanbuild_or_u4reproduction=False,one_firstASM=True,first_actual_link=c16,current_input_identities=ids,no_image_object_lib_payload_read=True,not_C3_or_hardware=True),staticgeometry=dict(modelcompile=1,forward=9,PHY=0,notdynamic=True),archiveworker_zero_PHY_not_wholesession_zero=True,ALL_V6_V7_C18_and_future_excluded=True))
 save('FAILURE_ENCODING_GAPS_EXCLUSIONS.json',dict(first_collector_error=rec(D/'SOURCE_CAPTURE_SCHEMA_FAILURE_RECEIPT_001.json'),new_saved_reader_exact_required_field='startup_stand_original_v1_gate',no_proposed_gate_added_or_result_rewritten=True,historical_version_gaps=gaps,saved_JSON_decode_gaps=saved_json_decode_gaps,prior_PH10_historical_context=pins['prior_summary'],prior_PH10_4_raw_unknowns_preserved=True,late_C16_current165_claims_not_rewrite_oldunknowns=True,encoding_rows=[dict(path=x['path'],original_SHA=x['source_SHA'],readable_UTF8_SHA=x.get('readable_UTF8_SHA'),encoding=x['encoding'])for x in rows],declared_exclusions=scope['explicit_exclusions'],excluded_references=excludedrefs,C17_closing_failure_notification=dict(delivery_before_event=True,cause='UNKNOWN',map_rerun=False),intentionalnegativefixtures_not_corruption=True,source_epoch_live_after_uncertainty_explicit=True))
 save('OPERATION_COVER_TWO_CASE_AND_SAVED_CLOSURE.json',dict(parent_two_case_batch_location_addendum='Parent explicit two-case/batch-path clarification, message07640; timestamp not fabricated',parent_saved_closure_grant='2026-11-04 06:50:42',existing_FINAL_unchanged=True,ParentExpected=rec(expected_path),only_6already_authorized_parent_input_SHA_compared_to_snapshots=True,parent_expected_only_operation_evidence_not_runtime_dependency=True,original798_not_overwritten=True,closed_source_error_preserved=True,queued_C18_scope_not_read_or_started=True))
 assert git('git09_savedclose_head','rev-parse','HEAD')==H and git('git10_savedclose_branch','rev-parse','--abbrev-ref','HEAD')=='mod4v1-lqr-mpc-robust'
 save('CAPTURE_MINIMUM.json',dict(status='SAVED_ONLY_PREFIX_CLOSURE_COMPLETE_WAIT_INDEX',source_snapshot_files=798,source_snapshot_bytes=sum(x['bytes']for x in rows),source_snapshot_identity_verified=798,prior_Git_refs=len(refs),raw_metadata_paths=len(raw),historical_version_gap_claims=len(gaps),excluded_context_claims=len(excludedrefs),new_physical_cases=2,controls=381,physics_steps=7620,complete0=2,formalFalse=2,current_parent=H,original_capture_calls=1,failed_original_schema_reader_preserved=True,saved_only_closure_calls=1,original_source_refresh=0,raw_payload_opens=0,raw_payload_hashes=0,original_helper_calls=0,Git_mutations=0,ARM_model_PHY_QA_Goal_agents=0,ready_for_record=False))
 lines=['# PH11 SOURCE_ONLY：closed V4/V5 + geometry + C7..C17，待父snapshot审查','',
 '- FINAL有限14根+23根文件+2个既有case/batch；925根内文件，全部967预列路径无lookupmissing，ALL activeV6/V7/C18/future排除，不读取其新249数据或后续handoff。',
 '- 已存798份text原字节/17739938B（794直接+4个索引exactSHA小依赖），本NEW saved-close逐份校验与首次captured source-before SHA/size一致；798未覆写。原live source完整afterSHA核验未到达且本轮未重读，明确不是fresh sourceafter证明。',
 f'- 复用PH10已commit元数据与saved bounded Git tree：{len(refs)}个exact prior refs，raw/binary仅{len(raw)}路径producer记录/初始stat，archive raw/lib/obj/axf/ZIP/USD payload open/hash全0。',
 f'- 声明历史version gap claims={len(gaps)}保原路径/期望SHA/producer/UNKNOWN，不替换当前文件或重建历史；原PH10 419known/4unknown与raw/readable独立身份保留，C16后来165SHA不回写其unknown。',
 '- 原capture一次metadata收尾错用proposed_gate.passed：首次copy后assert1，collector错误非robot异常。原源码/完整合并stderr/798 prefix元数据rawbytes已归revisions/capture_attempt_01；NEW saved reader必需startup_stand_original_v1_gate，exact bool False，不伪造字段。',
 '- saved两case193/3860与188/3760，381/7620、completeFalse/formalFalse/softwareFalse/noBALANCE，与父Expected六来源SHA逐项一致；旧V1 ERROR601/12020无result不回填。',
 '- 累计上下文6attempt2482/49640，五formalFalse+一ERROR；passive3/12000另列，不当独立0/6资格率。新V6父并行活动不属于此数，不声称全session无PHY。',
 '- target unique162C=1/39/122分段AC5u6，不是clean/u4UV重现；oneASM/onearmlink rc0，AXF629048仅既有producer/a707...；原Stage1/MF9025/MOD4UNBOUND，不是C3/startup/power/sole-send/HW/ISR/WCET资格。',
 '- ROM118512/RW66352只是选定map，C17原report/receipt已交后closingfailure事件cause UNKNOWN；不重map/原算法/测试/链接。所有FALSE gate/negativefixture/encoding/failure修订链保留。',
 '- ownrepo/mod4v1-lqr-mpc-robust父仍e176d2a6401fafb9d618a042acba8190023c3273；原helper b2fd15只读SHA，不执行；Git仅own只读metadata、无index mutation/stage/record/commit/tag/push/remote/credentials/hooks。',
 '- 新registry/manifest/identity/gaps/operation cover以saved素材生成；INDEX另封，SourceOnly不是record许可或Goal完成。父独立少量snapshot数值/source审查后才另准recorder。PH11pending，PH10不重做。']
 with(D/'REVIEW_HANDOFF.md').open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(lines)+'\n')
 save('SOURCE_PREPARATION_RECEIPT.json',dict(status='SAVED_SOURCE_PREFIX_BYTEIDENTITY_READY_FOR_PARENT_REVIEW_NO_RECORD',source_snapshot_files=798,source_snapshot_bytes=17739938,exact_prior_Git_refs=len(refs),raw_metadata_paths=len(raw),historical_version_gap_claims=len(gaps),source_snapshot798_byteidentity=True,original_live_after_payload_recheck=False,original_source_refresh=False,source_changes_claim='No snapshot changes; originalafter fullSHA unavailable/unreopened, not assertedfresh',original_capture_metadata_schema_error_preserved=True,saved_only_close_used=True,small_parent_case_inputs6_SHA_equal=True,new_cases2_controls381_steps7620=True,passive12000_separate=True,old_ERRORnoresult_preserved=True,target_link1_rc0_bytes629048_notC3orHW=True,current_own_HEAD=H,original_helper_b2fd15_only_read=True,Git_mutations=0,ARM_native_model_PHY_QA_agents_Goal_raw_payload_opens_or_hashes=0,helper_or_case_or_map_reruns=0,ALL_V6_V7_C18_excluded=True,index_pending_separate_saved_metadata_seal=True,artifacts=[rec(D/n)for n in ['REVIEW_HANDOFF.md','CAPTURE_MINIMUM.json','SOURCE_MANIFEST.json','CASE_AND_TARGET_REGISTRY.json','FAILURE_ENCODING_GAPS_EXCLUSIONS.json','SOURCE_SNAPSHOT_IDENTITY_PINS.json','OPERATION_COVER_TWO_CASE_AND_SAVED_CLOSURE.json']],ready_for_record=False))
 print(json.dumps(dict(status='SAVED_PREFIX_CLOSURE_PASS',copied_text=798,bytes=17739938,prior_refs=len(refs),raw_metadata=len(raw),version_gap_claims=len(gaps),source_refresh=0,raw_payload=0,physical_cases=2,controls=381,physics_steps=7620,REVIEW_HANDOFF=rec(D/'REVIEW_HANDOFF.md')),ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/'SAVED_CLOSURE_FIRST_STOP.json'
  if not p.exists():save('SAVED_CLOSURE_FIRST_STOP.json',dict(status='STOPPED_NEW_SAVED_CLOSURE_NO_AUTOFIX',error=traceback.format_exc(),original_source_or_raw_refresh=0,Gitmutation=0))
  raise
