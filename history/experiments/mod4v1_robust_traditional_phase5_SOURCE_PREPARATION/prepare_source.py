"""PH5 bounded source snapshot only. No Git, experiments, raw digests or source edits."""
from pathlib import Path
import ast,collections,datetime,fnmatch,hashlib,json,re,sys,traceback
S=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102');WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');P=Path(__file__).resolve().parent;PROJECT=S.parent
sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
HEX=re.compile(r'^[0-9a-fA-F]{64}$');ROUND=re.compile(r'(?<![a-z0-9])r(\d{2})(?=[^0-9]|$)',re.I)
TEXT={'.py','.c','.h','.cc','.cpp','.hpp','.md','.json','.txt','.log','.csv','.tsv','.xml','.urdf','.yml','.yaml','.toml','.ini','.ps1','.sh','.bat','.cmd','.cmake','.mk','.map','.lst','.asm','.s','.def','.d','.diff','.patch','.html','.svg','.sha256','.macros','.in'}
RAW={'.jsonl','.npz','.npy','.usd','.usda','.usdc','.stl','.stp','.step','.zip','.gz','.tar','.7z','.exe','.dll','.o','.obj','.lib','.a','.bin','.elf','.pt','.pth','.onnx','.png','.jpg','.jpeg','.webp','.gif','.pdf','.mp4','.raw','.dat','.f32','.f64'}
PRIOR=[('mod4v1_robust_traditional_phase1/manifest.json','93e0814f5d4dc165dda1f85f8ee12bc35be04d2f'),('mod4v1_robust_traditional_phase2/manifest.json','02b5ff84b905a4e40f207a44b0491aeff2f79b7e'),('mod4v1_robust_traditional_phase3_SOURCE_PREPARATION/FINAL_SOURCE_MANIFEST.json','fa6838807f4d69d2b8ac52300d74ad40f365d2ed'),('mod4v1_robust_traditional_phase4_SOURCE_PREPARATION/FINAL_SOURCE_MANIFEST.json','db8fd0606e00a450504853181a6b4cdf66869d68')]
NOW=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sh(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def safe(x):
 if isinstance(x,dict):return {k:safe(v)for k,v in x.items()}
 if isinstance(x,list):return [safe(v)for v in x]
 if isinstance(x,float)and not __import__('math').isfinite(x):return {'nonfinite_original':str(x),'source_bytes_retained':True}
 return x
def new(p,x):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(safe(x),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def relative(p):
 if p.is_relative_to(S):return p.relative_to(S).as_posix()
 if p.is_relative_to(WT):return '@repo/'+p.relative_to(WT).as_posix()
 if p.is_relative_to(PROJECT):return '@project/'+p.relative_to(PROJECT).as_posix()
 return '@external/'+str(p).replace(':','').replace('\\','/')
def metadata(p):
 st=p.stat();return {'path':str(p),'source_relative':relative(p),'bytes':st.st_size,'mtime_ns':st.st_mtime_ns}
def raw_only(p,size):return p.suffix.lower()in RAW or size>10000000 or (p.suffix.lower()not in TEXT and p.name not in ('LICENSE','NOTICE','Makefile','CMakeLists.txt'))
def forbidden(p):
 low=str(p).replace('\\','/').lower()
 if any(t in p.parts for t in ('__pycache__','.git','.venv','node_modules')):return 'runtime_cache'
 if p.name.lower().startswith(('.env','id_rsa','id_ed25519'))or p.suffix.lower()in('.pem','.key','.kdbx'):return 'credential_path'
 if 'pc3_candidate_bundle_v1'in low:return 'active_PC3_candidate_bundle_excluded'
 if any(int(x)>=48 for x in ROUND.findall(low)):return 'R48plus_future_excluded'
 if any(x in low for x in ('moving_hop','movinghop','phase6_pending')):return 'future_movinghop_or_postcut_excluded'
 if p.name.startswith(('~$','.tmp'))or p.suffix.lower()in('.tmp','.temp','.lock'):return 'temporary'
 return None

def main():
 assert not (P/'SOURCE_MANIFEST.json').exists(),'No recapture or overwrite'
 started=NOW();authority_path=S/'PH5_ARCHIVE_CUTOFF_H5.json';authority=load(authority_path);authority_sha=sh(authority_path.read_bytes());assert authority['no_commit_record_tag_push_yet']and authority['no_mtime_blind_selection']
 anchor=S/authority['completion_anchor'];assert sh(anchor.read_bytes())==authority['completion_anchor_SHA']
 old_by_sha=collections.defaultdict(list);old_by_path=collections.defaultdict(set);prior_meta=[]
 for name,commit in PRIOR:
  p=WT/'history/experiments'/name;m=load(p);prior_meta.append({'path':str(p),'SHA':sh(p.read_bytes()),'commit':commit})
  for e in m['entries']:
   h=e.get('source_SHA',e.get('original_sha256'));ap=e.get('snapshot_path',e.get('archive_path'));ah=e.get('snapshot_SHA',e.get('archive_sha256'))
   if h and ap and ah==h:
    ref={'archive_path':ap,'SHA':h,'prior_commit':commit};old_by_sha[h].append(ref)
    path=e.get('path')
    if path:old_by_path[str(Path(path).resolve()).lower()].add(h)
 nodes={};queue=[];exclusions=[];missing=[];claims=collections.defaultdict(list);version_claims=[];documents=[];case_sets={};batch_payloads=[];explicit_roots={};parse_events=[];changes=[];redactions=0
 modules=[(S/x).resolve()for x in authority['include_task_trees']];root_names={authority_path.name}
 def exclude(p,why,producer=None):exclusions.append({'path':str(p),'reason':why,'producer':producer,'not_read_or_traversed':True})
 def add(p,reason,expected=None,producer=None,explicit=False):
  p=Path(p).resolve();bad=forbidden(p)
  if bad:exclude(p,bad,producer);return
  if not p.is_relative_to(PROJECT):missing.append({'path':str(p),'reason':'outside_project_not_read','producer':producer,'expected_SHA':expected});return
  if p.parent==S and p.name.startswith('CONTINUATION')and p.name not in root_names:exclude(p,'continuation_not_named_by_written_cutoff',producer);return
  key=str(p).lower()
  if expected and HEX.fullmatch(str(expected)):version_claims.append({'path':str(p),'expected_SHA':expected.lower(),'producer':producer})
  if key not in nodes:nodes[key]={'path':p,'reasons':set(),'expected':set(),'producers':set(),'explicit':False};queue.append(key)
  n=nodes[key];n['reasons'].add(reason);n['explicit']|=explicit
  if expected and HEX.fullmatch(str(expected)):n['expected'].add(expected.lower())
  if producer:n['producers'].add(str(producer))
  if p.parent==S:explicit_roots[key]=n
 def tree(p,why):
  p=Path(p)
  if not p.exists():missing.append({'path':str(p),'reason':'explicit_tree_absent'});return
  for x in sorted(p.rglob('*')):
   if x.is_file()and not x.is_symlink():add(x,why,explicit=True)
 def resolve(value,producer):
  if not isinstance(value,str)or not value or '://'in value:return None
  value=value.split('#')[0];p=Path(value)
  if p.is_absolute():return p.resolve()
  options=[producer.parent/p,S/p,producer.parent/'sources'/p]
  for x in options:
   if x.exists():return x.resolve()
  return (S/p).resolve()
 def walk(obj,p,loc='$',context=False):
  if isinstance(obj,list):
   for i,x in enumerate(obj):walk(x,p,f'{loc}[{i}]',context)
  elif isinstance(obj,dict):
   if p.name=='PACKAGE_MANIFEST.json'and(loc.startswith('$.files')or loc.startswith('$.omitted')):return
   h=next((obj[k].lower()for k in ('SHA','sha256','SHA256','sha','source_SHA','original_sha256','producer_SHA','output_sha256')if isinstance(obj.get(k),str)and HEX.fullmatch(obj[k])),None)
   vals=[obj[k]for k in ('object','object_path')if isinstance(obj.get(k),str)]if h and any(isinstance(obj.get(k),str)for k in ('object','object_path'))else[obj[k]for k in ('path','file','source_path','source','source_file','artifact','output','original_path','npz_path','raw_path')if isinstance(obj.get(k),str)]
   for value in vals:
    target=resolve(value,p)
    if target is None:continue
    if h:
     claims[str(target).lower()].append({'SHA':h,'producer':str(p),'location':loc,'producer_bytes':obj.get('bytes',obj.get('size_bytes'))})
     if context:add(target,'actual_provenance_SHA_dependency',h,str(p))
   if isinstance(obj.get('source_SHA'),str)and HEX.fullmatch(obj['source_SHA'])and isinstance(obj.get('source'),str):add(resolve(obj['source'],p),'explicit_source_SHA',obj['source_SHA'],str(p))
   for k,v in obj.items():
    if HEX.fullmatch(v)if isinstance(v,str)else False:
     if '/'in k or '\\'in k:
      target=resolve(k,p)
      if target:
       claims[str(target).lower()].append({'SHA':v.lower(),'producer':str(p),'location':loc+'.'+k,'producer_bytes':None})
       if context:add(target,'named_provenance_SHA',v,str(p))
    walk(v,p,loc+'.'+k,context or k in ('files','sources','source_files','source_before_physics','runner_sources_before_physics','source_hashes','source_and_evidence_sha256','frozen_source','source_closure','seal_anchors_verified'))
 # Explicit root patterns and reports are exact namespace admissions, not mtimes.
 for x in S.iterdir():
  if x.is_file()and any(fnmatch.fnmatchcase(x.name,pat)for pat in authority['root_allowlist_patterns']):root_names.add(x.name)
 for name in sorted(root_names):add(S/name,'written_root_allowlist',explicit=True)
 for module in modules:tree(module,'written_named_component_tree')
 for x in (S/'reports').iterdir():
  if x.is_file()and any(fnmatch.fnmatchcase(x.name,pat)for pat in authority['include_report_patterns']):add(x,'written_report_allowlist',explicit=True)
 for b in sorted((S/'batches').iterdir()):
  if not b.is_dir()or not any(fnmatch.fnmatchcase(b.name,pat)for pat in authority['include_batch_patterns']):continue
  prot=b/'PROTOCOL.json';payload=load(prot);names=payload.get('case_names',[]);assert isinstance(names,list)and len(set(names))==len(names),(b,'protocol case_names')
  br=b/'BATCH_RESULT.json';bp=load(br)if br.exists()else{};listed={x['case']for x in bp.get('rows',[])if'case'in x}
  assert listed<=set(names),(b,'batch case outside protocol');case_sets[b.name]={'protocol_path':str(prot),'protocol_SHA':sh(prot.read_bytes()),'scheduled_case_names':names,'result_cases':sorted(listed),'unstarted':bp.get('unstarted',[])};batch_payloads.append({'batch':b.name,'payload':safe(bp)})
  tree(b,'closed_batch_protocol_and_saved_failures')
  for case in names:
   if case in set(nodes):pass
   target=S/'results'/case
   if target.exists():tree(target,'only_protocol_listed_case')
   else:missing.append({'path':str(target),'reason':'protocol_listed_case_not_saved_or_unstarted','batch':b.name,'listed_executed':case in listed})
 prior_receipt=WT/authority['include_prior_postcommit_receipt'];add(prior_receipt,'written_prior_postcommit_receipt',explicit=True)
 entries=[];by_text_sha=collections.defaultdict(list)
 for key in queue:
  n=nodes[key];p=n['path']
  if not p.is_file():missing.append({'path':str(p),'reason':'named_dependency_absent','expected_SHA':sorted(n['expected']),'producers':sorted(n['producers'])});continue
  st=p.stat();e={**metadata(p),'selection_reasons':sorted(n['reasons']),'expected_SHA':sorted(n['expected']),'producers':sorted(n['producers']),'source_SHA':None,'snapshot_path':None,'snapshot_SHA':None,'kind':None}
  if raw_only(p,st.st_size):e.update(kind='raw_metadata_only',content_read=False);entries.append(e);continue
  if p.is_relative_to(WT)and p!=prior_receipt:
   # Existing Git history is a reference leaf, never recursively parsed as a
   # TASK-root namespace or cloned into another broad archive closure.
   raw=p.read_bytes();h=sh(raw);e.update(source_SHA=h,snapshot_SHA=h,snapshot_path=p.relative_to(WT).as_posix(),kind='existing_repository_reference',prior_commit='db8fd0606e00a450504853181a6b4cdf66869d68');entries.append(e);by_text_sha[h].append(e);continue
  raw=p.read_bytes()
  if (st.st_size,st.st_mtime_ns)!=(p.stat().st_size,p.stat().st_mtime_ns):changes.append({'path':str(p),'phase':'during_read_not_captured'});continue
  h=sh(raw);e['source_SHA']=h
  if n['expected']and h not in n['expected']:
   valid=[(wanted,ref)for wanted in n['expected']for ref in old_by_sha.get(wanted,[])]
   if valid:
    wanted,ref=valid[0];assert sh((WT/ref['archive_path']).read_bytes())==wanted;e.update(source_SHA=wanted,snapshot_SHA=wanted,snapshot_path=ref['archive_path'],kind='historical_executed_version_prior_Git_reference',current_different_SHA_not_substituted=h,prior_commit=ref['prior_commit']);entries.append(e);by_text_sha[wanted].append(e);continue
   if p.parent==S:missing.append({'path':str(p),'reason':'current_root_not_expected_executed_version_no_substitution','current_SHA':h,'expected_SHA':sorted(n['expected'])});continue
  try:encoding='utf-16'if raw.startswith((b'\xff\xfe',b'\xfe\xff'))else'utf-8-sig';text=raw.decode(encoding)
  except UnicodeError:
   try:encoding='gb18030';text=raw.decode(encoding)
   except UnicodeError:e.update(kind='undecodable_metadata_only',source_SHA=None,content_read_for_decode_only=True);entries.append(e);continue
  cleaned,count=redact(text);redactions+=count;archived=cleaned.encode('utf-8')if count else raw;ah=sh(archived)
  prior=old_by_sha.get(h,[])if h==ah else[]
  if prior:
   ref=prior[-1];assert sh((WT/ref['archive_path']).read_bytes())==ah;e.update(snapshot_path=ref['archive_path'],snapshot_SHA=ah,kind='prior_same_byte_Git_reference',prior_commit=ref['prior_commit'])
  else:
   dest=P/'snapshot'/e['source_relative'];dest.parent.mkdir(parents=True,exist_ok=True)
   if dest.exists():assert dest.read_bytes()==archived,'Partial prior snapshot differs; preserve for diagnosis'
   else:dest.write_bytes(archived)
   e.update(snapshot_path=dest.relative_to(WT).as_posix(),snapshot_SHA=ah,kind='new_full_text'if not count else'new_redacted_text')
  e.update(redactions=count,encoding=encoding);entries.append(e);by_text_sha[h].append(e)
  if p.suffix.lower()=='.json':
   try:
    obj=json.loads(text);documents.append((p,obj));walk(obj,p,context=any(t in p.name.lower()for t in ('index','manifest','protocol','freeze','receipt','source')))
   except (ValueError,TypeError):parse_events.append({'path':str(p),'original_bytes_saved':True,'error':traceback.format_exc()})
  if p.suffix.lower()=='.py':
   try:
    for x in ast.walk(ast.parse(text)):
     names=[x.module]if isinstance(x,ast.ImportFrom)and x.module else[a.name for a in x.names]if isinstance(x,ast.Import)else[]
     for name in names:
      target=(S/(name.replace('.','/')+'.py')).resolve()
      if target.exists()and str(target).lower()not in nodes:
       expected=old_by_path.get(str(target).lower(),set())
       if expected:add(target,'local_import_earlier_verified_source',sorted(expected)[-1],str(p))
       elif target.name in root_names:add(target,'local_import_explicit_cutoff_root',producer=str(p),explicit=True)
       else:exclude(target,'unbound_import_not_automatically_admitted',str(p))
   except SyntaxError:parse_events.append({'path':str(p),'kind':'original_saved_source_syntax_not_executed','error':traceback.format_exc()})
  if p.suffix.lower()=='.md':
   for value in re.findall(r'\]\(<([^>]+)>\)',text):
    target=resolve(value,p)
    if target is None or target.is_dir():continue
    if target.parent==S and target.name not in root_names:continue
    if target.is_relative_to(WT)or target.is_relative_to(S/'reports')or any(target.is_relative_to(x)for x in modules):add(target,'closed_document_named_file',producer=str(p))
 # Resolve producer hashes without reading any raw bytes.
 for e in entries:
  if e['snapshot_path']:continue
  cc=claims.get(e['path'].lower(),[]);hh=sorted({x['SHA']for x in cc if x['producer_bytes']in(None,e['bytes'])});e['producer_claims']=cc
  if len(hh)==1:e['source_SHA']=hh[0];e['SHA_status']='existing_producer_claim_only_not_rehashed'
  elif len(hh)>1:e['SHA_status']='conflicting_producer_claims_current_unknown'
  else:e['SHA_status']='unknown_no_bound_producerSHA_no_rehash'
 resolved=[];gaps=[]
 for c in version_claims:
  h=c['expected_SHA'];candidate=by_text_sha.get(h,[]);prior=old_by_sha.get(h,[]);raw=next((e for e in entries if e['path'].lower()==c['path'].lower()and e['source_SHA']==h),None)
  if candidate:resolved.append({**c,'resolution':'selected_saved_text_SHA','snapshot_path':candidate[0]['snapshot_path']})
  elif prior:resolved.append({**c,'resolution':'prior_PH1_to_PH4_saved_SHA','reference':prior[-1]})
  elif raw:resolved.append({**c,'resolution':'producer_only_artifact_not_rehashed'})
  else:gaps.append(c)
 records=[];software=[];scheduled={x for b in case_sets.values()for x in b['scheduled_case_names']}
 for p,obj in documents:
  if p.parent.parent==S/'results'and p.parent.name in scheduled and p.name in('result.json','ERROR.json'):
   record={'case':p.parent.name,'path':str(p),'source_SHA':next(e['source_SHA']for e in entries if e['path']==str(p)),'original_payload':safe(obj)}
   (records if p.name=='result.json'else software).append(record)
 verified=0
 for e in entries:
  if e['snapshot_path']:assert sh((WT/e['snapshot_path']).read_bytes())==e['snapshot_SHA'];verified+=1
  st=Path(e['path']).stat()
  if (st.st_size,st.st_mtime_ns)!=(e['bytes'],e['mtime_ns']):changes.append({'path':e['path'],'phase':'postcapture_future_version_not_replaced'})
 assert all(not forbidden(Path(e['path']))for e in entries)
 summary={'source_entries':len(entries),'new_text_copies':sum(e['kind'].startswith('new_')for e in entries),'new_text_bytes':sum((WT/e['snapshot_path']).stat().st_size for e in entries if e['kind'].startswith('new_')),'prior_Git_text_references':sum('reference'in e['kind']for e in entries),'text_SHA_pairs_verified':verified,'raw_metadata_only':sum(not e['snapshot_path']for e in entries),'raw_existing_producerSHA_known':sum(not e['snapshot_path']and e['source_SHA']is not None for e in entries),'root_explicit_allowlist':len(explicit_roots),'protocol_scheduled_unique_cases':len(scheduled),'physical_result_files':len(records),'software_ERROR_files':len(software),'missing_events_initial':len(missing),'unresolved_version_claims_initial':len(gaps),'excluded_paths_or_trees':len(exclusions),'source_changes':len(changes),'redactions':redactions,'new_physics_tests_compile_once_rawhash_Git_agents_GPU_realIO':False}
 scope={'authority_path':str(authority_path),'authority_SHA':authority_sha,'authority':authority,'started_at_utc':started,'ended_at_utc':NOW(),'root_admission':'explicit cutoff patterns plus needed executed/provenance/import/loader closure; no mtime selection','case_admission':'actual protocol case_names plus batch result/unstarted verification; no result-prefix sweep','Goal':'active','parent_review_before_Git':True}
 new(P/'SOURCE_MANIFEST.json',{'scope':scope,'summary':summary,'entries':entries,'source_version_claims_resolved':resolved,'prior_references':prior_meta})
 new(P/'CASE_AND_FAILURE_REGISTRY.json',{'batches':case_sets,'batch_original_payloads':batch_payloads,'physical_results':records,'software_ERROR_records':software,'software_errors_not_robot_zero_ofN':True,'H5_complete_expected64_but_all_failures_preserved':True})
 new(P/'MISSING_AND_EXCLUSIONS.json',{'missing':missing,'unresolved_version_claims':gaps,'source_changes':changes,'original_json_or_syntax_reader_events':parse_events,'exclusions':exclusions,'unknown_raw':[e for e in entries if not e['snapshot_path']and e['source_SHA']is None],'inherited_FSM_old_ERROR_REPORT_SHA_gap':'eea7bbf33028a3abaf697a3ec76c06fefdf53d68c8f551a6b9593fba157f048d; disclose, do not rebuild','postcut_phase6_pending':True})
 new(P/'EXPLICIT_ROOT_ALLOWLIST.json',{'root':str(S),'files':[{'path':str(n['path']),'reasons':sorted(n['reasons']),'expected_SHA':sorted(n['expected'])}for n in explicit_roots.values()],'not_mtime_based':True})
 new(P/'SNAPSHOT_CONSISTENCY_RECEIPT.json',{'status':'LOCAL_PH5_SOURCE_PREPARED_ONLY_WAIT_REVIEW','scope':scope,'summary':summary,'sourceRoot_oldexpertindex_main_helper_modified':False,'record_stage_commit_tag_push_calls':0,'raw_content_rehashes':0,'physics_unit_compile_oldonce_newagents_GPU_realIO':False})
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  n=1
  while(P/f'PREPARATION_FAILURE_{n:03d}.txt').exists():n+=1
  (P/f'PREPARATION_FAILURE_{n:03d}.txt').write_text(traceback.format_exc(),encoding='utf-8');(P/f'PREPARATION_FAILURE_SOURCE_{n:03d}.py').write_bytes(Path(__file__).read_bytes());raise
