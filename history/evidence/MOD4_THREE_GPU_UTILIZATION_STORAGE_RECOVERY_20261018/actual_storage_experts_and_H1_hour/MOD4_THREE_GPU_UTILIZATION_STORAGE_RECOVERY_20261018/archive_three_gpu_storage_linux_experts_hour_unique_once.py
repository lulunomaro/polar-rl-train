"""Record this actual storage/scheduling repair once, including every failed wrapper and saved report."""
from pathlib import Path
import sys,os,json,time,hashlib,traceback,importlib.util,importlib
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';P=W/'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018';REPO=W/'polar-rl-train'
BASE='29a389d4c64a5342cbe92d51deea32b2ac50ef2c';ID='three-gpu-storage-reclaim-linux-experts-hour-continuation';TAG='trial-20261018-'+ID;TITLE='Restore210 storage and threeGPU work while continuing one-hour H1 blocks'
DEST=REPO/'history/evidence'/B.name/'actual_storage_experts_and_H1_hour';NOTE=B/'THREE_GPU_STORAGE_LINUX_EXPERTS_HOUR_NOTE_UTF8.txt';MSG=B/'THREE_GPU_STORAGE_LINUX_EXPERTS_HOUR_TAG_UTF8.txt'
sp=importlib.util.spec_from_file_location('consumed_old_stage_pure_git_functions_only',P/'archive_ce3_original_fp32_native_reuse_training_unique_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);rawgit=u.rawgit;H=u.H;TEXT=set(u.TEXT)|{'.cpp','.h','.hpp','.c','.cc','.rst'}
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and args[4]==MSG.read_text('utf8');return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)
def main():
 assert rawgit('rev-parse','HEAD')==BASE and not rawgit('status','--porcelain') and not rawgit('tag','--list',TAG) and not DEST.exists() and not NOTE.exists() and not MSG.exists()
 cleanup=json.loads((R/'EXACT81_OLD_BUFFER_DELETE_FINAL_ACTUAL.json').read_bytes());assert cleanup['above_original25GiB']
 assert json.loads((R/'E3_LINUX_FULL1500_RECORDED_PHYSICS_REWARD_CPU_ACTUAL.json').read_bytes())['passed_recorded_full_data_source_physics_CPU']
 assert json.loads((R/'E2_LINUX_FULL1500_RECORDED_PHYSICS_REWARD_CPU_ACTUAL.json').read_bytes())['passed_recorded_full_data_source_physics_CPU']
 tags={}
 for line in rawgit('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1377
 oldrows=[];prior_indices=[]
 for rel in ('actual_H1_8a7c_review_one_hour_continuation','followup_H1_hour_requested_current_status','followup_three_4090_requested_status'):
  p=REPO/'history/evidence'/P.name/rel/'REPORT_CAPTURE_INDEX.json';v=json.loads(p.read_bytes());oldrows.extend(v['entries']);prior_indices.append(p.relative_to(REPO).as_posix())
 prior={r['sha256']:r for r in oldrows if r.get('Git_path') and r.get('archived_sha256')};known={str(Path(r['source_path']).resolve()):dict(bytes=r['bytes'],SHA=r['sha256'],provenance='prior complete Git capture index') for r in oldrows if r.get('sha256') and Path(r['source_path']).suffix.lower() not in TEXT};skipped=[]
 def accept(path,row,proof):
  if not isinstance(path,str) or not isinstance(row.get('bytes'),int):return
  sha=row.get('SHA') or row.get('sha256');p=Path(path)
  if not isinstance(sha,str) or len(sha)!=64 or not p.is_file() or p.suffix.lower() in TEXT:return
  if p.stat().st_size!=row['bytes']:skipped.append(dict(path=str(p),proof=str(proof),declared_bytes=row['bytes'],actual_bytes=p.stat().st_size,reason='Historical manifest alias not current complete artifact proof'));return
  known[str(p.resolve())]=dict(bytes=row['bytes'],SHA=sha,provenance=str(proof))
 def visit(v,proof):
  if isinstance(v,list):
   for row in v:visit(row,proof)
  elif isinstance(v,dict):
   for key in ('path','local_path','source_path'):accept(v.get(key),v,proof)
   for val in v.values():
    if isinstance(val,(dict,list)):visit(val,proof)
 for root in (P,B):
  for p in root.rglob('*.json'):
   if '__pycache__' in p.parts:continue
   v=json.loads(p.read_bytes())
   if 'reports' in p.parts:visit(v,p)
   if isinstance(v,dict) and (p.name.endswith('MANIFEST_V1.json') or p.name=='LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json'):
    for row in v.get('files',[]):
     if isinstance(row,dict) and isinstance(row.get('relative'),str):accept(str(p.parent/row['relative']),row,p)
 note='Human again required deletion of unnecessary old210 data and meaningful use of allthree4090. Agent scheduling/execution failure is agent responsibility, no repeated technical approval attribution. New exact81 closed121 middle control-prefix buffers each prehashed against originalproducer index then actuallydeletedonce:27045605376allocatedbytes reclaimed,free21626306560to48671883264,888protectedfiles metadataunchanged. Firstlast2/every25milestones/allcheckpoints/sources/reports retained; deleted81 originals accuratelydeclared deleted, notbackedup. Old189/new81 bothconsumed; no broaddeletion/remount/fstab/WindowsCwrite. New unusedLinux210 E2sourceca6fc/owned112/Adam666780 andLinux72GPU1 E3source8043/owned85/657660 diagnosticcases use frozenactoronly, fresh88/104, originalseed60928white_v3 andsourcephysics/reward/commands/DR/hardware, nooptimizer/PPO/paidGO/budget. Preserve everyattempt: d1callableclass inspect.getsourcefile TypeError,missingAppLauncher; only exactownedfailedSDKorphan117732 aftermainparentout/noGPU/cwdargvcreateproof SIGTERM withactualexit, notH1orotherjob. V2localstaleorphanreportprelaunchreject; d2oldWindowsquerybinding rejection; v3LinuxPhysXbinding+originaltenpublicC++references,localFileExistsbeforeupload thenuniqueV5; d3SDKProxyArray torch.is_tensor numpyCUDAconversion errors andvalidprefixraw. V4usesexistingtypedcpu adapteronly, callable/ProxyfixturesandAST, ownunusedd4 native120 andallrowsCPUactualpass; E3readeroriginalwronggeometrypathfalse thenresolvedcorrectpathindependentCPU. v1unimportedhistoricalmigrationtoolcredentialcapture-redactedonly originalsretained; v2+excludedunimportedstandalonetool. Newfull1500/6000cb actualcomplete: E2all30files/218260237B raw1aaaca... andE3all29files/904205878B rawe401fa..., twohostcompleteSHA; actualparentschildrenout/privatefcntlFree/noerror. Fullallrow source/actor/normal35/clip6/previousactual/reset/contactintegral/COM/torquespeed/query/authoredgeometry andE3originalphase recipeage stablecreditedrequestpeak literalreconstructionpassed. E2ordinary0/all88alive15s butsigned4worldgoal skillfalse; actualworldmetrics retained. E3ordinary3251,strict0/96,57/96validprefixupright50and15salive,normal8/8,39closurefirstfail. PassiveactualRewardManager termweightparams/source andstepreadouts,body/worldframes collected; legacyjump/spin/recoveryactive absent inthesenewLinuxcases, notoldcase/H1proof oruniquecause. No reward/LR/STD/physicalthreshold/gatechanges. Priorhour1H1 naturallyclosed71updates1704controls34.08Menvsteps:completefe7780a502743dc12c0826d82f4a5a5a5ee8917f095890c7bfb866c48b600309/16644915B/Adam648000,199tensor105float finite/all17actualchanges. Originalowner110623/node22089/worker22790 actualoutEXIT0/canonicalNone/twooriginalfcntl/private/sharedfree,actual3641.6100673675537seconds oncecharged,remaining496844.9903564453readsnapshotonly. CompositefinitecollectorreadnewE2/E3fullthenonlymissingH1finalactualreturned, no oldcompletePT/rawreplay. H1samecompletefe778preparedandactuallynewhour2owner124906/node26884/native26888 rootH1h2_1810p5; targetfullsourceRSL5SDKCPU actualpass andoriginalcostouthandoff beforedispatch. Latestnative/noerrors/goempty at18:00capture, notnewPPOyet. Ownnew20knative180/originalformalFP32CPU thenoriginalowner onehourGOsave3600+lifecycle3900exitreserve300; no24updatecutoff,rollout24unchanged,all25GiBstart/free8GiB/GPU/RAM/hardwareguards. Fullmodel/behaviorauditonlyafterhour,safehandoffnotliveextension. New completefe778 frozenpackage thenportedhost/GPU/interpreter/lockbindingonlyto210 sourceGPUprivateoriginalfcntl andsameDguard. InitialPathFinder missededitableIsaacLabbeforeanyworker,inlinefollowupNoneType retainedinrepairreport; V2onlyimportlib.util.find_spec SDKlookupfix actualsameSDK/RSLsourceSHAs andnewunusednative120 actualcomplete/all26files/allrowCPU pass. SamealreadyexistingfrozenV3 dual64audit bound1e-4,max4.5070993e-5,originalFP32diagnostic.0001182556 preservedseparately; ordinary34/11takeoff0landing0recovery nativecontext notfullskill. Newunusedsamebackendfull1500parent127446/H1f7_1810ev1f actualdispatch,stillpending,notfalsePASS. 72H1notstoppedforevaluation. AllthreeGPUshaveactualworkthisturn, notall3PPO/100percent/permanentidle. Latesthumanonehourcadencecontinuesoriginalscope; E2E3paidholds0GOcharged,3060SSHrestorednofreshdesktop/MSVCRTadmission,Laptoppaused. AlltransportfreshlocalCIM andonlyactualalivefiniteexclusive21072_249,actualreturns; no secondmonitor/watcher5minSSH/GittraininghostSSH/otherjobkill/lockdelete. Original1188000seconds/master812a4b004005RM003002001/7extensions/onewriterreal2fcntlactualGOindependentintervalonce preserved; no ledgercopy/clear/refund/doublecharge/newbudget. Scopephysics2.5msx4TGS32/4/100Hz/history5msbin3/20kx24/35-38-6/25612864ELU/D0D7noisehardware/public4-only.001clip6/LRconfig1e-4adaptivevsstored1e-5/learnableinheritedsixSTD allunchanged. Allancestorfalse/effectiveprefix/unknowns retained, noS3S5graduation/heldouttuning/sourcebinaryorcookedmanifoldproof. Sameoriginalmod4-10ACTIVEhourly/targetupdatedV14andappTOMLreadbackexact nosecondmonitor/autobudget; healthyunchangedpendingquiet. CaptureallS+Rnewsource/report/errors/lookupmiss/unusedhelpers/workorder/appreceipt exactorcredential-redactedoriginalSHA; largeonlyexistingproducerpathsizeSHA, originalsretainedexceptexactauthorizeddeleted81oldbuffers; partialdeferred. Oneunique record_experiment/-Fannotatedtrial, preserveall1377tagobjectspeels, remote/trackedverify. Poststageformalreceiptsordinaryonly,pushfailureexistingobjects,norepeatrecord/tag orendlessHEADwriteback. Gitdoesnotstoptraining/replayGPU/modifyaccount.'
 for p,t in ((NOTE,note),(MSG,TITLE+'\n\n'+note)):
  with p.open('x',encoding='utf8') as f:f.write(t)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[];captured=0
 for root in (P,B):
  for p in sorted(x for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained incomplete'));continue
   if p.suffix.lower() not in TEXT:
    r=known.get(str(p.resolve()))
    if r is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No existing current producer checksum; no archival rehash'));continue
    assert p.stat().st_size==r['bytes'];rows.append(dict(source_path=str(p.resolve()),bytes=r['bytes'],sha256=r['SHA'],capture='actual_large_index_only',index_provenance=r['provenance'],original_retained=True));continue
   raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
   if sha in prior:
    r=prior[sha];rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=r['Git_path'],archived_sha256=r['archived_sha256'],redaction_count=r.get('redaction_count',0),redaction_reason=r.get('redaction_reason'),original_retained=True));continue
   try:txt=raw.decode('utf8');enc='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
   safe,n=redact(txt);data=safe.encode(enc) if n else raw;dst=DEST/root.name/p.relative_to(root);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);rel=dst.relative_to(REPO).as_posix();r=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=rel,archived_bytes=len(data),archived_sha256=H(dst),byte_preserving_decode=enc,redaction_count=n,redaction_reason='Capture-only historical credential redaction; original retained' if n else None,original_retained=True);rows.append(r);prior[sha]=r;files.append(rel);captured+=1
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,new_texts=captured,prior_complete_indices=prior_indices,skipped_stale_large_aliases=skipped,no_archive_GPU_or_large_rehash_or_account_mutation=True),indent=2),'utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Exact81cleanup actual27GB reclaimed; both new Linux expert full1500 allrow CPU and source reward readouts; H1 hour1closed71wholeCPU costexit; actualhour2newnative andnew210frozen nativeCPU/fulldispatch; all failures and current pending retained.','--push'];rec.main();head=rawgit('rev-parse','HEAD');obj=rawgit('rev-parse',TAG)
 v=u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=rawgit;v.verify(rows,tags,head,TAG,obj);assert len(rawgit('tag','--list').splitlines())==1378
 print(json.dumps(dict(commit=head,tag=TAG,object=obj,total_tags=1378,remote_main_tag_peel_all1377_old_tags_and_tracked_SHA_verified=True,entries=len(rows),new_texts=captured,deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THREE_GPU_STORAGE_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_committed_push_existing_objects_only_no_repeat_record_tag=True),f,indent=2)
  raise
