"""Unique real repair/deployment stage; originals and all preparation failures retained."""
from entry_io import *
import subprocess,importlib
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';DEST=REPO/'history/evidence'/D.name/'initialization_reviewed_entry410_scope'
ID='wave50-entry-initialization-repair-independent-scope-started'
def main():
 assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only') and not gitio.g('tag','--list','*'+ID) and not DEST.exists()
 cpu=json.loads((R/'INITIALIZATION_REVIEWED_TARGET_CPU_PASSED.json').read_bytes());assert cpu['passed'] and cpu['source_count']==410
 dispatch=json.loads((R/'INITIALIZATION_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json').read_bytes());assert dispatch['actual_Popen_argv_cwd_start_verified']
 assert json.loads((R/'ENTRY_HOURLY_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['passed'] and json.loads((R/'ENTRY_METADATA_SYNCED.json').read_bytes())['passed']
 actual=json.loads(max(R.glob('INITIALIZATION_REVIEWED_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes())
 previous=gitio.refs();save('ENTRY_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,old_tags=len(previous),prior_main=gitio.g('rev-parse','HEAD')))
 note=R/'ENTRY_INITIALIZATION_REPAIR_STAGE_REPORT.md'
 with note.open('x',encoding='utf8') as f:f.write('''# Independent WAVE50 reset-entry scope deployed; initialization failure retained

The completed147 valid50mm audit remained forward5/27 reverse25/27 after two duration-only blocks; it is notqualified50. No third blind duration-only block or70mm promotion was launched. The accepted35mm own369 b026/17615538B/CPU102 and full1293c97 ancestry is the selected initial source, not degraded219f/a67b/discard oranotherexpert. New work changes only deterministic resetXY positions for2820 actualWave origins; other17180 unchanged. Original geometry, DR, command/RNG consumption, reward/LR/clock/hardware/fivefamilies/health thresholds and2m route remain. The existing tested component mapSHA f42f0b15333c9bedd903921e191940cc0a9e9d3042fd354053f74d5c1ee0eb0d places fullbank25200point footprint onflatapproach twoX-side separatedlanes andYcellbounds, frontsupport at least.517m. Origin/assignment/bank/profile/sourcefile identity cache and independentlydictowned checkpoint identity were added. Fullposeq30/normal/clearance/zero velocity AST exact exceptXYlookup. Entry exposure is approach/onset/partialwave training; original2m route cannot certify complete3.006m frozen route, rootproxy is notcontact orcausalproof.

First immutable source398 cloned384 allbytes and14new files, passed actualtargetCPU strictoldsource/fullD0D7/privatecommand fixture/cacheoriginmutation/storage/boundidentity rejection. SDK GPU initialization then failed before control/PPO: RslRl wrapper reset precedes diagnostic Wave placement, initial10origins were nonWave and strict v1 entry_map rejected No actual Wave origins. Error/log/attention/sources and actual parentguardianchild exit/twofcntl-free/idlecanonical boundary preserved, noPPO charge. No398controller/SDK was resumed or replayed. New source410 cloned398 unchanged plus12 versioned v2 files. v2 initialization handles proven allnonWave smallfixtures(n<20000) with exactunchangedorigins; zeroWave production20k stillstrictrejects, anyWave uses originalv1math byteexact. No geometry/physics/health/source/RNGvalidator relaxation. Lazy simulationconfigure import separatedfrompure CPU fixture withoutimporting AppLauncher. NewtargetCPU passed actual20k map, full1600assignment/privatecommand CPU roundtrip, origin invalidation/smallnonWaveidentity andempty20k rejection, independentstorage andsourcepreservation, controllerimport/main/Popen root andseedguards. Exact newfullposeAST andsame-entryrestore wrongmap/origin/assignment/input identities rejected. Initial old35 identity restored then explicit35to50assignment+entryscope/CUDAroundtrip/episode+1 is required by ownruntime; later same50entry exact, notPhysXexactresume.

Source410 unique controller actuallydispatched, PID3064496-start90661954 as an historical locator only. Ownactual /proc argv/cwd/start/receipt/stage supersedes snapshot. Its newentry SDK10 actuallypassed10G4cells/bothsides/fullflatfootprint/selectedreset300control1200callback. Newentry native20k actuallypassed24warm120timed/480timed576totalcallbacks, actualallresetXYmap/groundheight/rewardformula/solver32-4/actionformula/ordinary-integrity andcomplete144controltrace two signedgentle+standing onbothsides. Native fullrawJSON/trace keptremote andpathsizeSHA indexed. Small128x2 completePPOownfullsave/PID/CPU/PASSED/uniqueaccounting passed andweightsdiscarded. Big20kx4/freshsameentry/formal300s automatically follow onlyownactualPASSED; current savedstages at archive are recorded below, never infer futurepass orformal fromCPU/SDK/native/process. Completeformal ownfullsave/PID/sourcefreeze/module snapshots/PASSED/actualCPU/uniqueoriginalcanonical settle andactualexit beforeparentautomatic newfourcase. Candidate148 reserved onlybyactual bothhostunused checks, readactualpublicationnumber anddo notrepublish. Frozen50 wholetenwave protocol145/147 and115/129 legacy originalfalse/prefix/groundquerycontactCOMhardware/fullsignedcircles thresholds remain; fullcandidate+trainingtrace beforecontinuation/70/qualified50/RM/MoE/permanentantiforgetting. Justifiedentryscope max2boundedblocks≤2h afterfullreview, noautomaticthird.

Original localanchor/path/schema/import/explicitassignmentCPUfixture/externalasset-reader errors andprelaunchsyntax rejection preserved, notphysicalfaults. An8GiB precreation resourceguard rejected actual7.69GiB free; independent measuredshortscope guard required2xactual completedpriorwholeoutput+2GiB headroom andpassed, withnoevidence/cache/environment deletion. Native automation trimsone trailingnewline; failed rawprompt-reader assertion andexactnative normalization proof kept. Central selectedscope CAS andreports copied, master/approval/tracks/RM004protected, canonical never writtenbysync. Sameexistingmod4-10 ACTIVEhourlytarget actualsettingsverified, quiethealthy/meaningfulnotification only; noextraautomation.

Allsaved attempts/false/raw/errors/source/CPU/GPUreceipts/sync/monitor/workorder capturedorexactexistingGitSHAreferenced, PTNPZrawJSONUSDZIP indexedoriginalskept, credentials excluded. This is a newreal entry-axis repair/deployment stage, not rerun prior trials. Allpoststage receipts/reports needordinarysupplement; failedpush mustcontinueoriginalobjects only. 005canonical1188000s330h/sevenextensions seventh100h alreadyonce/noextensioncopyclear-tail-recharge. PPOloadlearnsaveexit failedstartup parentunique; CPU/SDK/native/frozen/fresh0PPO nocharge. Activeactualaccountedtail supersedes snapshots. Actualfcntl locks/persistentfile distinction/no killhotpatchdual20k/otherAI/WASD. E0/CURB20/SLOPE5-8-10/WAVE35 acceptedobserved scopesfrozen; gateuntrained/hardwareuncalibrated/S8specificlater/93-94paused; allfixed approved contracts andotherexpertgate/min(18h,.13B) planning remain.
'''+ '\nActual archive snapshot phase: '+str((actual['current_state'] or {}).get('phase'))+'\nOwn passed stage receipts: '+json.dumps([k for k in actual['reports'] if k.endswith('PASSED.json')])+'\nAttention: '+json.dumps(actual['reports'].get('E1_ATTENTION.json'))+'\n')
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
   clean,count=redact(txt);data=clean.encode('utf8') if count else raw
   out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
   row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=count)
  rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_saved_entry_repair_sources_reports_failures_captured=True,large_originals_retained=True,credentials_excluded=True,later_receipts_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   q=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),capture_output=True,check=True);return q.stdout.decode().strip()
  return original(*args)
 rec.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Repair Wave50 entry initialization and deploy independent fullstate learning scope','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Actual410targetCPU/map/cache/strictsource andresetAST passed; failed398precontrolSDK andallreader/preparation failures retained. New410SDK10/native20k completeactualentryscope andsmall128x2 fullPPO passed, remaining stages followownPASSED only. CentralCASprotected/hourlymonitor actualverified,allrawfalse unchanged.','--push']
 rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag)
 remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 tracked=set(gitio.g('ls-files').splitlines())
 for row in rows:
  if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 save('ENTRY_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(previous),saved_sources=len(rows),all_current_saved_entry_repair_sources_reports_tracked_exact=True))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,saved_sources=len(rows))))
if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_STAGE_RECORD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_only_no_repeat_record_tag_commit=True));raise
