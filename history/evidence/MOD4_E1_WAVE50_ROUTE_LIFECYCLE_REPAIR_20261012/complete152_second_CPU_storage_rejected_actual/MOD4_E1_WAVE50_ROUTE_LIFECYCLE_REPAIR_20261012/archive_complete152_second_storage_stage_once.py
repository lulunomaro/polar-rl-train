"""One new diagnosis/rejection trial, then ordinary supplement for its Git receipt."""
from route_fixture_io import *
import importlib,subprocess
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'))
import archive_actual_reference_stage_once as archive
REPO=W/'polar-rl-train';SECOND=W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012'
ID='wave50-full152-second-route-cpu-prepared-storage-rejected'
DEST=REPO/'history/evidence'/D.name/'complete152_second_CPU_storage_rejected_actual'
archive.FOLDERS=(D,SECOND)

def main():
    assert not archive.gitio.g('status','--porcelain') and not archive.gitio.g('diff','--cached','--name-only')
    assert not archive.gitio.g('tag','--list','*'+ID) and not DEST.exists()
    decision=json.loads((R/'COMPLETE152_ROUTE_SECOND_SCOPE_DECISION.json').read_bytes());storage=json.loads((SECOND/'reports/SECOND1800_DURABLE_STORAGE_ADMISSION_ACTUAL.json').read_bytes())
    assert decision['all_four_actual_complete_errorfree_fullraw_reviewed'] and not decision['qualified50'] and not storage['passed']
    for name in ('COMPLETE152_SECOND_STORAGE_METADATA_SYNCED.json','COMPLETE152_SECOND_STORAGE_MONITOR_ACTUAL_VERIFIED.json'):assert json.loads((R/name).read_bytes())['passed']
    old=archive.gitio.refs()
    save('COMPLETE152_SECOND_STORAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=archive.gitio.g('rev-parse','HEAD'),old_tag_count=len(old),all_prepared_unused_and_reader_error_sources_retained=True))
    save('SECOND1800_HUMAN_STORAGE_ACTION_REQUESTED.json',dict(epoch=time.time(),request_user_input_async_accepted=True,requested_action='free_at_least3GB_nontraining_data_space_or_supply_writable_durable_directory',protected_training_evidence_source_weights_environment_cache_must_remain=True,actual_free_bytes=storage['resources']['actual_durable_free_bytes'],required_bytes=storage['resources']['required_second1800_bytes'],shortfall_bytes=storage['resources']['shortfall_bytes'],response_not_yet_received=True,not_permission_to_delete_files_or_start_before_actual_admission=True))
    note=D/'ACTUAL_COMPLETE152_SECOND_CPU_STORAGE_STAGE_REPORT.md';assert not note.exists()
    note.write_text('''# Complete152 full raw review; same-route second1800 prepared, durable storage rejected

Own443 first300 fullsave completed withCPU107/68401c/source443/100actual module snapshots+ownfreeze/PID3274916/6updates144controls2.88Msteps576callbacks/positive9actor tensors andoptimizerdelta120/PASSED/unique330.2157027721405s originalparentonce/actualparentguardianchild exits/twofcntlFree/active-Sactive empty. Newroute only Wave-born inward2→4m; oldoutward/lateral/nonWave2m exact. Complete144control trace1.44s/env auditeddynamiccurrentrootcellfamily4/two signedtoward-standing/prereset-before/beforephysicscommands vsafterupdatehist. Rootproxy is not fullroute/contact/learningcausality. Geometry/resetXY/episodefixedtoward/absolute draws-standing.2/vy-yaw0/DRrewardLRhardwareclock/family proportions unchanged; frozen15s/.4approach/1N/after200mm untouched.

152 allfour actualcomplete/errorfree/twohost8JSON byteSHA/fullraw182821946B SHA2452d4c4c36a2cfc0d32aa3f14c17ded7ba2477b3d3ccfd2c9a8fed2e2aaffc7/queryNPZ/root30q-parameters-staticrecipes-assignments/6000callbacks/actualfloat32query ground1e-6/contactintegralCOMhardware fullreview passed. Same50mm tenwaves2.406422727m/.4approach/twowheel1N/fulltenwaves+200mm after-support/80env1500controls15s20260928white3. Forward12/27 reverse25/27/ordinary0/route4/closure1.1957105016335845mm; standing26 no traversal requirement. Data-contract pass not50mm qualification. Allvalidfailedprefixes/declaredtruncation exactcoverage/noresetteleport/originalfalse retained. Direct1519forward26reverse fullinitial30q-parameters-staticrecipes-assignments exact: forward regressed6,30,60,69,75 and improved24,33,36,39,45,48,51,57; reverse regressed4,64 improved19. Negative4pi0/8 positive7/8/world63/64 maxcross.051384614 and ±1.5errors.066174537/.045016099 are retaineddiagnostics, E0frozen/gateuntrained, no expert substitution. No invented27/27 or90/95/100promotiongate/no qualified50/fullRM-MoE/70/permanentantiforgetting.

A sameidentity independent second1800 window is concretely prepared because newroute first300 gave only1.44s/env exposure. Sourceonly own443model32264 SHA68401cae6402c5aa38797dabdbb7043f8036ed6fcbacd9c34fda0bdd95a813c5/18701417B/CPU107, accepted35b026/1293c97 ancestry exact; this is a sameexpert continuation source, not qualified50 or otherexpertdefault. Three localnewfiles: same-scope-manifest-only worker, explicit005sevenextensions and sourceguard, unique secondcontroller. Expected old443allbytes+3=446, no actualnewroot/sourcefreeze/targetfullstateCPU/GPU/PPO/controllerdispatch yet. CPUcomponent against actualsaved107 verifies fullCPU/privatecommand diskfixtures, separateactorcriticoptimizer storage, wrongprofile-assignment-map-origin-parentboundarySHA-episode-spawn-limit-initialsource-expert strictrejection, noRNGdraw/noCUDA. Originalobserver incorrectly used command-only equality on full checkpoint containingtuple/tensors and failed before proof/targetroot/GPU; originalsource/error retained. IndependentcompleteCPU-tree equality handles exactdtype-shape torch/numpy/listtuple without productionvalidator changes; subsequentcomponentCPU passed. Actualtarget import-main-Popen-root-guardian binding/CUDA startup stillfuture andmustnot be claimed fromcomponent.

Fresh actual durable storage guard refused new1800 scope: ext4 free2801319936B, required5284658838B, deficit2483338902B; RAM59500097536B healthy. Required=2×realcompleted1800wholeoutput1515186413B+2GiB+2×positive source delta601182B+105600000B route-state-file margin. Newtargetroot notcreated, noPPOattempt/control/charge/candidate-numberpreclaim. Humanresource action requested via native asynctextquestion: free at least3GB nontraining data or provide writable durable directory; evidence-source-weights-env-cache remainprotected. No loweredguard/tmpfs/deletion or automaticbudget. This is storageadmission rejection, not physics/PPO failure. Actualcapacity andfulloldsource-save/exits-twofcntl-idle must be reread before future genuine targetCPU107/source446 and unique1800dispatch. Original443SDK/native/smallbig/fresh/clockDRgeometryhardware PASSED path-size-SHA reused; no oldGPUpreflight/once replay. Same50entrydirectionroute fullCPUCUDA exact/geometry-command-privateRNG/episode+1/newflagsfalse, notPhysXexactresume; ownnewfullsave/PID/PASSED/uniquecloseout/actualexit locks idle then newactualunusednumber fourcase/direct152/fulltrace. Currentroute block count1(first300); max2/fullaudit, no thirdblinddurationblock/70, systemicresidual noimprovement independentdiagnosis.

ProtectedcentralCAS full152/direct151/decision/componentCPU/resource rejection/originalreadererror/newworkorder withmasterapprovaltracksRM004 protected andno canonicalwrite. Same mod4-10 heartbeatACTIVE hourlytarget/quiethealthy nativeTOML exact prompt(normalized trailingwhitespaceonly) verified; noadditionalmonitor.005solecanonical1188000/7extensions seventh100h alreadyonce; actualaccountedtail priority/noledgercopy-clearactive-tail-recharge-extension, CPU-SDKnative-frozen-fresh0PPO nocharge. E0/accepted35-CURB20-SLOPEobservedfreeze/gateuntrained/hardwareuncalibrated/S8specificapproval/93-94paused/WASD noGUIresetstoprestart; fixed004005masterRM clockDRrewardLRhardwarehealthquerycontactfullcircle tolerances andotherexpertgate protections unchanged. Allretainednew source/report/error/unusedpreparation/rawcost/syncmonitor/humanaction/workorder captured; large originals realpathsizeSHA indexonly/originalskept, credentials excluded. Newactualdiagnosis/rejection uniqueannotatedrecord_experiment; remote main-tag-peeled/alloldobjects andtrackedSHA verified, laterreceipt ordinarysupplement. Git doesnot pause/start/modify training or repeat oldonce; pushfailure continueexistingobjects only.
''',encoding='utf8')
    rows,files=archive.capture(DEST)
    sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment');original=rec.git
    def short_git(*args):
      if args[:2]==('add','--'):
        p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
      return original(*args)
    rec.git=short_git
    sys.argv=['record_experiment.py','--id',ID,'--title','Review complete152 and preserve second-route CPU preparation storage rejection','--kind','diagnostic','--note-file',str(note),'--files',*files,'--validation','152fourcase fullraw-query/twohost8JSON/root30q-paramsrecipesassignments/6000callbacks-groundcontactCOMhardware/direct151 reviewed:12forward25reverse, allfalse-prefixes retained. Sameidentity107CPUcomponents prepared source443+3 expected446; tuple-tensor observererror and independentCPUtree correction preserved. Actual1800durablefree2.801GB vsrequired5.285GB rejected beforetargetroot-GPU-PPO. Humanstorageaction requested. ProtectedCAS/nativehourlymonitor; nooldonce/GPU replay/budgettransaction/threshold changes.','--push'];rec.main()
    tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=archive.gitio.g('rev-parse','HEAD');obj=archive.gitio.g('rev-parse',tag);archive.verify(rows,old,head,tag,obj)
    save('COMPLETE152_SECOND_STORAGE_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(old),captured_sources=len(rows),all_current_saved_evidence_tracked_or_actual_large_SHA_index=True))
    newer=archive.gitio.refs();dest=REPO/'history/evidence'/D.name/'complete152_storage_stage_receipt_ordinary_supplement'
    later,paths=archive.capture(dest)
    subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in paths),capture_output=True,check=True)
    archive.gitio.g('commit','-m','Supplement verified complete152 storage-rejection stage receipt');archive.gitio.g('push','origin','HEAD');supp=archive.gitio.g('rev-parse','HEAD');archive.verify(later,newer,supp)
    current={r['source_path']:r for r in later}
    for folder in archive.FOLDERS:
      for p in folder.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        assert current[str(p.resolve())]['sha256']==H(p.read_bytes())
    print(json.dumps(dict(stage_commit=head,tag=tag,tagobject=obj,supplement_commit=supp,actual_remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),total_tags=len(newer),all_current_saved_sources_reports_SHA_tracked_or_actual_large_index=True,captured_sources=len(later),no_unrecorded_stage_receipt=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('COMPLETE152_STORAGE_STAGE_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_existing_objects_no_record_tag_commit_replay=True));raise
