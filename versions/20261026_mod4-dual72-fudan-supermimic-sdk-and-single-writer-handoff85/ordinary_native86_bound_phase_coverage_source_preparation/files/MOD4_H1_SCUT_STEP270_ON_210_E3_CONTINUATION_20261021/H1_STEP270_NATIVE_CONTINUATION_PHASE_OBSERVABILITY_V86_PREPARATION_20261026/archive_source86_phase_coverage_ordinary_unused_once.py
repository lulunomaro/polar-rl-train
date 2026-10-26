from pathlib import Path
import importlib.util,json,time,traceback
F=Path(__file__).resolve().parent;T=F.parent;W=T.parent;G=W/'polar-rl-train';R=F/'reports'
N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026'
path=N/'archive_closed85_native_Fudan_and_E3_ordinary_unused_once.py'
spec=importlib.util.spec_from_file_location('previous_ordinary85_definitions_only',path);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
s=base.s
def patch(a,b):
 global s
 assert s.count(a)==1,a;s=s.replace(a,b,1)
patch('ordinary_closed85_native_Fudan_E3_and_continuation_prep','ordinary_native86_bound_phase_coverage_source_preparation')
patch("nr=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026'/'reports'","nr=T/'H1_STEP270_NATIVE_CONTINUATION_PHASE_OBSERVABILITY_V86_PREPARATION_20261026'/'reports'")
s=s.replace('ACTUAL_ORDINARY_CLOSED85_NATIVE_FUDAN_E3_GIT_NOTE','ACTUAL_ORDINARY_NATIVE86_SOURCE_PHASE_COVERAGE_GIT_NOTE')
s=s.replace('ORDINARY_CLOSED85_NATIVE_FUDAN_E3_ARCHIVE_STARTED','ORDINARY_NATIVE86_SOURCE_PHASE_COVERAGE_ARCHIVE_STARTED')
ns={'__name__':'native86_source_ordinary_capture_only','__file__':str(base.m.m.engine)};exec(compile(s,str(base.m.m.engine),'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='f1643f090b43df7b8156f7f38b7cd11abf1aadd4' and len(git('tag','--list').splitlines())==1456 and not git('status','--porcelain')
 previous=G/'versions/20261026_mod4-dual72-fudan-supermimic-sdk-and-single-writer-handoff85'
 ns['prior'](previous/'COMPLETE_FILE_CAPTURE_INDEX.json');ns['prior'](previous/'ordinary_closed85_native_Fudan_E3_and_continuation_prep/ORDINARY_CAPTURE_INDEX.json')
 work=json.loads((R/'CURRENT_SOURCE_ONLY86_BOUND_NATIVE_PHASE_DIAGNOSTIC_WORK_ORDER_ACTUAL.json').read_bytes())
 assert not work['actual_installed86_SDK_source_CPU'] and not work['payload_Task_controller_GO_or_fee']
 note='''Ordinary source-only supplement to consumed85 trial, no record/tag. Bound actual qualified85 formal native FINAL/CPU/original72cost/allout/runtime order metadata; no PT load/hash/copy or network/GPU/physics. The metadata compatibility test deliberately reuses saved85 runtime order as a same-source CPU fixture, not a fresh86 SDK admission. Typed native source94e7f272 and separate frozen83B bootstrap829700 remain distinct, E3 latest qualified85update87/862540. No newpayload, Task, controller, installed86source, GO or fee.

Bridge differs from frozen nativecontinuation candidate only exact optional phase-sampling import+attachment afterrestore. Trainedweights/3optimizers/globaliteration68 and original newepisode/fresh48replay contract unchanged. Optional hook records actual sampledstart ages once perPi, no percontrol GPUread/extraactorforward/RNG/physics/reward/action/sampling change; attemptedstarts are not successfulupdates/physicalevents. Synthetic8/8 forwarding/RNG/originalexception/optionaltransfer+IO/invalidframe/boundary/doublehook tests passed; intentional optional-I/O error artifacts and source preserved. SourceAST equality after removing exact two nodes passed. No source-only evidence is a runtime skill or performance claim.

ThreeGPU sole72controller/typedsource+worker/strict210-to72control dependency admission remains the next implementation task, concretely specified in the handoff. Old210canonical/fence staysretired, currentfinite72account and strict86412.86069250107/actualGO-terminal3900/3600/300 untouched. Original physics/reward/commands/270dualwheeltopcontact200callbacksuccess/trace/retention/fullsave unchanged. No blind identicalrun, oldonce, modelreread or ledgerwrite. Existing1456tagobjects/peels protected. All newsource/metadata/CPU/fixture/errors/monitor text captured; postGit verification conversationonly. Healthy source-onlypending staysquiet.
'''
 ns['run_stage']('fudan',[F],[Path(__file__)],note,'Prepare native86 typed source binding and optional phase sampling coverage')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SOURCE86_ORDINARY_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as out:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),no_second_record_or_tag=True),out,indent=2)
  raise
