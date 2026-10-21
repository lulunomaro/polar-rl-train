from pathlib import Path
import hashlib,json,subprocess,time,tomllib,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;G=W/'polar-rl-train';D=G/'versions/20261020_two_linux_policy50_series/cohort50_closed51_learning_shared_eval_V84_20261021/POST_GIT_MONITOR_ORDINARY'
H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(G),*args],text=True).strip()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 assert git('rev-parse','HEAD')==json.loads((R/'V84_MAIN_ORDINARY_GIT_ACTUAL.json').read_bytes())['remote_main'] and not git('status','--porcelain') and not D.exists()
 tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines();assert len(tags)==1418
 a=json.loads((R/'V84_POSTGIT_MONITOR_UPDATE_ARGS.json').read_bytes());raw=(Path.home()/'.codex/automations/mod4-10/automation.toml').read_bytes();saved=tomllib.loads(raw.decode());checks=dict(prompt=saved['prompt']==a['prompt'],status=saved['status']==a['status']=='ACTIVE',rrule=saved['rrule']==a['rrule'],target=saved['target_thread_id']==a['targetThreadId'],id=saved['id']=='mod4-10');assert all(checks.values())
 put(R/'V84_POSTGIT_EXACT_MONITOR_READBACK_ACTUAL.json',dict(epoch=time.time(),passed=True,checks=checks,prompt=saved['prompt'],TOML_SHA=H(raw),no_second_monitor=True))
 old=json.loads((D.parent/'COMPLETE_FILE_CAPTURE_INDEX.json').read_bytes());prior={x['path'].casefold():x for x in old['entries']};bases=[B,W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021']+[W/('MOD4_TWO_LINUX_POLICY50_COHORT_'+str(i)+'_20261021') for i in (50,52)];binary={'.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.png','.jpg','.gif','.mp4','.stl','.mesh','.bin','.so','.dll','.pyd','.ttf','.pyc','.cubin','.pch'};D.mkdir(parents=True);index=[];files={};sys=__import__('sys');sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
 for p in sorted({p for base in bases for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}):
  if p.suffix.lower() in binary:continue
  st=p.stat();savedrow=prior.get(str(p).casefold())
  if savedrow and savedrow['bytes']==st.st_size and savedrow.get('source_mtime_ns')==st.st_mtime_ns:continue
  data=p.read_bytes()
  try:text=data.decode('utf8')
  except UnicodeDecodeError:continue
  if savedrow and H(data)==savedrow['SHA']:continue
  clean,n=redact(text);encoded=clean.encode();assert len(encoded)<49_000_000
  dest=D/'files'/p.relative_to(W);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(encoded);rel=dest.relative_to(G).as_posix();files[rel]=H(encoded);index.append(dict(source=str(p),bytes=len(data),SHA=H(data),archive=rel,archive_SHA=H(encoded),redaction_count=n,complete_UTF8=True))
 desc=D/'SUPPLEMENT_INDEX.json';put(desc,dict(epoch=time.time(),entries=index,ordinary_only_no_record_tag_or_training=True,unique_base='257dde27b0c4d0da917b5958f4442e058ad0a4a5',all_saved_postsupplement_texts_in_four_scopes_captured=True));files[desc.relative_to(G).as_posix()]=H(desc.read_bytes());paths=list(files)
 subprocess.run(['git','-C',str(G),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(x.encode() for x in paths)+b'\0',check=True,capture_output=True);git('commit','-m','Record V84 existing monitor exact readback and verified closed50 shared-evaluation handoff');git('push','origin','main');head=git('rev-parse','HEAD');remote=dict(x.split()[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines());assert remote['refs/heads/main']==head
 for line in tags:
  row=line.split();assert remote[row[0]]==row[1]
  if len(row)==3:assert remote[row[0]+'^{}']==row[2]
 for path,sha in files.items():assert H(subprocess.check_output(['git','-C',str(G),'show',head+':'+path]))==sha
 assert not git('status','--porcelain');print(json.dumps(dict(remote_main=head,all1418_tag_objects_and_peels_unchanged=True,existing_monitor_exact=True,ordinary_only=True,new_complete_texts=len(index),all_new_Git_blobs_verified=True,workspace_clean=True)),flush=True)
except BaseException:
 put(R/('V84_POSTGIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_objects_not_record_or_tag=True));raise
