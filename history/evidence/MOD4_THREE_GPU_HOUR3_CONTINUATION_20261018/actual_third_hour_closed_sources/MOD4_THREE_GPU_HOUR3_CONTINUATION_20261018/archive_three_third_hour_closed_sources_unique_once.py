"""Record this actual hour-continuation stage once, with complete lossless report capture."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,importlib,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';U=W/'MOD4_THREE_GPU_HOUR2_CONTINUATION_20261018';REPO=W/'polar-rl-train';BASE='cabb92cdd006479ddccd00ee73a81c4345f65e9f';ID='three-gpu-third-hour-closed-source-continuation';TAG='trial-20261018-'+ID;TITLE='Continue three independent experts from complete second-hour checkpoints';DEST=REPO/'history/evidence'/B.name/'actual_third_hour_closed_sources';NOTE=B/'THIRD_HOUR_CLOSED_SOURCES_NOTE_UTF8.txt';MSG=B/'THIRD_HOUR_CLOSED_SOURCES_TAG_UTF8.txt'
sp=importlib.util.spec_from_file_location('consumed_previous_stage_capture_functions_only',U/'archive_three_closed_source_next_hour_unique_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);rawgit=u.rawgit;H=u.H;TEXT=u.TEXT
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and args[4]==MSG.read_text('utf8');return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)
def main():
 assert rawgit('rev-parse','HEAD')==BASE and not rawgit('status','--porcelain') and not rawgit('tag','--list',TAG) and not DEST.exists() and not NOTE.exists();assert json.loads((R/'THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes())['three_actual_PPO_learning_verified'];tags={}
 for line in rawgit('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1380;oldindex=REPO/'history/evidence'/U.name/'actual_three_closed_source_next_hour/REPORT_CAPTURE_INDEX.json';prior={};known={}
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
 note='''The second three-GPU hour completed and all three full checkpoints passed local CPU verification. H1 completed74updates/35.52Menvsteps, SHA cbcbe7dace2215d19040cb51f14961e2e9fac3b650d020047a524a4e53f51bcf,16645235bytes,Adam652420. E2 completed241updates/115.68Menvsteps,SHA022c25069b299b245fe5b5bc3539194c0d5e1a483d3cf4c05bbf39410a7a4647,14615528bytes,Adam676420. E3 completed95updates/45.6Menvsteps,SHA58010f3c34f5b1aa43fb206a56ca89353159a18a23154fd9c1fbb071778b6e01,14715349bytes,Adam661460. All17actorSTD/critic tensors changed, all17Adam steps advanced20perupdate, complete model/runtime finite, full model counts199/105,175/98,173/96. Originalowner150567 and all nodes/children actually exited0; canonicalNone, original twofcntl and GPU private/shared free. Actual independent costs3661.9466540813446/3616.773087501526/3643.8627054691315 seconds,sum10922.582447052002 chargedonce; remaining471355.60507392883 is a readonly snapshot, not a new budget or refund.

The next original three-expert hour uses each latest full production checkpoint on the same GPU/backend. E3 was already a direct production-source loader; this time all workers change only sourcefilename and expectedAdam bindings. Normalized whole-worker AST, static runtime/assets/lib manifests and installedRSL5/SDKmath source checks remain exact. All33 existing wrong-source/backend/GPU/Adam/schema/finite/EXIT/cost/failedprefix/runtime/AST negative cases reject. Originalaccount/owner/node code is retained. No standalone native replay, no productioncheckpoint masquerading as native, no live patch, no reward/LR/learnable inheritedSTD/command/physics/CAD/threshold change. The AI owns these technical changes; no repeated approval attribution.

New originalwriter162530, E2node162535, H1node35140, E3node35157 use unused T3h3_1810v3 roots. Three actualGO/positiveproductionupdate logs/matchingGPUcompute are verified before claiming actual learning. Each slot saves after3600seconds fromtrueGO, lifecycle3900including300exit; no24updatecutoff, original20k24rollout and25GiBstart/free8GiB completeupdate savedstop/physical guards retained. No midhour checkpoint download or heavy behavior audit. Future final collector/reviewer binds this actual new dispatch and is prepared only. Original1188000seconds330h7extensions and oneoriginalwriter/twofcntl/independentactualintervalsumonce remain; no ledgercopy/doublecharge/clearactive/refund/tail/budgetincrease.

All second-hour closure/CPU/model indices/cost/exit evidence and third-hour sources/controllers/CPU/resource/deployment/metadata/workorder/monitor/appreceipts are captured. Historical failures and earlier numeric false reports remain. Oversized text reports are fully preserved in ordered UTF8 parts with whole-reassembly SHA verification, rather than omitting text or changing the50MB record limit. Large model/raw/NPZ/USD/ZIP files use existing producer path/size/SHA only; originals stay in place. Credentials are capture-redacted with original/archive SHA and reason. No archival GPU replay, old PT/raw rehash, otherjob signal, system change or repeated cleanup. Same originalACTIVE hourly monitor and target, no secondwatcher or automaticbudget. One unique record_experiment and annotated-F trial, preserving all1380oldtags. Push failure continues existingobjects only; later formal reports are ordinary supplements, never repeated record/tag/helper. Git verification output is the receipt, avoiding endless HEAD writeback.'''
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
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=entries,deferred=deferred,new_texts=newtexts,complete_lossless_text_parts=partsrows,prior_complete_index=oldindex.relative_to(REPO).as_posix()),indent=2),'utf8');files.append(index.relative_to(REPO).as_posix());assert all((REPO/f).stat().st_size<50_000_000 for f in files);rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Secondhourall3fullmodelCPU/Adam/cost/out; new3GO/positivePPO/compute; originalPPOphysicalaccountAST/sourceSDK; fulltextreportslosslessorderedpartsSHAverified.','--push'];rec.main();head=rawgit('rev-parse','HEAD');obj=rawgit('rev-parse',TAG);verify=u.stage.u.u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;verify.gitio.g=rawgit;verify.verify(entries,tags,head,TAG,obj)
 for row in entries:
  if row.get('ordered_UTF8_parts'):
   h=hashlib.sha256()
   for r in row['ordered_UTF8_parts']:
    z=(REPO/r['Git_path']).read_bytes();assert len(z)==r['bytes'] and hashlib.sha256(z).hexdigest()==r['SHA'];h.update(z)
   assert h.hexdigest()==row['archived_whole_SHA']
 assert len(rawgit('tag','--list').splitlines())==1381;print(json.dumps(dict(commit=head,tag=TAG,object=obj,total_tags1381=True,remote_main_tag_peel_all1380oldtags_tracked_SHA_fulltextparts_verified=True,entries=len(entries),new_texts=newtexts,lossless_text_parts=partsrows,deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THIRD_HOUR_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_recorded_only_push_existingobjects_no_repeat_record_tag=True),f,indent=2)
  raise
