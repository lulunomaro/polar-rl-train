"""One annotated stage; all saved successes/refusals and prepared sources are retained."""
from wave_direction_io import *
import subprocess,importlib
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';DEST=REPO/'history/evidence'/D.name/'new_episode_direction424_actual_deployment'
ID='wave50-isolated-episode-direction424-sdk-and-fullstate-started'
def main():
 assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only') and not gitio.g('tag','--list','*'+ID) and not DEST.exists()
 cpu=json.loads((R/'DIRECTION_TARGET_CPU_PASSED.json').read_bytes());assert cpu['passed'] and cpu['source_count']==424
 assert json.loads((R/'DISPATCH_ACTUAL_RECEIPT.json').read_bytes())['actual_Popen_argv_cwd_start_verified'] and json.loads((R/'DIRECTION_DISPATCH_METADATA_SYNCED.json').read_bytes())['passed'] and json.loads((R/'DIRECTION_HOURLY_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['passed']
 actual=json.loads(max(R.glob('DIRECTION_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes());assert 'WAVE50_SDK10_PASSED.json' in actual['reports']
 previous=gitio.refs();save('DIRECTION_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,old_tags=len(previous),prior_main=gitio.g('rev-parse','HEAD')))
 note=R/'WAVE50_DIRECTION424_REAL_STAGE_REPORT.md'
 with note.open('x',encoding='utf8') as f:f.write('''# Independent50mm episode-direction repair deployed

Complete149 allfour fullraw/query/twohost8JSON/contactCOMhardware/ground1e-6/allinitialization/direct148 passed as data-validity only. Actualforward14816/27→1491/27 and reverse24→25 preserved with all26forward+2reverse valid15s failed prefixes, originalfalse/raw/cost. Stopentryduration-only after300+1800, no thirdblindblock/70. Independentnewdirection axis from accepted35 own369b026/17615538B/CPU102, ancestor1293c97; unqualifiedea9/9bfe/219f/a67b/discard/otherexperts notdefaultwarmstart.

Actualnewimmutable root /home/egde/rl_candidates/MOD4_S3_E1_WAVE50_EPISODE_DIRECTION_REVIEWED_20261012/source424=all412oldbytesexact+12 newdirection files. Episode-bound sign fromlegalfullflat resetcell towardwaves; old absrandom vx≤.3/standing.2/vy-yaw/old RNGdraw consumption unchanged, no newRNG. Only Wave boundepisode AND originalcurrentfamily4 modifies signedvx, originalcurrentnonWave/plane command exact. No liveposition/heading correction, aftercrossflip, teacher/truthactor-gate, reward/LR/DR/reset/geometry/route mixedaxis. Original2mtrainingroute cannotcontain frozen3.006m fulltenwave test; entry/onset exposure proxy notcontact/fullroute/causalcertificate.

ActualtargetCPU admitted completeoldsourceD0D7/schema/storage/privatecommand strict-loader fixtures, actual20korigins1600assignments/entrymapf42f0b/2820Wave17180otherexact, originmutationcache/smallnonWave init/production20kzeroWave strictreject, actualruntimeclass fixedepisode direction/absvxstandingRNG/nonWaveparentcommand exact/selectedepisode subset/diskstate/strictwrongassignment-map-origin-profile rejection. IndependentfullsaveCPUfixture actual104 float tensors (source102 plusdirection sign/resetXY), strictbadboundepisode rejection; no CUDA/physicalpass inferred. Sourcefreeze andimport-main-Popen-guardian actualbindings verified, targetCPUactualscope ownsource validated. Initial localI/O module-name collision beforestage, duplicate immutableunusedjob localreceipt afterroot/upload beforeCPU, and AST selection indentation refusal retained originalsource/error; independently onlyunfinishedsteps completed, no oldstage/root/upload/GPU replay. Missingreferencepath readererror retained, notphysicsfault.

Uniquecontroller actualargv/cwd/start/PID verified; newSDK10 PASSED actual10G4cells/twosides/fullflatfootprint/selectedreset/300controls1200callbacks/ground-rewardformula/solver/ordinarynonfinite/auditeddirectionstanding complete300trace. Newnative20k24warm120timed480/576callbacks ownstage governs current actual status. Controller automaticallynewnative ->128x2+20kx4 completePPOdiscard once ->freshsame50entrydirection new20k0control0PPO explicitseed20260928 strictCPUCUDA diskroundtrip/sourceepisode+1 ->first300sloadlearnsaveexit/save25/15slocalguardian fromb026. Oldgeometry/clockDRhardware SHAexactreuse; no45minclock or olddirectionlessGPU claims. SDK/native/preflight/activity do not claimformal final/qualified50. Initialold35actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA/terraincommand exact then explicit35to50actualassignment+entry+newdictdirection identity migration; same50entrydirection futurefullstrict exact, no PhysXexactresume. Ownactualfinalschema/PID/snapshots/PASSED/uniqueparentsegment/actualexit/twofcntl-free/noactive thenactualunusedcandidatepublication/fourcasefullraw/direct149 andfulltrace beforemorePPO/70/qualification, max2bounded≤2h/fullaudit. Complete145/14750protocol/contact1N/.4approach/15s/200mmafter/query1e-6/contactCOMhardware/validprefix/stand26/noresetteleport and115129fullsignedcircle alongcrossdedrift/two4pi/straight originalfalse/finaldynamicbias/staticconfig/.0075 andactualrawlastreset feedback originaltols preserved. Futurefive readonlyreaders prepared/ASTparsed only, not futurepasses.

Central CAS protectedmaster/approval/tracks/RM004 exact; canonical notwritten bysync. Same mod4-10 ACTIVEhourly target actualnativeprompt exact verified, healthyquiet meaningfulstage/majorregression/repair/completion/humanaction only, noextraautomation/5minSSH/ping/Rich/automaticbudget.005 solecanonical1188000s330h/7extensions seventh100h alreadyonce; actualparent PPOloadlearnsaveexit failedstartup uniquecharge; CPU/SDKnativefrozenfresh0PPO nocharge, actualaccountedtail overidlesnapshots/no extensions/copy/clearactive/tail/recharge. Actualfcntlheld≠fileexists/no deletelocks/kill/hotpatch/dual20k/otherAI/WASDGUIresetstoprestart. E0/CURB20/WAVE35/SLOPE ONLYacceptedobserved frozen/gateuntrained/hardwareuncalibrated/S8specificlater/93-94paused, full004005/master/RM/clockDRrewardhardware/healthv3/fullsignedcircle/fivefamilies30+20/20/15/15/otherexpertgate min(18h,.13B) protectedplanning unchanged. No pureteacherS7S870-20-10/permanentantiforgetting/fullRM-MoE claim.

Allsavednewsource/CPU/declaredprepared/readererrors/refusals/unusedsource/dispatch/current receipts/sync/monitor/workorder/Gitreceipt captured, largePTNPZrawJSONUSDZIP actualpath-size-SHA indices onlyoriginalskept/credentials excluded. Unique annotatedrecord_experiment actualremote main/tag/peeled/alloldtags, pushfailurecontinueoriginalobjects no record-tag-commit replay. Later savedreports andstageGitreceipt ordinarysupplement. Gitnottrainingdependency;neverrepeatoldGPU/once/budget forarchiving.
''')
 prior={}
 for p in (REPO/'history/evidence').rglob('*CAPTURE_INDEX.json'):
  for row in json.loads(p.read_bytes()).get('entries',[]):
   if row.get('sha256') and row.get('Git_path') and row.get('archived_sha256'):prior[row['sha256']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();sha=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if sha in prior:
   ref=prior[sha];assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:txt=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,count=redact(txt);data=clean.encode('utf8') if count else raw;out=DEST/D.name/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
   row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=count)
  rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_sources_reports_errors_captured=True,large_originals_retained=True,credentials_excluded=True,later_receipts_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   q=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),capture_output=True,check=True);return q.stdout.decode().strip()
  return original(*args)
 rec.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Deploy isolated Wave50 episode-direction scope after complete149 regression','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Own424targetCPU andfullsavefixture strictpassed, accepted35b026 source/old412bytes exact. Actualuniquecontroller argv/cwd/start andnewSDK10 full300tracePASSED; latestownnative/preflight/fresh/formal stage governs actualstatus. Alloldfailurefalse/raw/cost/readerrefusals retained, centralCAS protected/nativehourly monitor exact verified, no oldonce/GPU orbudget replay.','--push']
 rec.main();tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag)
 remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 tracked=set(gitio.g('ls-files').splitlines())
 for row in rows:
  if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 save('DIRECTION_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(previous),saved_sources=len(rows),all_current_saved_sources_reports_tracked_exact=True))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,saved_sources=len(rows))))
if __name__=='__main__':
 try:main()
 except BaseException:save('STAGE_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_only_no_repeat_record_tag_commit=True));raise
