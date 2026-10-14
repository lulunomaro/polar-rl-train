"""Unique actual V8 retention repair and reviewed second sameidentity dispatch."""
from pathlib import Path
import importlib,json,sys,subprocess,time
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
FOLDERS=(D,W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014',W/'MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014',W/'MOD4_3060_LEFT_JOINT_MARGIN014_FACTOR_20261014',W/'MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014',W/'MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014',W/'MOD4_3060_FULL80_PARAMETER_BOUND_20261014',W/'MOD4_3060_FULL80_FROZEN_CURRENT_20261014',W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014',W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014',W/'MOD4_LEFT_REPAIR_RESIDUAL_CPU_20261014',W/'MOD4_LEFT_JOINT_CENTER_KEEPSTD_CPU_20261014',W/'MOD4_3060_LEFT_CENTER_KEEPSTD_FULL80_FACTOR_20261014',W/'MOD4_3060_LEFT_NEAR_LOWER_FULL80_FACTOR_20261014',W/'MOD4_LEFT_HEAD_FEATURE_RESPONSE_CPU_20261014',W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014')
def main():
    ID='wave50-retention-v8-pairs-complete-second-sameidentity-started'
    note=D/'RETENTION_V8_COMPLETE_AND_SECOND_SAMEIDENTITY_STAGE.md'
    dest=REPO/'history/evidence'/D.name/'retention_v8_complete_second_sameidentity_stage'
    assert note.is_file() and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID)
    S=W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014'
    decision=json.loads((D/'reports/BEST2B_COMPLETE_FOURCASE_SECOND_SAMEIDENTITY_SCOPE_DECISION_ACTUAL.json').read_bytes())
    target=json.loads((S/'reports/SECOND_ROOT_TARGET_CPU_MATERIALIZATION_COMPLETE.json').read_bytes())
    dispatch=json.loads((S/'reports/SECOND_ROOT_UNIQUE_FORMAL_DISPATCH_ACTUAL.json').read_bytes())
    assert decision['four_frozen_cases_actual_complete'] and decision['sameidentity_second3600_reasonable'] and decision['no_new_policy_axis']
    assert target['passed'] and target['actual_sourcefreeze_count']==541 and target['canonical_bytes_unchanged']
    assert dispatch['pid']>0 and dispatch['second_bounded_formal_seconds']==3600 and not dispatch['PPO_claimed']
    old=cap.a.gitio.refs();cap.a.FOLDERS=FOLDERS;rows,files=cap.capture_streaming(dest)
    sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
    def wrapped(*args):
        if args[:2]==('add','--'):
            p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),capture_output=True,check=True)
            return p.stdout.decode().strip()
        return cap.g(*args)
    rec.git=wrapped
    sys.argv=['record_experiment.py','--id',ID,'--title','Complete native V8 inherited skill pairs, retain regressions, and start reviewed second whole20k sameidentity block','--kind','repair','--note-file',str(note),'--files',*files,'--validation','All3 new V8 native scopes and6 full1500 paired cases completed with original raw/query/contact-integral COMhardware/6000callbacks/firstphysics root30q DRparams assignment capturedRNG queues/source/binding identities and independent full prefix reviews. Straight plusminus1.5 errors improve while original strictfalse retained. Both spin signs0of8 originalyawtol.2; negative spin all8 worsen, ordinary1to1. World62of64to61of64, env60improves27and86regress, originallegacyfalse retained. V8 represented Plane query references own USD/nativeactor getter/fixed publicsource plus actually-loaded DLLsha; originalidealZfalse and V6 strictfailure preserved, no bindingbitexact or shapeLocal calibration claim. Whole best terrain2b20k107float99perenv195tensor and13restore/all9trainingNPZ4536controls audited, Wave50forward22of27reverse25of27 notqualified. Typed13 receipts371negative tests; original schema/path errors retained and new V2 pureguard tested. Independent actual targetCPU10799 storage/disk/36negative and541sourcefreeze with budgetbytes unchanged, resourceguard and originalfirstexit/twofcntlidle checked. Unique new formal parent dispatched secondandlast3600 from same2b, no initializer/newaxis/oldGPUreplay/budgetextension. Dispatch itself not PPO proof; later ownactualsave CPU needed. All raw/source/errors/false/cost/prepared/monitor kept, large actualpathsizeSHA only.','--push']
    rec.main()
    tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID
    head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
    report=D/'reports/RETENTION_V8_SECOND_SAMEIDENTITY_STAGE_GIT_RECORDED.json';assert not report.exists()
    report.write_text(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),actual_saved_sources=len(rows),later_receipt_ordinary_supplement_required=True),indent=2),encoding='utf8')
    print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,actual_saved_sources=len(rows))))
if __name__=='__main__':main()
