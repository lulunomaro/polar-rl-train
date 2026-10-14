from pathlib import Path
import json,time,sys,subprocess,importlib
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
def main():
    ID='wave50-left-exploration-first-final-full80-22-25'
    note=D/'LEFT_FIRST_FORMAL_FINAL_FULL80_STAGE.md';dest=REPO/'history/evidence'/D.name/'left_first_final_full80_22_25_stage'
    assert note.exists() and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID)
    old=cap.a.gitio.refs();cap.a.FOLDERS=(D,W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014',W/'MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014',W/'MOD4_3060_LEFT_JOINT_MARGIN014_FACTOR_20261014',W/'MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014',W/'MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014',W/'MOD4_3060_FULL80_PARAMETER_BOUND_20261014',W/'MOD4_3060_FULL80_FROZEN_CURRENT_20261014',W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014',W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014',W/'MOD4_LEFT_REPAIR_RESIDUAL_CPU_20261014')
    rows,files=cap.capture_streaming(dest)
    sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
    def wrapped(*args):
        if args[:2]==('add','--'):
            p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
        return cap.g(*args)
    rec.git=wrapped
    sys.argv=['record_experiment.py','--id',ID,'--title','Complete whole20k left exploration first formal and paired full80 terrain improvement with residual regressions','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Own whole20k final32635 SHA2b full10799/189updates90.72Msteps/actor9Adam3780/13strict restore/522sourcefreeze/3624.510s unique original settlement/actualexit-twofcntlFree-idle; full9NPZ2.64GB all4536controls/resetunion/dynamicfamily/signed/40s prefix actual CPU reviewed, ordinary275 and closure2.8768mm legacyfalse retained. New3060 full80 source2b ground1e-6/contactintegralCOMhardware/6000cb/fullvalidprefix actual reviewed: forward7to22of27 (15 improvements,no regression), reverse27to25 (2 regressions), ordinary0; all initialrootq30/physicalrecipesassignment/capturedRNG and queue exact. Residual5forward2reverse actualCPU: continuousyaw/one slowdown, leftjointguard99.998765percent persists and stdactual0.677323, no unique causal claim. Original three inherited skills seed20261002/80-88-88/1500 preserved; CPUports and observers/mocked phase tests prepared, original drafts/schema/seed/API issues retained; only newnativeflat120 dispatched pending, no furtherPPO/qualification claimed.','--push'];rec.main()
    tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
    p=D/'reports/LEFT_FIRST_FINAL_FULL80_22_25_STAGE_GIT_RECORDED.json';p.write_text(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),actual_saved_sources=len(rows),later_receipt_ordinary_supplement_required=True),indent=2),encoding='utf8');print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,actual_saved_sources=len(rows))))
if __name__=='__main__':main()
