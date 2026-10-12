"""Archive actual new scope and all retained observer failures; no training dependency."""
from route_fixture_io import *
import importlib,subprocess
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'))
import archive_actual_reference_stage_once as base
REPO=W/'polar-rl-train'
ID='wave50-route4m-fullsave-fixture-repaired443'
DEST=REPO/'history/evidence'/D.name/'independent_route443_actual'
base.FOLDERS=(D,PRIOR)

def main():
    assert not base.gitio.g('status','--porcelain') and not base.gitio.g('diff','--cached','--name-only')
    assert not base.gitio.g('tag','--list','*'+ID) and not DEST.exists() and not (R/'ROUTE443_STAGE_GIT_RECORDED.json').exists()
    for name in ('FIXTURE_REVIEWED_TARGET_CPU_PASSED.json','ROUTE443_ACTUAL_METADATA_SYNCED.json','ROUTE443_HOURLY_MONITOR_ACTUAL_VERIFIED.json','ROUTE443_FINAL_CLOSEOUT_METADATA_SYNCED.json','ROUTE443_FINAL_HOURLY_MONITOR_ACTUAL_VERIFIED.json','ROUTE443_FORMAL_FINAL_ACTUAL_REVIEW.json'):
        assert json.loads((R/name).read_bytes())['passed']
    latest=max(R.glob('ROUTE_FIXTURE_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]))
    actual=json.loads(latest.read_bytes());reports=actual['reports']
    assert actual['source_count']==443 and reports.get('E1_ATTENTION.json') is None
    for name in ('WAVE50_SDK10_PASSED.json','WAVE50_NATIVE20K_PASSED.json','WAVE50_SDK10_ROUTE_GPU_SCOPE_PASSED.json','WAVE50_NATIVE20K_ROUTE_GPU_SCOPE_PASSED.json','wave50_discard128_PASSED.json','wave50_discard20k_PASSED.json','WAVE50_FRESH_PROCESS_SAME_SCOPE_PASSED.json'):
        assert name in reports,name
    old=base.gitio.refs()
    save('ROUTE443_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=base.gitio.g('rev-parse','HEAD'),old_tag_count=len(old),actual_snapshot_path=str(latest),actual_snapshot_SHA=H(latest.read_bytes()),no_old_record_or_training_replayed=True))
    note=D/'ACTUAL_ROUTE443_STAGE_REPORT.md';assert not note.exists()
    own=json.loads((R/'ROUTE443_FORMAL_FINAL_ACTUAL_REVIEW.json').read_bytes())
    assert own['source_count']==443 and own['finite_tensors']==107 and own['actor_tensors_changed']>0 and own['optimizer_step_delta']>0
    note.write_text('''# Independent Wave50 route lifecycle repair and own first300s fullsave complete

Post151 saved completed episodes require actual root displacement2.973834991455078–3.1593399047851562m. The immutable actual old production rough_route_boundary truncates at Chebyshev XY distance>2m from physical-episode spawn. This is an observed exposure gap, not sole causal proof of forward failure or proof all postures are impossible. New axis only gives Wave-born physical episodes4m inwardX travel; outwardX/lateralY/nonWave-born17180 retain exact2m boundary. Fifty-mm geometry/resetXY/episode-fixedtoward direction/absolute command draws-standing.2-vy-yaw0/DR/reward/LR/hardware/clock/family proportions unchanged. Same rough_route_boundary time_out classification/bootstrap and exact reason coverage; frozen .4approach/15s/both-wheel1N/200mm after-support unchanged. No liveheading-position correction/teacher/actor-gate truth/new RNG.

Source439=old426 allbytes+independent route-state/runtime/fullcheckpoint/fullsave/CPU/SDK/PPO/fresh/controller/005guard components. TargetCPU20k2820Wave/17180other exact, strict profile-assignment-map-origin-parentBoundarySHA-episode-anchor-limit fixtures and diskrestore/noCUDA passed. Initial wrapper omitted inherited saved expert/source-header assertions while validating route/parentSHA; that coverage gap disclosed and retainedCPUcomponent only. Source440=439 exact+unique source-reviewedwrapper keeps original expert/initialb026 header assertions; fullCPU107 fixture(originalsource102) and10strict wrong-state/source rejections passed before unique dispatch.

Old440SDK actually completed300controls before post-physics CUDA shadow fixture failed because plain-dict Scene lacks env_origins for eagerly evaluated getattr default. Original error/source/log/PID/attention/partialtrace retained; full physical result was not saved, so440SDK is not admitted from CPU inference or reconstructed physical data. ZeroPPO/canonicalunchanged classification retained. Actual parent-guardian-SDKchild exits, two fcntl locksfree and active-Sactive empty checked before new443.

Source443=440 exact+three independent fixture-probe-controller files. Only shadow Scene mapping+attribute API fixed; complete physical report saved before postfixture. Same real route/old boundary functions and actual physics-loop source preserved. Shadowfixture is CUDA tensor math, no physical step/teleport/progress credit. CPU fixture initially imported whole SDK runtime before AppLauncher and was rejected with isaaclab_physx ImportError before proof/dispatch/GPU; original error retained. Independent continuation extracts immutable original boundary functionAST for noCUDA CPU check, then completes only previously unexecuted CPU/dispatch. No old440/439/426 main/resume/once or failure eval replay.

Actual443targetCPU/sourcefreeze and unique controller dispatch verified. OwnSDK10 actual10G4 cells/fullfootprint/300control1200callbacks and native20k24warm120timed480/576callbacks, physical ground/reward/DR/solver/health and CUDA4m-vs-original2m boundary fixtures PASSED. Two actual complete native traces independently audit signedtoward and standing on both entry sides, not fullroute/circle/contact certification. New128x2 and20kx4 fullPPOdiscard weights/PID/ownfullsave/PASSED and original unique canonical closeouts passed; independent freshsame50-entry-direction-route20k0control0PPO seed20260928 strict CPUCUDA roundtrip/sourceepisode+1 passed. First300s load-learn-save-exit automatically started from accepted35own369b026, not discarded weights. Actual own final/positive actoroptimizer/exit/unique account/candidate scope only when independently reported later; no graduation or claimed forward causal improvement from process/shortprefix.

Fullstate original35 actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA/oldterraincommand identity first exact, explicit new50-entry-direction-route migration/CUDA diskroundtrip/sourceepisode+1. Private route dict contains identity/mask/sign/episode/spawn/limits/counts; no oldnamed mixing or RNG draws. Ownfixture and eventual real GPUfinite107 must be independently bound to source443 and saved bytes; CPUfixture/discard never substitutes formal ownsave. After ownfullsave/PID/PASSED/unique originalparent settlement/actual exits/two locksfree/idle, ownparent publishes new fourcases using actual unused candidate number. Full raw/query/6000callbacks/root30q-params-staticrecipes-assignment/contactCOMhardware and115129diagnostics/direct151/complete dynamic-family trainingtrace remain required before next bounded block/70. No blind third same-scope duration block/no wholeRM-MoE/permanentantiforgetting claim.

Only durable ext4 actualfree resource evidence used: twice completed first300s pipeline614471041B +2GiB +twice positive source delta +newstate-file margin admitted. No raw/weights/source/environment/cache deletion, reduced resource ratio, tmpfs escape or unlimited long-run claim.0051188000s330h/sevenextensions seventh100h alreadyonce; actual parent uniquely accounts PPOloadlearnsaveexit/failedstartup, CPU-SDK-native-frozen-fresh0PPO no charge; no copied ledger/clearactive/tail/recharge/extension/autobudget. E0/accepted35/CURB20/SLOPE scopes frozen/gateuntrained/hardwareuncalibrated/S8specificapproval/93-94paused/WASD untouched. ClockDRrewardhealthcontactqueryfullcircle original tolerances retained.

Protected centralCAS uploaded actual439/440CPU-disclosure/failure/443CPUdispatch-SDKnative-current/resource-reader-error/workorder with masterapprovaltracksRM004 protected/no canonicalwrite. Same mod4-10 native heartbeat ACTIVE hourly target/quiet healthy intent verified against actual TOML, requested-vs-native whitespace-only hashes retained. All saved local newsource, failed440trace index, observer/schema/rejected/unusedpreparation, resource, successfulactual, monitor/sync/workorder/Gitreceipt captured. Largeoriginals realpath-size-SHA only/originals retained; credentials redacted, not exposed. Newrealstage unique annotatedrecord_experiment; actualremote main/tag/peeled/alloldobjects and trackedSHA verified. Later reports/receipt ordinarysupplement; Git does not pause or restart training.

Actual own formal checkpoint SHA'''+own['checkpoint']['sha256']+'''/'''+str(own['checkpoint_bytes'])+'''B/CPU107/source443/'''+str(own['actual_module_snapshot_count'])+'''module snapshots+ownfreeze;6updates144controls2.88Menvsteps576callbacks,9actorchanged/optimizerdelta120. Alltenstartup initialold35exact→new50-entry-direction-route CUDAroundtrip/sourceepisode+1 verified. Ordinary-integrity-unknown0/nonfinitefalse/STOPnone/closure.859745079651475mm/mimic.0016914558364078403rad; timeout1469/route1/unique1470 and bothcoverageexact. Unique330.2157027721405s originalparent once accounted; actualparentguardianchild exits/twofcntlFree/active-Sactive empty verified. Full144control savedNPZ/dynamicfamily4/two signedstanding/prereset-before/tracehistphase CPUreviewpassed; eachenv1.44s/rootcommandproxy notalltenwaves/contact/causality. Ownparent actuallypublished152fourcases; collection/partialreview pendinghealthy, no future terrainpass from fullsave. Newformal-final/trace/candidatepending protected centralCAS and samehourlymonitor nativeactual verified.

Current actual collection: '''+str(latest)+'''; phase='''+reports['E1_STATE.json']['phase']+'''. Future actual candidate overrides this snapshot.
''',encoding='utf8')
    rows,files=base.capture(DEST)
    sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment');original=rec.git
    def short_git(*args):
        if args[:2]==('add','--'):
            r=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in args[2:]),capture_output=True,check=True);return r.stdout.decode().strip()
        return original(*args)
    rec.git=short_git
    sys.argv=['record_experiment.py','--id',ID,'--title','Repair Wave50 episode route bound and verify independent443 fullsave','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Original2m production boundary and observed completed3m paths audited. NewWave inward4m only; strict fullstate CPU and CUDA SDK/native own scope passed.440 postfixture failure and SDK-import CPU reader rejection retained. Small/big discard/fresh ownPASSED; ownfirst300s b026→newscope fullsaveCPU107/source443/positive9actoroptimizer120/tenstartup/unique330.2157s/exits-locks-idle verified,144control fulltrace reviewed.152actualfourcases healthy pending. ProtectedcentralCAS/hourlyactualmonitor. No oldonce replay/threshold-DR changes/budgettransaction.','--push']
    rec.main()
    tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID
    head=base.gitio.g('rev-parse','HEAD');obj=base.gitio.g('rev-parse',tag);base.verify(rows,old,head,tag,obj)
    save('ROUTE443_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,old_tag_count_preserved=len(old),captured_sources=len(rows),all_current_saved_evidence_tracked_SHA_verified=True,push_pending=False,later_reports_receipts_require_ordinary_supplement=True))
    print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,captured_sources=len(rows),oldtags=len(old))))

if __name__=='__main__':
    try:main()
    except BaseException:save('ROUTE443_STAGE_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_existing_objects_no_record_tag_commit_replay=True));raise
