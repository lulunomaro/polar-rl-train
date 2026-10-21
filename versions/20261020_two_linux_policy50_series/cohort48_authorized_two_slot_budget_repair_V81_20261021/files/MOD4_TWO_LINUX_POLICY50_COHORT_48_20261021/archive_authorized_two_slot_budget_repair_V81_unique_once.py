"""Copy to a fresh once helper after actual closure and following two-PPO evidence."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';G=W/'polar-rl-train';ROOT=G/'versions/20261020_two_linux_policy50_series';NAME=Path(__file__).stem
H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args,input=None):
 p=subprocess.run(['git','-C',str(G),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').strip()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert NAME.endswith('_once') and 'TEMPLATE' not in NAME
 arg=R/sys.argv[1];assert arg.resolve().is_relative_to(R.resolve());cfg=json.loads(arg.read_bytes());assert re.fullmatch('[A-Za-z0-9_]{3,90}',cfg['destination']);assert re.fullmatch('[a-f0-9]{40}',cfg['base_HEAD'])
 P=Path(json.loads((B/'NEXT_COHORT_RESERVED_SOURCE_CONFIG_NO_TOKEN.json').read_bytes())['previous_stage_dir']);proof=json.loads((P/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());active=json.loads((R/'TWO50_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_OR_PENDING_ACTUAL.json').read_bytes());nxt=json.loads((R/'NEXT_TWO50_FIVE_UNUSED_WORKFLOW_FILES_ACTUAL_CPU.json').read_bytes());N=Path(nxt['next_stage']);assert proof['passed'] and proof['original_canonical_cost_settled'] and active['passed'] and nxt['passed_source_AST']
 assert all(x.resolve().is_relative_to(W.resolve()) for x in (B,P,N));D=ROOT/cfg['destination'];assert git('rev-parse','HEAD')==cfg['base_HEAD'] and not git('status','--porcelain') and not D.exists();tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(tags.splitlines())>=1416
 put(R/(NAME+'_STARTED_ACTUAL.json'),dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,configuration=cfg,unique_repair_trial_record_no_training_or_ledger_write=True));prior={};bySHA={};old=G/'versions/20261020_linux4090_return_two50';indexes=[old/'COMPLETE_ALL_SOURCE_REPORT_ERROR_INDEX.json'];indexes+=list(ROOT.rglob('COMPLETE_FILE_CAPTURE_INDEX.json')) if ROOT.exists() else []
 for p in sorted(indexes,key=lambda p:json.loads(p.read_bytes())['epoch']):
  v=json.loads(p.read_bytes())
  for x in v['entries']:
   if x.get('SHA') and x.get('archive'):
    row=dict(x,prior_capture_epoch=v['epoch']);prior[x['path'].casefold()]=row;bySHA[x['SHA']]=row
 supplement=old/'POST_GIT_MONITOR_ORDINARY/SUPPLEMENT_INDEX.json'
 if supplement.exists():
  v=json.loads(supplement.read_bytes())
  for x in v['entries']:
   row=dict(path=x['source'],bytes=x['bytes'],SHA=x['SHA'],archive=x['archive'],archive_SHA=x['SHA'],mode='full',prior_capture_epoch=v['epoch']);prior[row['path'].casefold()]=row;bySHA[row['SHA']]=row
 known={}
 for base in (P,B,N):
  for m in base.rglob('THREE_SLOT_COMPLETE_MANIFEST_V1.json'):
   for x in json.loads(m.read_bytes()).get('files',[]):known[str((m.parent/x['relative']).resolve())]=x['SHA']
 for x in proof['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
 sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
 D.mkdir(parents=True);entries=[];artifacts=[];newfiles={};splits=[];binary={'.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.zip','.png','.jpg','.gif','.mp4','.stl','.mesh','.bin','.so','.dll','.pyd','.ttf','.pyc'}
 def add(p,data):
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);newfiles[p.relative_to(G).as_posix()]=H(data)
 for p in sorted({p for base in (P,B,N) for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}):
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
 index=dict(epoch=time.time(),kind='explicitly_approved_two_slot_budget_guard_repair_deployment',entries=entries,new_complete_models_producer=proof['models'],actual_original_cost_sumonce=proof['actual_cost_sumonce'],remaining_at_closure_snapshot=proof['remaining_actual_snapshot'],new_actual_GO_PPO_receipt=active,all_old_tags_preserved=True,unique_authorized_repair_trial=True,archival_no_training_or_account_write=True,deferred=[]);add(D/'COMPLETE_FILE_CAPTURE_INDEX.json',json.dumps(index,ensure_ascii=False,indent=2).encode('utf8'));add(D/'EXTERNAL_MODEL_ASSET_INDEX.json',json.dumps(dict(epoch=time.time(),artifacts=artifacts,no_binary_rehash_for_Git=True),ensure_ascii=False,indent=2).encode('utf8'))
 import record_experiment as recorder
 original_record_git=recorder.git
 def exact_record_git(*args):
  if args and args[0]=='add':
   assert args[1]=='--';paths=args[2:];data=b'\0'.join(p.encode('utf8') for p in paths)+b'\0';return git('add','--pathspec-from-file=-','--pathspec-file-nul',input=data)
  return original_record_git(*args)
 recorder.git=exact_record_git
 sys.argv=['record_experiment.py','--id','e2-e3-scheduled-two-slot-budget-guard-approved-v81','--title',cfg['title'],'--kind','repair','--note-file',str(B/'ACTUAL_TWO50_CLOSED_AND_NEXT_LEARNING_V81_STAGE_NOTE.md'),'--validation','Human explicitly approved scheduled E2/E3 caps; 10 CPU budget cases; target full source CPU; remote owner SHA exact; both actual GO/PPO/UUID/createargv and original writer locks verified; no skill qualification.','--files',*newfiles]
 recorder.main()
 tag=git('tag','--points-at','HEAD').splitlines();assert len(tag)==1;tag=tag[0];git('push','--atomic','origin','HEAD:main','refs/tags/'+tag);head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head
 assert remote['refs/tags/'+tag]==git('rev-parse','refs/tags/'+tag) and remote['refs/tags/'+tag+'^{}']==head
 assert len(git('tag','--list').splitlines())==len(tags.splitlines())+1
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
 assert not git('status','--porcelain');print(json.dumps(dict(remote_main=head,total_tags=len(tags.splitlines())+1,unique_tag=tag,unique_tag_object=git('rev-parse','refs/tags/'+tag),all_old_tag_objects_and_peels_unchanged=True,all_new_Git_blobs_and_full_parts_verified=True,source_text_entries=len(entries),new_Git_files=len(newfiles),new_full_large_logs=len(splits),unique_record_once=True,actual_closed_models={k:x['final']['SHA'] for k,x in proof['models'].items()},next_two_PPO_verified=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put(R/(NAME+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only=True));raise
