"""Record this actual hour-continuation stage once, with complete lossless report capture."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,importlib,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';U=W/'MOD4_THREE_GPU_HOUR4_CONTINUATION_20261018';REPO=W/'polar-rl-train';BASE='f1c8b881064f30cf75ef91744692c224888532b2';ID='three-gpu-fifth-hour-closed-source-continuation';TAG='trial-20261018-'+ID;TITLE='Continue all three experts from complete fourth-hour checkpoints';DEST=REPO/'history/evidence'/B.name/'actual_fifth_hour_closed_sources';NOTE=B/'FIFTH_HOUR_CLOSED_SOURCES_NOTE_UTF8.txt';MSG=B/'FIFTH_HOUR_CLOSED_SOURCES_TAG_UTF8.txt'
sp=importlib.util.spec_from_file_location('consumed_previous_stage_capture_functions_only',W/'MOD4_THREE_GPU_REAL_TRAINING_HOUR_COHORT_20261018/archive_three_real_gpu_training_hour_unique_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);rawgit=u.rawgit;H=u.H;TEXT=u.TEXT
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and args[4]==MSG.read_text('utf8');return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)
def main():
 assert rawgit('rev-parse','HEAD')==BASE and not rawgit('status','--porcelain') and not rawgit('tag','--list',TAG) and not DEST.exists() and not NOTE.exists();assert json.loads((R/'THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes())['three_actual_PPO_learning_verified'];tags={}
 for line in rawgit('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1383;oldindex=REPO/'history/evidence'/U.name/'actual_fourth_hour_closed_sources/REPORT_CAPTURE_INDEX.json';prior={};known={}
 for r in json.loads(oldindex.read_bytes())['entries']:
  if r.get('Git_path') and r.get('archived_sha256'):prior[r['sha256']]=r
  elif r.get('sha256') and Path(r['source_path']).suffix.lower() not in TEXT:known[str(Path(r['source_path']).resolve())]=dict(bytes=r['bytes'],SHA=r['sha256'],provenance=str(oldindex))
 def accept(path,r,proof):
  if not isinstance(path,str):return
  p=Path(path);sha=r.get('SHA') or r.get('sha256');size=r.get('bytes')
  if p.is_file() and p.suffix.lower() not in TEXT and isinstance(sha,str) and len(sha)==64 and isinstance(size,int) and p.stat().st_size==size:known[str(p.resolve())]=dict(bytes=size,SHA=sha,provenance=str(proof))
 def visit(v,proof):
  if isinstance(v,list):
   for x in v:visit(x,proof)
  elif isinstance(v,dict):
   for k in ('path','local_path','source_path'):accept(v.get(k),v,proof)
   for x in v.values():
    if isinstance(x,(dict,list)):visit(x,proof)
 for root in (U,B):
  for p in root.rglob('*.json'):
   if '__pycache__' in p.parts:continue
   if 'reports' in p.parts or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json':
    v=json.loads(p.read_bytes());visit(v,p)
    if p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json':
     for r in v['files']:accept(str(p.parent/r['relative']),r,p)
 previous=json.loads((U/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert previous['passed_all_three_whole_final_models_CPU'];current=json.loads((R/'THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());active=json.loads((R/'THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes())
 note='The fourth three-GPU hour fully closed. Complete checkpoint source/size/SHA, all-model finite CPU, all17Adam and actor9STD/critic8 actual changes, original independent cost once and actual saved exit/real fcntl evidence are preserved below. No behavior or skill success is inferred.\n\n'+json.dumps(previous,indent=2)+'\n\nThe fifth original expert hour continues each latest full production source on the same GPU/backend. Only sourcefilename/Adam bindings change; whole-worker AST and runtime-assets/RSL5/SDKmath source checks remain exact. All33 existing negative cases reject. Original one-writer two-fcntl independent actual interval sum-once accounting and1188000seconds330h7extensions remain; no ledgercopy/refund/doublecharge/clearactive/tail/budgetincrease. Same3600GOtosave/3900lifecycle300exit/no24updatecutoff and original20k24rollout/reward/LR/learnable inheritedSTD/command/DR/physics/CAD/thresholds. No standalone native replay, fake native checkpoint, live patch, otherjob signal, system change or extra cleanup. No heavy midhour PT/behavior audit. Future hour-end collector is bounded to the actual new writer, same source connection metadata max900 before final download, and remains prepared only.\n\nActual new dispatch:\n'+json.dumps(current,indent=2)+'\n\nActual threeGO/positiveproduction/matchingGPU metadata:\n'+json.dumps(active,indent=2)+'\n\nThe AI owns technical work, without repeated approval attribution. All previous false/failure prefixes/source limitations and ungraduated skills remain. Same original ACTIVE hourly monitor and target; no second watcher or automatic budget. Capture all new sources, reports, errors, unused helpers, workorders, monitor/appreceipts and original cost evidence. Text reports over50MB are preserved completely as ordered UTF8parts with reassemblySHA; model/raw/NPZ/USD/ZIP use producerpathsizeSHAonly, originalsretained. Credentials are capture-redacted with original/archiveSHA and reason. No archival GPU replay or oldPT/rawrehash. One unique record_experiment and annotated-Ftrial preserves all1383oldtags. Pushfailureonlyexistingobjects; poststage formal reports ordinarysupplement, no repeated helper/record/tag or endlessHEADwriteback.'
 for p,s in ((NOTE,note),(MSG,TITLE+'\n\n'+note)):
  with p.open('x',encoding='utf8') as f:f.write(s)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);entries=[];files=[];deferred=[];partsrows=[];newtexts=0
 for root in (U,B):
  for p in sorted(x for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained'));continue
   if p.suffix.lower() not in TEXT:
    r=known.get(str(p.resolve()))
    if r is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No producer SHA; no archival rehash'));continue
    assert p.stat().st_size==r['bytes'];entries.append(dict(source_path=str(p.resolve()),bytes=r['bytes'],sha256=r['SHA'],capture='actual_large_index_only',index_provenance=r['provenance'],original_retained=True));continue
   raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
   if sha in prior:
    r=prior[sha];entries.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=r['Git_path'],archived_sha256=r['archived_sha256'],redaction_count=r.get('redaction_count',0),redaction_reason=r.get('redaction_reason'),original_retained=True));continue
   try:txt=raw.decode('utf8');enc='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
   safe,n=redact(txt);data=safe.encode(enc) if n else raw;dest=DEST/root.name/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',redaction_count=n,redaction_reason='Capture-only credential redaction; original retained' if n else None,original_retained=True)
   if len(data)>49_000_000:
    partdir=dest.with_name(dest.name+'.complete_parts');partdir.mkdir();parts=[];offset=0;assembled=hashlib.sha256()
    while offset<len(data):
     end=min(offset+24_000_000,len(data))
     if end<len(data):end=data.rfind(b'\n',offset,end)+1;assert end>offset
     z=data[offset:end];z.decode(enc);q=partdir/('part'+str(len(parts)).zfill(3)+'.txt');q.write_bytes(z);assembled.update(z);rel=q.relative_to(REPO).as_posix();parts.append(dict(Git_path=rel,bytes=len(z),SHA=hashlib.sha256(z).hexdigest()));files.append(rel);offset=end
    whole=hashlib.sha256(data).hexdigest();assert assembled.hexdigest()==whole;dest=dest.with_name(dest.name+'.SPLIT_CAPTURE_INDEX.json');dest.write_text(json.dumps(dict(source_path=str(p.resolve()),source_bytes=len(raw),source_SHA=sha,archived_whole_bytes=len(data),archived_whole_SHA=whole,ordered_UTF8_parts=parts,reassembly='Concatenate ordered parts without inserting bytes',whole_capture_reassembly_SHA_verified=True,original_source_report_unchanged=True,redaction_count=n),indent=2),'utf8');row.update(capture='complete_UTF8_lossless_ordered_parts',ordered_UTF8_parts=parts,archived_whole_bytes=len(data),archived_whole_SHA=whole,whole_capture_reassembly_SHA_verified=True);partsrows.append(dict(source_path=str(p.resolve()),bytes=len(raw),parts=len(parts),whole_SHA=whole))
   else:dest.write_bytes(data)
   rel=dest.relative_to(REPO).as_posix();row.update(Git_path=rel,archived_bytes=dest.stat().st_size,archived_sha256=H(dest));entries.append(row);prior[sha]=row;files.append(rel);newtexts+=1
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=entries,deferred=deferred,new_texts=newtexts,complete_lossless_text_parts=partsrows,prior_complete_index=oldindex.relative_to(REPO).as_posix()),indent=2),'utf8');files.append(index.relative_to(REPO).as_posix());assert all((REPO/f).stat().st_size<50_000_000 for f in files);rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Fourthhourall3fullmodelCPU/Adam/cost/out; new3GO/positivePPO/compute; originalPPOphysicalaccountAST/sourceSDK; fulltextreportslosslessorderedpartsSHAverified.','--push'];rec.main();head=rawgit('rev-parse','HEAD');obj=rawgit('rev-parse',TAG);verify=u.u.u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;verify.gitio.g=rawgit;verify.verify(entries,tags,head,TAG,obj)
 for row in entries:
  if row.get('ordered_UTF8_parts'):
   h=hashlib.sha256()
   for r in row['ordered_UTF8_parts']:
    z=(REPO/r['Git_path']).read_bytes();assert len(z)==r['bytes'] and hashlib.sha256(z).hexdigest()==r['SHA'];h.update(z)
   assert h.hexdigest()==row['archived_whole_SHA']
 assert len(rawgit('tag','--list').splitlines())==1384;print(json.dumps(dict(commit=head,tag=TAG,object=obj,total_tags1384=True,remote_main_tag_peel_all1383oldtags_tracked_SHA_fulltextparts_verified=True,entries=len(entries),new_texts=newtexts,lossless_text_parts=partsrows,deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THIRD_HOUR_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_recorded_only_push_existingobjects_no_repeat_record_tag=True),f,indent=2)
  raise
