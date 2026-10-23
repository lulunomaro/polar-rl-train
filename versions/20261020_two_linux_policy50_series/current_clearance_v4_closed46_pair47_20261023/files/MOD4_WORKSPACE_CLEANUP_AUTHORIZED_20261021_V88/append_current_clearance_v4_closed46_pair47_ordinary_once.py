"""Ordinary V4 follow-up: complete46 pair models, fresh space and pair47 both PPO."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,time,traceback
C=Path(__file__).resolve().parent;W=C.parent;T=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021';S=W/'MOD4_CURRENT_EXPERT_GRADUATION_JUMP_FROZEN_20261021';B=T;R=C/'reports';G=W/'polar-rl-train';ROOT=G/'versions/20261020_two_linux_policy50_series';K=W/'MOD4_STORAGE_WASTE_CLEANUP_SUBAGENTS_AUTHORIZED_20261023';NAME=Path(__file__).stem
H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args,input=None):
 p=subprocess.run(['git','-C',str(G),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').rstrip('\r\n')
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert NAME.endswith('_once') and 'TEMPLATE' not in NAME
 arg=R/sys.argv[1];assert arg.resolve().is_relative_to(R.resolve());cfg=json.loads(arg.read_bytes());assert re.fullmatch('[A-Za-z0-9_]{3,90}',cfg['destination']);assert re.fullmatch('[a-f0-9]{40}',cfg['base_HEAD'])
 P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V46_20261023';N=W/'MOD4_TWO_LINUX_POLICY50_COHORT_53_20261021';proof=json.loads((P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());active=json.loads((B/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V47_20261023/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());native=json.loads((T/'reports/STEP270_NATIVE32_V4_SAVED_ROWS_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['original_canonical_cost_settled'] and active['passed'] and native['passed_saved_rows_execution_CPU']
 assert all(x.resolve().is_relative_to(W.resolve()) for x in (B,P,N));D=ROOT/cfg['destination'];assert git('rev-parse','HEAD')==cfg['base_HEAD'] and not git('status','--porcelain') and not D.exists();tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(tags.splitlines())==1427
 put(R/(NAME+'_STARTED_ACTUAL.json'),dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,configuration=cfg,ordinary_followup_no_training_or_ledger_write=True));prior={};bySHA={};old=G/'versions/20261020_linux4090_return_two50';indexes=[old/'COMPLETE_ALL_SOURCE_REPORT_ERROR_INDEX.json'];indexes+=list(ROOT.rglob('COMPLETE_FILE_CAPTURE_INDEX.json')) if ROOT.exists() else []
 indexes.append(G/'versions/20261022_host72_closed_tasks_cleanup_V112/COMPLETE_CAPTURE_INDEX.json')
 for p in sorted(indexes,key=lambda p:json.loads(p.read_bytes())['epoch']):
  v=json.loads(p.read_bytes())
  for original in v['entries']:
   x=dict(original)
   if 'SHA' not in x and x.get('source_SHA'):x['SHA']=x['source_SHA']
   if x.get('SHA') and x.get('archive'):
    row=dict(x,prior_capture_epoch=v['epoch']);prior[x['path'].casefold()]=row;bySHA[x['SHA']]=row
 supplement=old/'POST_GIT_MONITOR_ORDINARY/SUPPLEMENT_INDEX.json'
 if supplement.exists():
  v=json.loads(supplement.read_bytes())
  for x in v['entries']:
   row=dict(path=x['source'],bytes=x['bytes'],SHA=x['SHA'],archive=x['archive'],archive_SHA=x['SHA'],mode='full',prior_capture_epoch=v['epoch']);prior[row['path'].casefold()]=row;bySHA[row['SHA']]=row
 known={}
 for ip in ROOT.rglob('EXTERNAL_MODEL_ASSET_INDEX.json'):
  for row in json.loads(ip.read_bytes()).get('artifacts',[]):
   if row.get('path') and row.get('SHA'):known[str(Path(row['path']).resolve())]=row['SHA']
 for stage in (T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V32_20261023',T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V35_20261023',T/'H1_STEP270_REWARD_AIRBORNE_TUCK_V3_RESOURCE_V39_20261023'):
  for x in json.loads((stage/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 for x in json.loads((T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V31_20261023/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 diagnostic=T/'H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023'
 for rp in (diagnostic/'reports').glob('*.json'):
  value=json.loads(rp.read_bytes());rows=list(value.get('artifacts',[]))
  if isinstance(value.get('artifact'),dict):rows.append(value['artifact'])
  if value.get('path') and value.get('SHA'):rows.append(value)
  for row in rows:
   if row.get('path') and row.get('SHA') and Path(row['path']).is_file():known[str(Path(row['path']).resolve())]=row['SHA']
 for x in json.loads((T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V30_20261023/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 for x in json.loads((T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V29_20261023/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 for x in json.loads((T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V28_20261023/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 for x in json.loads((T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V27_20261023/reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 for x in json.loads((T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V26_20261023/reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 for x in json.loads((T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V25_20261022/reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 for x in json.loads((T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V24_20261022/reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 for x in json.loads((T/'H1_STEP270_REWARD_BOUNDARY_REPAIR_RESOURCE_V23_20261022/reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 failed_diagnostic=json.loads((T/'H1_STEP270_REWARD_PATH_V1_20261022/reports/V110_FAILED21_DIAGNOSTIC_PREFIX_TWOHOST_SHA_AND_ALL_OUT_ACTUAL.json').read_bytes())['local_prefix'];known[str(Path(failed_diagnostic['local_path']).resolve())]=failed_diagnostic['SHA']
 for x in json.loads((T/'H1_STEP270_REWARD_H1_ONLY_V20_20261022/reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 for rp in (T/'H1_STEP270_REPLAY_DIAG_20261022_V105/reports').glob('*.json'):
  value=json.loads(rp.read_bytes());records=list(value.get('artifacts',[]))
  if isinstance(value.get('artifact'),dict):records.append(value['artifact'])
  if value.get('path') and value.get('SHA'):records.append(value)
  for row in records:
   if row.get('path') and row.get('SHA') and Path(row['path']).is_file():known[str(Path(row['path']).resolve())]=row['SHA']
 for base in (P,B,N,W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021',S,C,K):
  for m in base.rglob('THREE_SLOT_COMPLETE_MANIFEST_V1.json'):
   for x in json.loads(m.read_bytes()).get('files',[]):known[str((m.parent/x['relative']).resolve())]=x['SHA']
 for x in proof['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 for model in json.loads((T/'H1_STEP270_E3_REWARD_PATH_PAIR_V17_20261022/reports/E3_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(model['final']['local_path']).resolve())]=model['final']['SHA']
 for model in json.loads((T/'H1_STEP270_E3_REWARD_PATH_PAIR_V18_20261022/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(model['final']['local_path']).resolve())]=model['final']['SHA']
 for suffix,local in (('', 'shared_H1_native13_actual'),('_V2','shared_H1_native13_V2_actual'),('_V3','shared_H1_native13_V3_actual')):
  rp=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/reports'/('SHARED_H1_NATIVE13'+suffix+'_FINITE_RETURNED_ACTUAL.json')
  if rp.exists():
   for row in json.loads(rp.read_bytes()).get('raw',[]):known[str((W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021'/local/row['relative']).resolve())]=row['SHA']
 for root in (T,S,W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021'):
  for manifest in root.rglob('SOURCE_MANIFEST.json'):
   for row in json.loads(manifest.read_bytes()).get('files',[]):known[str((manifest.parent/row['relative']).resolve())]=row['SHA']
  for report in (root/'reports').glob('*CPU_PREPARED_ACTUAL.json'):
   value=json.loads(report.read_bytes());pack=value.get('package')
   if pack:known[str(Path(pack['path']).resolve())]=pack['SHA']
 for report,folder in (('H1_NATIVE180_EXISTING_FINITE_RETURNED_ACTUAL.json','H1_native180_actual'),('H1_NATIVE180_V2_EXISTING_FINITE_RETURNED_ACTUAL.json','H1_native180_V2_actual')):
  rp=S/'reports'/report
  if rp.is_file():
   for row in json.loads(rp.read_bytes()).get('raw',[]):known[str((S/folder/row['relative']).resolve())]=row['SHA']
 for report,folder in (('SHARED_H1_FULL13_EXISTING_FINITE_RETURNED_ACTUAL.json','shared_H1_full13_V4_actual'),('SHARED_H1_BASELINE32_NATIVE13_V5_FINITE_RETURNED_ACTUAL.json','shared_H1_baseline32_native13_V5_actual'),('SHARED_H1_BASELINE32_FULL13_V6_EXISTING_FINITE_RETURNED_ACTUAL.json','shared_H1_baseline32_full13_V6_actual')):
  rp=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/reports'/report
  if rp.is_file():
   for row in json.loads(rp.read_bytes()).get('raw',[]):known[str((W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021'/folder/row['relative']).resolve())]=row['SHA']
 for report,folder in (('H1_FULL1500_EXISTING_FINITE_RETURNED_ACTUAL.json','H1_full1500_actual'),('E3_NATIVE60_EXISTING_FINITE_RETURNED_ACTUAL.json','E3_native60_actual'),('E3_FULL750_EXISTING_FINITE_RETURNED_ACTUAL.json','E3_full750_actual'),('E2_NATIVE60_V2_EXISTING_FINITE_RETURNED_ACTUAL.json','E2_native60_V2_actual'),('E2_NATIVE60_V3_EXISTING_FINITE_RETURNED_ACTUAL.json','E2_native60_V3_actual'),('E2_FULL750_V3_COMPLETION_V2_FINITE_RETURNED_ACTUAL.json','E2_full750_V3_actual')):
  rp=S/'reports'/report
  if rp.exists():
   for row in json.loads(rp.read_bytes()).get('raw',[]):known[str((S/folder/row['relative']).resolve())]=row['SHA']
 for row in json.loads((T/'reports/STEP270_NATIVE_V4_FULL_RAW_RECEIPT_RECOVERED_V2_ACTUAL.json').read_bytes())['raw']:known[str((T/'native32_v4_actual'/row['relative']).resolve())]=row['SHA']
 for report in (T/'reports').glob('STEP270_SMALL_NATIVE_*_SOURCE_AST_PREPARED_ACTUAL.json'):
  pack=json.loads(report.read_bytes()).get('zip')
  if pack:known[str(Path(pack['path']).resolve())]=pack['SHA']
 for version in ('V1','V2'):
  rp=T/'reports'/('STEP270_FULL20K_NATIVE180_'+version+'_FINITE_RETURNED_ACTUAL.json')
  if rp.is_file():
   for row in json.loads(rp.read_bytes()).get('raw',[]):known[str((T/('full20k_native180_'+version+'_actual')/row['relative']).resolve())]=row['SHA']
 for row in json.loads((T/'reports/STEP270_FULL20K_NATIVE180_V3_CORE_CLOCK_GUARD_WITNESS_CPU_ACTUAL.json').read_bytes())['raw_all_complete_SHA_local_verified']:known[str(Path(row['path']).resolve())]=row['SHA']
 for row in json.loads((T/'reports/H1_CLOSED_PREFIX12_FORENSICS_VERIFIED_RELOCATION_ACTUAL.json').read_bytes())['files']:known[str(Path(row['local_path']).resolve())]=row['SHA']
 row=json.loads((T/'reports/STEP270_20K_EXPLICIT_FULLSTATE_MIGRATION_CPU_REFERENCE_ACTUAL.json').read_bytes())['reference_artifact'];known[str(Path(row['path']).resolve())]=row['SHA']
 for row in json.loads((T/'reports/PAIR_V1_H1_CLOSED_CONTROL318_FORENSICS_RELOCATED_SPACE_RELEASED_ACTUAL.json').read_bytes())['files']:known[str(Path(row['local_path']).resolve())]=row['SHA']
 for row in json.loads((T/'reports/ADDITIONAL_CLOSED_H1_FORENSICS_VERIFIED_C_RELOCATION_SPACE_RELEASED_ACTUAL.json').read_bytes())['files']:known[str(Path(row['local_path']).resolve())]=row['SHA']
 failed_prefix=json.loads((T/'reports/V98_H1_FAILED_PREFIX_AND_ACTUAL_COMMAND_SDK_SOURCE_RETURNED_ACTUAL.json').read_bytes())['prefix'];known[str(Path(failed_prefix['local_path']).resolve())]=failed_prefix['SHA']
 sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
 D.mkdir(parents=True);entries=[];artifacts=[];newfiles={};splits=[];binary={'.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.zip','.png','.jpg','.gif','.mp4','.stl','.mesh','.bin','.so','.dll','.pyd','.ttf','.pyc'}
 def add(p,data):
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);newfiles[p.relative_to(G).as_posix()]=H(data)
 for p in sorted({p for base in (P,B,N,W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021',S,C,K) for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}):
  st=p.stat();s=str(p);saved=prior.get(s.casefold())
  if p.suffix.lower() in binary:
   artifacts.append(dict(path=s,bytes=st.st_size,SHA=known.get(str(p.resolve())),SHA_kind='existing producer manifest/complete receipt' if str(p.resolve()) in known else 'unknown; no Git rehash',original_retained=True));continue
  if saved and saved['bytes']==st.st_size and (saved.get('source_mtime_ns')==st.st_mtime_ns if 'source_mtime_ns' in saved else st.st_mtime<=saved['prior_capture_epoch']):
   entries.append(dict(saved,path=s,source_mtime_ns=st.st_mtime_ns,capture='existing_complete_Git_path_size_mtime_reference',not_rehashed_for_archival=True));continue
  raw=p.read_bytes()
  try:text=raw.decode('utf8')
  except UnicodeDecodeError:
   artifacts.append(dict(path=s,bytes=len(raw),SHA=known.get(str(p.resolve())),SHA_kind='unknown binary; no Git rehash',original_retained=True));continue
  sha=H(raw);saved=bySHA.get(sha)
  if saved:entries.append(dict(saved,path=s,bytes=len(raw),SHA=sha,source_mtime_ns=st.st_mtime_ns,capture='existing_complete_Git_SHA_reference'));continue
  clean,n=redact(text);data=clean.encode('utf8');dest=D/'files'/p.relative_to(W);row=dict(path=s,bytes=len(raw),SHA=sha,source_mtime_ns=st.st_mtime_ns,redaction_count=n,redaction_reason='credential capture-only redaction' if n else None,original_retained=True)
  if len(data)>49_000_000:
   offset=0;parts=[];joined=hashlib.sha256()
   while offset<len(data):
    end=min(offset+24_000_000,len(data))
    while end<len(data) and data[end]&0xc0==0x80:end-=1
    assert end>offset;block=data[offset:end];block.decode('utf8');part=dest.with_name(dest.name+'.utf8part'+str(len(parts)).zfill(4)+'.txt');add(part,block);joined.update(block);parts.append(dict(path=part.relative_to(G).as_posix(),bytes=len(block),SHA=H(block)));offset=end
   assert joined.hexdigest()==H(data);desc=dict(original_path=s,original_bytes=len(raw),original_SHA=sha,archived_bytes=len(data),archived_SHA=H(data),ordered_UTF8_parts=parts,full_reassembled_SHA_verified=True,redaction_count=n);dest=dest.with_name(dest.name+'.ordered_parts.json');add(dest,json.dumps(desc,indent=2).encode('utf8'));row.update(mode='full_ordered_UTF8_parts',archive_SHA=H(data));splits.append(desc)
  else:add(dest,data);row.update(mode='redacted' if n else 'full',archive_SHA=H(data))
  row['archive']=dest.relative_to(G).as_posix();entries.append(row);bySHA[sha]=row
 index=dict(epoch=time.time(),kind='V4_closed46_115_77PPO_no_transfer_pair47_bothPPO',entries=entries,reference_complete_models_producer=proof['models'],actual_original_cost_sumonce=proof['actual_cost_sumonce'],remaining_at_closure_snapshot=proof['remaining_actual_snapshot'],current_pair_actual_GO_PPO_reward_table_reference=active,all_latest_actual_handoff=json.loads((T/'reports/NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED46_115_77_NO_TRANSFER_PAIR47_BOTH_PPO_WORK_ORDER.json').read_bytes()),all_errors_unused_source_and_old_false_preserved=True,actual_retention_and_relocation_locations_preserved=True,no_270mm_or_graduation_claim=True,no_native_query_replay=True,deferred=['e2'],all_old_tags_preserved=True,ordinary_followup_only=True,archival_no_training_or_account_write=True);add(D/'COMPLETE_FILE_CAPTURE_INDEX.json',json.dumps(index,ensure_ascii=False,indent=2).encode('utf8'));add(D/'EXTERNAL_MODEL_ASSET_INDEX.json',json.dumps(dict(epoch=time.time(),artifacts=artifacts,no_binary_rehash_for_Git=True),ensure_ascii=False,indent=2).encode('utf8'))
 paths=list(newfiles);data=b'\0'.join(p.encode('utf8') for p in paths)+b'\0';git('add','--pathspec-from-file=-','--pathspec-file-nul',input=data);git('commit','-m',cfg['title']);head=git('rev-parse','HEAD');git('push','origin','HEAD:main');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head
 assert git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags')==tags
 for line in tags.splitlines():
  a=line.split();assert remote[a[0]]==a[1]
  if len(a)>2:assert remote[a[0]+'^{}']==a[2]
 z=subprocess.run(['git','-C',str(G),'cat-file','--batch'],input=''.join(head+':'+p+'\n' for p in newfiles).encode(),capture_output=True,check=True);offset=0
 for p,sha in newfiles.items():
  end=z.stdout.index(b'\n',offset);a=z.stdout[offset:end].split();assert a[1]==b'blob';size=int(a[2]);offset=end+1;assert H(z.stdout[offset:offset+size])==sha;offset+=size+1
 for desc in splits:
  joined=hashlib.sha256();size=0
  for part in desc['ordered_UTF8_parts']:
   data=(G/part['path']).read_bytes();assert H(data)==part['SHA'];joined.update(data);size+=len(data)
  assert size==desc['archived_bytes'] and joined.hexdigest()==desc['archived_SHA']
 assert not git('status','--porcelain');print(json.dumps(dict(remote_main=head,total_tags=len(tags.splitlines()),ordinary_commit_only=True,all_old_tag_objects_and_peels_unchanged=True,all_new_Git_blobs_and_full_parts_verified=True,source_text_entries=len(entries),new_Git_files=len(newfiles),new_full_large_logs=len(splits),no_record_or_new_tag=True,actual_closed_models={k:x['final']['SHA'] for k,x in proof['models'].items()},cleanup_full_SHA_and_all_paths_verified=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put(R/(NAME+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only=True));raise
