"""Ordinary supplement after the actual stage, no new experiment or repeated tag."""
from pathlib import Path
import sys,json,time,hashlib,traceback,importlib.util
B=Path(__file__).resolve().parent;R=B/'reports';P=B.parent/'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018';REPO=B.parent/'polar-rl-train';BASE='72a59d625978abdaf7ca94d7282fff9a4d13bac6';DEST=REPO/'history/evidence'/B.name/'followup_hour2_production_fe778_full_actual';NOTE=B/'HOUR2_PRODUCTION_FE778_FULL_ORDINARY_NOTE_UTF8.txt'
sp=importlib.util.spec_from_file_location('consumed_stage_pure_utilities_only',B/'archive_three_gpu_storage_linux_experts_hour_unique_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);git=u.rawgit;H=u.H;TEXT=u.TEXT
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists() and not NOTE.exists()
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1378
 oldindex=REPO/'history/evidence'/B.name/'actual_storage_experts_and_H1_hour/REPORT_CAPTURE_INDEX.json';old=json.loads(oldindex.read_bytes());prior={r['sha256']:r for r in old['entries'] if r.get('Git_path') and r.get('archived_sha256')};known={str(Path(r['source_path']).resolve()):r for r in old['entries'] if r.get('sha256') and Path(r['source_path']).suffix.lower() not in TEXT}
 def visit(v,proof):
  if isinstance(v,list):
   for x in v:visit(x,proof)
  elif isinstance(v,dict):
   sha=v.get('SHA') or v.get('sha256');size=v.get('bytes')
   if isinstance(sha,str) and len(sha)==64 and isinstance(size,int):
    for key in ('local_path','path','source_path'):
     if isinstance(v.get(key),str):
      p=Path(v[key])
      if p.is_file() and p.suffix.lower() not in TEXT and p.stat().st_size==size:known[str(p.resolve())]=dict(bytes=size,sha256=sha,index_provenance=str(proof))
   for x in v.values():
    if isinstance(x,(list,dict)):visit(x,proof)
 for root in (B,P):
  for p in root.rglob('*.json'):
   if 'reports' in p.parts and '__pycache__' not in p.parts:visit(json.loads(p.read_bytes()),p)
 note='Ordinary actual followup only after unique72a59d6/tag7a5995e5. Original1378tagobjectspeels unchanged. H1hour2 own20knative180/3.6Mpolicy14.4Mphysical originalformalFP32CPU actualpass max3.43322754e-5; originalowner124906 trueGO1792317866.576721=18:04:26.576721Beijing,productionworker27620/create1792317866.97 actualmetadata phaseproduction/noerror. Saveplanned19:04:26,nominalend19:09:26 notfutureFINALguarantee. Samecompletefe778/owned71/Adam648000 inheritsallstate; onehour3600+300cap3900,no24updatecutoff,originalbudget/physics/reward/LR/STD/sourceguards retained. No midhourfirstPT/behavioraudit, no healthytrainingstop. FutureonlymissingH2finalcollector/fullmodelCPU/frozenpreparer adaptedactualowner/sourcefilename/dispatch andCPUimportASTbindingverified,notexecuted. Newfe778210full1500/80/6000cb all26filesactualcomplete/twohostSHA,parent127446child127447EXIT0/out/privatefcntlFree/noerror. ExistingfrozenV3 dual64 rawreferencefalse .00010465342667487221>original.0001,FP32diagnostic .0002593994; originalerrortrace retained. ExistingonlyCPUdiagnostic allotheroriginalsource/physical/phase/query/contactCOMhardware/authored34 checks passed,executedclip6reference6.1685141e-5,one dual64overboundrow allsaturatedsameexecution,notreplacementforrawfalse/qualification. 35takeoff7landing0recovery strictvalidfirstprefix descriptive,ordinary669/trunc0,idealZ0false2; no statisticalsamebackendactualinitialmatched oruniquecauseclaim. Native120passindependentretained; fullrawfalse notnewtraininggate,nohumanquestion orPPOinterruption. Allfirstepisodefailedprefix/originalnumericfalse/readererrors retained. Same mod4-10ACTIVEhourly/originaltargetV15 appreceipt/TOMLreadback exact, no newmonitor/autobudget. Allfinitecollectorreturned/freshCIMknown0, noextraSSH/replaynative/full/PT/rawhash/GPU/accountmutation. Capture allnewS+R source/report/error/fullcollectionindices/workorder/monitor/appreceipt/stagereceipt andthissource/note. LargeartifactsproducerpathsizeSHAonly, noarchivehash; originalsretainedexceptpreviouslyindexedexact81deletedbuffers. Finalremoteverificationtooloutput isreceipt, noendlessHEADwriteback. Pushfailureonlyexistingobjects,norepeatedcommit/tag/helper.'
 with NOTE.open('x',encoding='utf8') as f:f.write(note)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];deferred=[];captured=0
 for root in (P,B):
  for p in sorted(x for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained'));continue
   if p.suffix.lower() not in TEXT:
    r=known.get(str(p.resolve()))
    if r is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No existing producer checksum; no archive rehash'));continue
    assert p.stat().st_size==r['bytes'];rows.append(dict(source_path=str(p.resolve()),bytes=r['bytes'],sha256=r['sha256'],capture='actual_large_index_only',index_provenance=r.get('index_provenance','prior complete Git index'),original_retained=True));continue
   raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
   if sha in prior:
    r=prior[sha];rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=r['Git_path'],archived_sha256=r['archived_sha256'],redaction_count=r.get('redaction_count',0),redaction_reason=r.get('redaction_reason'),original_retained=True));continue
   try:txt=raw.decode('utf8');enc='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
   safe,n=redact(txt);data=safe.encode(enc) if n else raw;dst=DEST/root.name/p.relative_to(root);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);r=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=dst.relative_to(REPO).as_posix(),archived_bytes=len(data),archived_sha256=H(dst),redaction_count=n,redaction_reason='Capture-only credential redaction, original retained' if n else None,original_retained=True);rows.append(r);prior[sha]=r;captured+=1
 (DEST/'REPORT_CAPTURE_INDEX.json').write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,new_texts=captured,prior_complete_index=oldindex.relative_to(REPO).as_posix(),ordinary_only_no_new_tag=True),indent=2),'utf8');git('add','--',DEST.relative_to(REPO).as_posix());git('commit','-F',str(NOTE));head=git('rev-parse','HEAD');git('push','origin','HEAD:main');v=u.u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=git;v.verify(rows,tags,head);assert len(git('tag','--list').splitlines())==1378
 print(json.dumps(dict(ordinary_commit=head,remote_main_all1378tag_objects_peels_and_tracked_SHA_verified=True,entries=len(rows),new_texts=captured,deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('HOUR2_PRODUCTION_FE778_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_committed_only_push_existing_objects_no_repeat_commit_or_tag=True),f,indent=2)
  raise
