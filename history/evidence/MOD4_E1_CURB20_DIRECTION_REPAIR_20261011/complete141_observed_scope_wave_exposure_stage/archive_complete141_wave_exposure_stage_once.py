"""Unique real stage, preserve all prior evidence and append only new SHA captures."""
from direction_io import *
import subprocess,importlib
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'))
import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';BASE=REPO/'history/evidence'/D.name
DEST=BASE/'complete141_observed_scope_wave_exposure_stage'
ID='curb20-complete141-observed-route-accepted-wave-exposure-reviewed'

def main():
 assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only')
 assert not gitio.g('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((R/'COMPLETE141_AND_WAVE_NEXT_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 previous=gitio.refs();save('COMPLETE141_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=gitio.g('rev-parse','HEAD'),old_tags=len(previous)))
 note=R/'COMPLETE141_OBSERVED_SCOPE_WAVE_EXPOSURE_STAGE_REPORT.md';assert not note.exists()
 note.write_text('# Complete CURB141 observed20mm acceptance and next Wave exposure diagnosis\n\nOwn source424 model32114 SHA7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43, CPU104, source424 and actual91snapshot+ownfreeze, PID2845252/PASSED complete save independently verified. SameCURB geometry/entry/direction allnine actorcriticoptimizerstd/D0D7/globalnamed/dictprivateCPUCUDA startup receipts, CUDA diskroundtrip and savedsourceepisode+1 exact; notPhysXexactresume. 46updates1104controls22.08Menvsteps4416callbacks, ordinary/integrity/unknown0/nonfinitefalse/STOPnone, closure.981814577mm/mimic.001691456rad. Timeout9685 plusroute7731 overlap7 union17409 and bothcoverageexact. Target900s includedload-learn-save-exit; actual935.517459s originalparent unique closed segment, no extension/recharge. Actualparentguardianchildexited, twofcntlOSlocksfree, active-Sactiveempty and savedreviewready are a legal lesson boundary, notfault/globalfinished.\n\nCandidate141 fourcases actualcomplete/errorfree, twohost8probe/result JSON byteSHAexact, full180926768bytes rawNPZ SHA4c4d4c31cdd61b25ed218a93dfe71405ce8c2d59b321e61902421c55ae9918b1. Fullroot30q/physicalparameters/recipes/assignments6000callbacks and actualground-contact integral COMlink hardware originaltolerances, fullsignedcircles/alongcross/dedrift/allprefixes retained. Same20mm verticalriser150mmstrip/9m mirrored40+40/.4m approach/allcurb/two-wheel200mm rear support/80env1500controls15sseed20260928. Up23→27/27 anddown27/27 with original1N contact support agreeing, standing26notrequiredcross. Freeze and accept this observed20mmscope only; no thirdCURB20 block/highercurb/globalRM002/STAIR/E1/MoE/permanentantiforgetting graduation orcausalablation claim.\n\nOldflat diagnostics source423→424 negative4pi3/8→0/8, positive8/8, world64/64→60/64 maxcross.057374901m/s, ±1.5errors.027949063/.046887603 retained originalstrictfalse. E0 always frozen/gateuntrained, separateCURB acceptedweights cannot substituteE0 or prove whole-system switching. Source1293c97 and source423e6df exactmatched references preserved.\n\nComplete424 saved trainingtrace1104controls=11.04s/env versus423168=1.68s. Inherited directionhist pluscurrentbeforephysics and endpoint exactly equalsfinalafterupdate; bothsigned andstanding verified. Root-center cross-environments544/590 are exposureproxy, notwheel/contact/fullroute certificates. Allthreeactualtracepath-size-SHA indices preserved. Original hugeSSH exec request10054 readerror and sensor_recipe exact reader assertion retained. Independent minimalarguments reader noGPU and finalsensor-schema reader verified actualimmutable b912 archive source: max_abs_actual_bias_rad is a mutable bias observation emitted after1500controls and resetresamples bias; staticconfig/noisedrawcounts and original.0075bound/finite remained strict. Endmax .007495775→.007467293 difference disclosed; unrecordedinitialbias vectors notfabricated as exact, no physics/runtime/tolerance changes or evaluation replay.\n\nNext approved independentWave35 repair preparation progressed by actualread-only fullsaved oldWave366 trace144controls=1.44s/env, family4 maxabs .29998064/yaw0 and maxgentle nominaldistance .432m verified. Old131 front22/reverse25of27, old2b4 checkpoint unqualified retained. CPUdiagnosis is testableexposure hypothesis, notphysicalpass/causalproof/newtargetCPU ornewlearningdeployment. Nextworkorder requires actualentry/complete10waves/exposurecoverage and newindependent005admission fromreviewed1293c97, notold2b4/CURB7b7003; same-scope evidence SHA reuse and fullCPUCUDA/ownership/episode+1 before boundedlearning, newunused actualfourcase fullreview before furtherPPO. Avoid blindoldWave900s/highergeometry orqueue-onlywork.\n\nCentral complete141/ownfinal/exposure/nextWave metadata CAS and samehourlyACTIVE heartbeat actually verified, protectedmaster/approval/tracks/RM/canonical bytes preserved. Canonical0051188000s330h/7extensions, noadd/copy/clear/recharge, idle674554.278856039s onlysnapshot. E0/SLOPE/CURBfrozen andplayer untouched, gateuntrained/hardwareuncalibrated/S8separateapproval. Allsavedreports/source/errors/false/raw/cost/sync/monitor/workorder/priorGitreceipts completecaptured orsameSHA oldGitref; weights/rawNPZ/USD/ZIP actualpath-size-SHAonly, credentials excluded. LaterstageGitreceipts need ordinarysupplement; originaltags/commits untouched, pushfailure onlyoriginalobjects continuation.\n',encoding='utf8')
 prior={}
 for p in BASE.rglob('*CAPTURE_INDEX.json'):
  for row in json.loads(p.read_bytes()).get('entries',[]):
   if row.get('Git_path') and row.get('archived_sha256'):
    assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256'];prior[row['sha256']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir();rows=[];files=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();sha=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if sha in prior:
   ref=prior[sha];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:txt=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,n=redact(txt);data=clean.encode('utf8') if n else raw
   out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
   row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=n)
  rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_saved_success_failure_reader_source_metadata_monitor_receipts_captured=True,large_originals_retained=True,credentials_excluded=True,later_results_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   q=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),capture_output=True,check=True);return q.stdout.decode().strip()
  return original(*args)
 rec.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Accept complete observed CURB20 route and review next Wave saved exposure','--kind','evaluation','--note-file',str(note),'--files',*files,'--validation','Actual own424 fullsave/CPU104/source424/allnine same-scope CUDA restore/PIDreceipt/unique935.517459s/actualexits/twoOSlocks/idle ledger verified. Fourcase141 complete/fullraw/ground-contact-COM-hardware/fullsignedcircles matched reviewed,20mm observedup/down27/27 accepted only; oldskill diagnostic decline/strictfalse preserved. Fulltrainingexposure11.04s audit and oldWave1.44s savedtrace CPUdiagnosis, originalreaderrors/schema discrepancies retained. Centralmetadata/hourlymonitor actualverified, protectedplan/canonical bytes unchanged, noGPU/replay/expansion/player interference.','--push']
 try:rec.main()
 except BaseException:
  import traceback;save('COMPLETE141_STAGE_RECORD_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),continue_original_objects_only=True));raise
 tag='trial-20261011-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag)
 remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 tracked=set(gitio.g('ls-files').splitlines())
 for row in rows:
  if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 save('COMPLETE141_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,all_current_saved_reports_tracked_exact=True,old_tags_preserved=len(previous),new_capture_files=len(files)))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,new_files=len(files),same_SHA_refs=sum(x['capture']=='same_SHA_existing_Git_reference' for x in rows),largeindices=sum(x['capture']=='large_actual_path_size_SHA_index_only' for x in rows))))

if __name__=='__main__':main()
