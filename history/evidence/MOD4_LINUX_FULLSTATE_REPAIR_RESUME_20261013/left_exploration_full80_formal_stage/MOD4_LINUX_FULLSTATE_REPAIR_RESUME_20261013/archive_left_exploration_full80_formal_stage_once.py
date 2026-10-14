from pathlib import Path
import json,time,sys,subprocess,importlib
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
def main():
    ID='wave50-full80-left-exploration-admitted-formal-started'
    note=D/'LEFT_EXPLORATION_FULL80_FORMAL_STAGE.md';dest=REPO/'history/evidence'/D.name/'left_exploration_full80_formal_stage'
    assert note.exists() and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID)
    old=cap.a.gitio.refs();cap.a.FOLDERS=(D,W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014',W/'MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014',W/'MOD4_3060_LEFT_JOINT_MARGIN014_FACTOR_20261014',W/'MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014',W/'MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014',W/'MOD4_3060_FULL80_PARAMETER_BOUND_20261014',W/'MOD4_3060_FULL80_FROZEN_CURRENT_20261014')
    rows,files=cap.capture_streaming(dest)
    sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
    def wrapped(*args):
        if args[:2]==('add','--'):
            p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
        return cap.g(*args)
    rec.git=wrapped
    sys.argv=['record_experiment.py','--id',ID,'--title','Review full80 terrain baseline; admit whole20k exploration with retained fresh source and start bounded formal','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Full80 original50mm1500controls6000callbacks query-contact-COMhardware and all prefix CPU reviews: forward7of27 reverse27of27 ordinary0, no qualification; wrapper missing dr_profile preGPU failure retained. Whole20k native144 actual107 source13CPUCUDA and all20k offset/defaultq; ordinary394 maxclosure3.17mm retained; stochastic fullPPO4 actor9 Adam80, weights discarded, sole parent294.981s charged. Fresh0PPO aftersave env unbound failure retained, independent remote/local107 actorcriticoptimizer13startup and actualexit-locksfree admission of own06a without GPU replay. New separate bounded3600formal actual dispatch522sourcefreeze and13ownstartup, original parameters and sole ledger retained; positive save/final/three inherited skills pending.','--push'];rec.main()
    tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
    p=D/'reports/LEFT_EXPLORATION_FULL80_FORMAL_STAGE_GIT_RECORDED.json';p.write_text(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),actual_saved_sources=len(rows),later_receipt_ordinary_supplement_required=True),indent=2),encoding='utf8');print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,actual_saved_sources=len(rows))))
if __name__=='__main__':main()
