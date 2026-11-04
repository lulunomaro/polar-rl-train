"""ONE finite PH11 SOURCE capture; no original helper, robot code, binary/raw body, compiler, solver or Git mutation."""
from pathlib import Path
import collections,hashlib,json,ntpath,os,re,subprocess,traceback
D=Path(__file__).resolve().parent;W=D.parents[2];R=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102');OLD=R.parent/'traditional_control_20261101';H='e176d2a6401fafb9d618a042acba8190023c3273'
P10=W/'history/experiments/mod4v1_robust_traditional_phase10_SOURCE_PREPARATION';S=R/'ARCHIVE_PHASE11_V5_FIRST_LINK_V17_CUTOFF_FINAL.json'
RAW_EXT={'.o','.obj','.a','.lib','.exe','.axf','.elfbin','.elf','.bin','.hex','.zip','.7z','.gz','.usd','.usda','.usdc','.stl','.objmesh','.npy','.npz','.pt','.pth','.onnx','.png','.jpg','.jpeg','.pdf','.mp4'}
TEXT_EXT={'.md','.py','.json','.log','.jsonl','.patch','.txt','.sct','.via','.c','.h','.s','.asm','.rst','.csv','.yaml','.yml','.xml','.ioc','.uvprojx','.xsd','.ini'}
SHA=re.compile(r'^[0-9a-fA-F]{64}$');ABS=re.compile(r'^[A-Za-z]:[\\/]')
rows=[];rawrows={};docs=[];gaps=[];claims=[];before=[];counts=collections.Counter()
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=sha(b))
def load(p):return json.loads(p.read_bytes())
def save(n,v):
 with(D/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def norm(p):return ntpath.normcase(ntpath.normpath(str(p)))  # Lexical only: never resolve/stat excluded activeV6, originalZIP or external evidence paths.
def active(p):
 s=str(p).replace('\\','/');return bool(re.search(r'STARTUP_STAND_V6|body_crouch_v6|run_startup_stand_case_v8|CONTINUATION_V6_|MOD4_DEPLOYMENT_[^/]*_V(?:1[89]|[2-9][0-9])(?:/|$)',s,re.I))
def forbidden(p):
 s=str(p).replace('\\','/').lower();return '/xwechat_files/'in s or '/.git/'in s or any(x in s for x in ['/credentials/','/expert/','/canonical/','/checkpoints/'])
def israw(p):return p.suffix.lower()in RAW_EXT or p.name.lower()in('trace.jsonl','physics.jsonl')or '/MODEL_AUDIT/'in p.as_posix()or p.name=='mod4v1_usd_source_aligned.xml'
def git(label,*args):
 env=dict(os.environ);env['GIT_OPTIONAL_LOCKS']='0';out=D/(label+'.stdout.txt');err=D/(label+'.stderr.txt')
 with(D/'GIT_READONLY_LEDGER.jsonl').open('a',encoding='utf-8')as f:f.write(json.dumps(dict(event='reserved',label=label,argv=['git','-C',str(W),*args],allowed_readonly=True,index_mutations=False))+'\n')
 with out.open('xb')as o,err.open('xb')as e:q=subprocess.run(['git','-C',str(W),*args],stdin=subprocess.DEVNULL,stdout=o,stderr=e,env=env)
 with(D/'GIT_READONLY_LEDGER.jsonl').open('a',encoding='utf-8')as f:f.write(json.dumps(dict(event='returned',label=label,rc=q.returncode,stdout=rec(out),stderr=rec(err)))+'\n')
 if q.returncode:raise RuntimeError('ReadonlyGit metadata failure:'+label)
 return out.read_bytes()
def capture(p,relative,reason):
 p=Path(p);assert not active(p)and not forbidden(p)and not israw(p)and p.suffix.lower()in TEXT_EXT
 st=p.stat();assert st.st_size<=16*1024*1024,'Bounded text metadata exceeded; no widening'
 b=p.read_bytes();counts['selected_text_reads']+=1;h=sha(b);dst=D/'snapshot'/relative
 if p.suffix.lower()=='.jsonl':dst=Path(str(dst)+'.txt')
 assert dst.resolve().is_relative_to((D/'snapshot').resolve());dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('xb')as f:f.write(b)
 enc='utf-8';readable=None;decode_error=None
 try:readable=b.decode('utf-8-sig');enc='utf-8-sig'if b.startswith(b'\xef\xbb\xbf')else'utf-8'
 except UnicodeDecodeError as ex:enc='UNRESOLVED_ORIGINAL_BYTES_NOT_TRANSCODED';decode_error=str(ex);gaps.append(dict(kind='selected_text_encoding_unresolved',path=str(p),source_SHA=h,error=decode_error,original_snapshot=str(dst),not_binary_body=True))
 x=dict(path=str(p),source_relative=relative,bytes=len(b),mtime_ns=st.st_mtime_ns,kind='new_full_text_exact_bytes',source_SHA=h,snapshot_path=dst.relative_to(W).as_posix(),snapshot_SHA=rec(dst)['SHA'],selection_reason=reason,encoding=enc,readable_UTF8_SHA=None if readable is None else sha(readable.encode('utf-8')),original_vs_readable_identity_separate=True)
 assert x['snapshot_SHA']==h;rows.append(x);before.append(dict(path=str(p),bytes=len(b),SHA=h,mtime_ns=st.st_mtime_ns));counts['snapshot_files']+=1;counts['snapshot_bytes']+=len(b)
 if p.suffix.lower()=='.json'and readable is not None:
  try:docs.append((p,json.loads(readable)))
  except json.JSONDecodeError as ex:gaps.append(dict(kind='existing_JSON_decode_failure_preserved_not_fixed',path=str(p),error=str(ex)))
 return x

def walker(v,loc='$'):
 stack=[(v,loc)];nodes=0
 while stack:
  v,where=stack.pop();nodes+=1
  if nodes>3000000:raise RuntimeError('metadata walker capacity stop')
  if isinstance(v,dict):
   hh=[]
   for k in ['SHA','sha','SHA256','sha256','source_SHA','raw_SHA','expected_SHA','snapshot_SHA','hash']:
    z=v.get(k)
    if isinstance(z,str)and SHA.fullmatch(z):hh.append(z.lower())
    elif isinstance(z,list):hh.extend(a.lower()for a in z if isinstance(a,str)and SHA.fullmatch(a))
   if isinstance(v.get('source_pin'),dict):
    z=v['source_pin'].get('SHA')
    if isinstance(z,str)and SHA.fullmatch(z):hh.append(z.lower())
   for k in ['path','source','source_path','source_absolute','source_absolute_path','file_path','output_object','object_path','filename','artifact']:
    a=v.get(k)
    if isinstance(a,str)and ABS.match(a):yield a,sorted(set(hh)),where+'.'+k,v.get('bytes',v.get('size'))
   for k,z in v.items():
    if isinstance(k,str)and ABS.match(k)and isinstance(z,str)and SHA.fullmatch(z):yield k,[z.lower()],where+'.<path_key>',None
    if isinstance(z,(dict,list)):stack.append((z,where+'.'+str(k)))
  elif isinstance(v,list):stack.extend((x,where+'['+str(i)+']')for i,x in enumerate(v)if isinstance(x,(dict,list)))

def rawmeta(p,hs,producer,loc,byteclaim=None,why='producer_raw_metadata_only'):
 k=norm(p);x=rawrows.setdefault(k,dict(path=str(p),kind='raw_metadata_only',content_opened=False,SHA_recomputed=False,producer_claims=[],stat=None))
 item=dict(SHA=hs,producer=str(producer),location=loc,producer_bytes=byteclaim)
 if item not in x['producer_claims']:x['producer_claims'].append(item)
 if x['stat']is None and Path(p).is_relative_to(R)and not active(p)and not forbidden(p):
  try:s=Path(p).stat();x['stat']=dict(bytes=s.st_size,mtime_ns=s.st_mtime_ns)
  except FileNotFoundError:x['stat']=dict(exists=False)
 return x

def main():
 assert not(D/'SOURCE_MANIFEST.json').exists()and not(D/'snapshot').exists(),'Immutable first capture, never refresh'
 fs=load(D/'FILESET_ALLOWLIST.json');scope=load(S);prior=load(P10/'FINAL_SOURCE_MANIFEST.json');priorpins=load(D/'PRIOR_CONTEXT_PINS.json')
 assert git('git06_capture_head','rev-parse','HEAD').decode().strip()==H
 save('CAPTURE_STARTED.json',dict(status='NEW_SOURCE_CAPTURE_ENTERED_ONCE',allowlist=rec(D/'FILESET_ALLOWLIST.json'),scope=rec(S),raw_payload_opens=0,raw_payload_hashes=0,old_helper_exec=0))
 # First read/copy ONLY classified text. No payload read of173binary/raw rows.
 for f in fs['files']:
  p=Path(f['path']);s=p.stat();assert s.st_size==f['bytes']and s.st_mtime_ns==f['mtime_ns'],('STOP source drift since finiteallowlist',str(p))
  if israw(p):rawmeta(p,[],S,'finiteallowlist',f['bytes']);continue
  capture(p,f['relative'],f['reason'])
 # Closed JSON producers supply actual prior identities, including C16's165 currentlink inputs.
 for p,obj in docs:
  for path,hs,loc,sz in walker(obj):claims.append(dict(path=path,SHAs=hs,producer=str(p),location=loc,bytes=sz))
 # Exact prior snapshot lookup: no oldsource payload recapture or PH10 preparer.
 prior_by_path=collections.defaultdict(list);prior_versions={};prior_snap={}
 for e in prior['entries']:
  prior_by_path[norm(e['path'])].append(e)
  if e.get('snapshot_path'):prior_snap[e['snapshot_path']]=e
  for tag in [e.get('source_SHA'),e.get('snapshot_SHA')]:
   if isinstance(tag,str)and SHA.fullmatch(tag):prior_versions[(norm(e['path']),tag)]=e
 for e in prior['source_version_claims_resolved']:
  if e.get('snapshot_path')and isinstance(e.get('expected_SHA'),str):prior_versions[(norm(e['path']),e['expected_SHA'])]=dict(path=e['path'],source_SHA=e['expected_SHA'],snapshot_SHA=e['expected_SHA'],snapshot_path=e['snapshot_path'],kind='PH10_resolved_historical_claim',prior_commit=H,resolution=e['resolution'])
 prefixes=sorted({P10.relative_to(W).as_posix()}|{Path(e['path']).parent.relative_to(W).as_posix()for e in prior['prior_references']})
 treebytes=git('git07_prior_bounded_tree','ls-tree','-r','-l','-z',H,'--',*prefixes);treemap={}
 for line in treebytes.split(b'\0'):
  if not line:continue
  a,n=line.split(b'\t',1);mode,typ,oid,sz=a.decode('ascii').split()
  if typ=='blob':treemap[n.decode('utf-8')]=dict(mode=mode,blob_oid=oid,bytes=int(sz))
 snap_by_path={norm(x['path']):x for x in rows};snap_by_sha=collections.defaultdict(list)
 for x in rows:snap_by_sha[x['source_SHA']].append(x)
 refs=[];versions=[];excluded=[];deps=[];seen=set();cursor=0
 def priorref(e,claim):
  rp=e.get('snapshot_path')
  if not rp or rp not in treemap:return None
  t=treemap[rp];return dict(path=claim['path'],expected_source_SHA=claim['SHA'],source_relative=e.get('source_relative'),kind='exact_prior_Git_reference',prior_commit=H,historical_prior_commit=e.get('prior_commit'),repo_path=rp,Git_blob_oid=t['blob_oid'],archived_bytes=t['bytes'],prior_source_SHA=e.get('source_SHA'),prior_readable_or_original_snapshot_SHA=e.get('snapshot_SHA'),prior_encoding=e.get('encoding',e.get('source_encoding')),prior_manifest=rec(P10/'FINAL_SOURCE_MANIFEST.json')if False else priorpins['PH10_manifest'],identity_basis='PreviouslycommittedPH10source/sourceversionmetadata+actualHEADtreeOID; no fresh priorblob or originalsource bodyhash',producer=claim['producer'],location=claim['location'])
 while cursor<len(claims):
  q=claims[cursor];cursor+=1;p=Path(q['path']);k=norm(p)
  for h in q['SHAs']or[None]:
   ident=(k,h)
   if ident in seen:continue
   seen.add(ident);cl=dict(path=str(p),SHA=h,producer=q['producer'],location=q['location'])
   if active(p)or forbidden(p):excluded.append(dict(**cl,reason='declared_excluded_activeV6_future_or_unrelated_context_not_missing_original'));continue
   if israw(p):rawmeta(p,[]if h is None else[h],q['producer'],q['location'],q['bytes']);continue
   if k in snap_by_path and (h is None or h==snap_by_path[k]['source_SHA']):versions.append(dict(**cl,resolution='selected_closed_epoch_exact_snapshot',snapshot_path=snap_by_path[k]['snapshot_path']));continue
   e=prior_versions.get((k,h))if h else next((a for a in prior_by_path[k]if a.get('snapshot_path')),None)
   ref=priorref(e,cl)if e else None
   if ref:refs.append(ref);versions.append(dict(**cl,resolution='exact_prior_Git_version',repo_path=ref['repo_path']));continue
   if h in snap_by_sha:versions.append(dict(**cl,resolution='exact_saved_content_digest_version',snapshot_path=snap_by_sha[h][0]['snapshot_path'],pathname_identity_not_assumed=True));continue
   if e and e.get('kind')=='raw_metadata_only':rawmeta(p,[]if h is None else[h],q['producer'],q['location'],q['bytes']);continue
   if not(p.is_relative_to(R)or p.is_relative_to(OLD)):
    excluded.append(dict(**cl,reason='external_tool_primary_web_temp_or_other_context_reference_only_no_payload_or_stat'));continue
   # Current source indices can admit only ONE exact SHA-pinned bounded small text dependency, not a directory sweep.
   if h and p.suffix.lower()in TEXT_EXT and p.is_file()and p.stat().st_size<2*1024*1024:
    assert len(deps)<256 and sum(x['bytes']for x in deps)<8*1024*1024,'Extra exactsmall dependency capacity stop'
    b=p.read_bytes();counts['dependency_pin_reads']+=1
    if sha(b)==h:
     rel='@dependencies/'+('task/'+p.relative_to(R).as_posix()if p.is_relative_to(R)else'oldpublic/'+p.relative_to(OLD).as_posix())
     x=capture(p,rel,'exact_bounded_dependency_index_SHA_match');deps.append(x);snap_by_path[k]=x;snap_by_sha[x['source_SHA']].append(x);versions.append(dict(**cl,resolution='explicit_current_exact_bounded_dependency_snapshot',snapshot_path=x['snapshot_path']))
     if p.suffix.lower()=='.json':
      ob=docs[-1][1]
      for pp,hh,ll,ss in walker(ob):claims.append(dict(path=pp,SHAs=hh,producer=str(p),location=ll,bytes=ss))
     continue
   # Historical gaps remain preserved; not relabelled sourcecorruption or filled with currentfiles.
   historical=next((e for e in prior['source_version_claims_resolved']if norm(e['path'])==k and e.get('expected_SHA')==h),None)
   if historical:gaps.append(dict(**cl,kind='historical_PH10_version_gap_or_reference_preserved',prior_resolution=historical.get('resolution')));continue
   if h and p.suffix.lower()in TEXT_EXT:gaps.append(dict(**cl,kind='UNRESOLVED_EXACT_SMALL_TEXT_VERSION',current_version_not_substituted=True))
   else:excluded.append(dict(**cl,reason='unqualified_path_or_no_version_claim_context_only'))
 # Mandatory unresolved new version -> preserve partial but no READY index.
 bad=[x for x in gaps if x.get('kind')=='UNRESOLVED_EXACT_SMALL_TEXT_VERSION']
 # Metadata-only reconciliations, never old/new physics/raw/model execution.
 case_rows=[]
 for name,expected_n,expected_steps in zip(scope['new_physical_registry']['ids'],scope['new_physical_registry']['controls'],scope['new_physical_registry']['physics_steps']):
  result=next(o for p,o in docs if p==R/'results'/name/'result.json');batch=next(o for p,o in docs if p==R/'batches'/name/'BATCH_RESULT.json')
  gate=result.get('proposed_gate',{});assert result['controls']==expected_n and result['physics_steps']==expected_steps and result['complete']is False and gate.get('passed')is False
  case_rows.append(dict(id=name,controls=expected_n,physics_steps=expected_steps,complete=False,original_formal_gate=False,stop=result['stop'],first_BALANCE=result.get('first_balance_s'),software_failure=batch['software_failure'],raw_payload_not_opened=True))
 assert sum(x['controls']for x in case_rows)==381 and sum(x['physics_steps']for x in case_rows)==7620 and all(x['software_failure']is False for x in case_rows)
 c16=next(o for p,o in docs if p==R/'MOD4_DEPLOYMENT_FIRST_LINK_V16/CURRENT_INPUT_IDENTITIES.json');assert c16['objects']==163 and c16['opaque_user_libs']==2 and c16['current_payload_hashes']==len(c16['records'])==165
 after=[]
 for x in before:
  p=Path(x['path']);now=rec(p);s=p.stat();after.append(now);assert now['SHA']==x['SHA']and now['bytes']==x['bytes']and s.st_mtime_ns==x['mtime_ns'],('STOP source changed, initial snapshot retained',x['path'])
 assert git('git08_final_head','rev-parse','HEAD').decode().strip()==H
 # Freeze complete metadata prior to prose/index; raw bodies remain zero.
 save('SOURCE_MANIFEST.json',dict(status='PH11_FINITE_SOURCE_CAPTURE_COMPLETE_PENDING_GAP_REVIEW_NOT_RECORD',scope=rec(S),entries=rows,prior_Git_references=refs,raw_metadata_only=list(rawrows.values()),source_version_claims=versions,summary=dict(counts,exact_prior_Git_refs=len(refs),raw_metadata_paths=len(rawrows),excluded_context_paths=len(excluded),unresolved_new_text_versions=len(bad)),raw_payload_opens=0,raw_payload_hashes=0,Git_mutations=0,old_helper_execution=0))
 save('SOURCE_BEFORE_AFTER_PINS.json',dict(before=before,after=after,all_equal=True,no_refresh=True,raw_bodies_not_read=True))
 save('FAILURE_ENCODING_GAPS_EXCLUSIONS.json',dict(gaps=gaps,declared_exclusions=scope['explicit_exclusions'],excluded_references=excluded,prior_PH10_historical_gaps=priorpins['prior_summary'],prior4_raw_unknowns_not_rewritten=True,C16_current165_identity_claims_supplemental_only=True,C17_closing_failure=dict(event='Parentreported workerclosingfailure afterreport/receiptdelivery',cause='UNKNOWN',map_reexecution=False),negativefixtures_are_preserved_test_inputs_not_corruption=True))
 save('CASE_AND_TARGET_REGISTRY.json',dict(new_physical=case_rows,new_total=dict(controls=381,physics_steps=7620,formalFalse=2,complete0=2,original_gate_true=0),cumulative_context=scope['cumulative_context'],prior_V1_ERROR_no_result_backfill=True,passive_separate=dict(cases=3,steps=12000),qualification_rate_not_inferred=True,target=dict(unique_C_sources=162,segmented_successes=[1,39,122],not_clean_build=True,AC5u6_variant_not_u4repro=True,ASM_native=1,actual_first_link=1,AXF_bytes=629048,current_input_metadata=c16,not_C3_integration_or_runtime_or_hardware=True),geometry=dict(modelcompile=1,forward=9,PHY_steps=0,not_dynamic=True),ALL_active_V6_excluded=True,archiveworker_new_PHY=0,parallel_parent_V6_not_whole_session_zero=True))
 save('CAPTURE_MINIMUM.json',dict(status='HOLD_NEW_VERSION_GAPS'if bad else'SOURCE_CAPTURE_READY_FOR_SAVED_CLOSURE',selected_text_files=len(rows),text_bytes=sum(x['bytes']for x in rows),prior_references=len(refs),raw_metadata_paths=len(rawrows),unresolved_new_version_count=len(bad),unresolved_new_versions=bad,source_before_after_equal=True,parent_unchanged=H,raw_payload_opens=0,raw_payload_hashes=0,Git_mutations=0,ARM_model_PHY_QA_Goal=0))
 print(json.dumps(dict(status='HOLD_NEW_VERSION_GAPS'if bad else'SOURCE_CAPTURE_SUCCESS',text=len(rows),text_bytes=sum(x['bytes']for x in rows),prior_Git=len(refs),raw_metadata_paths=len(rawrows),unresolved_new_versions=bad,source_before_after_equal=True),ensure_ascii=False))
 if bad:raise SystemExit(1)
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/'CAPTURE_FIRST_STOP.json'
  if not p.exists():save('CAPTURE_FIRST_STOP.json',dict(status='STOPPED_PRESERVE_FIRST_SOURCE_CAPTURE_PREFIX',error=traceback.format_exc(),counts=dict(counts),copied_text_records=rows,raw_payload_opens=0,raw_payload_hashes=0,Git_mutations=0,no_auto_refresh_or_retry=True))
  raise
