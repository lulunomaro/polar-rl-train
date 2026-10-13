from pathlib import Path
import json,time,sys,subprocess,importlib
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
def main():
    ID='wave50-linux-hour-final-left-joint-paired-factors'
    note=W/'MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014/ACTUAL_LEFT_JOINT_PAIRED_FACTOR_STAGE.md';dest=REPO/'history/evidence'/D.name/'final_left_joint_factor_stage'
    assert note.exists() and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID)
    old=cap.a.gitio.refs();cap.a.FOLDERS=(D,W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014',W/'MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014',W/'MOD4_3060_LEFT_JOINT_MARGIN014_FACTOR_20261014',W/'MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014')
    rows,files=cap.capture_streaming(dest)
    sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
    def wrapped(*args):
        if args[:2]==('add','--'):
            p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
        return cap.g(*args)
    rec.git=wrapped
    sys.argv=['record_experiment.py','--id',ID,'--title','Complete original Linux20k hour and reject two paired left-joint mean factors; admit whole20k exploration CPU candidate','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Actual whole20k final107/184updates88.32Msteps/12restore/actor9Adam3680/parentEXIT and sole settlement/twofcntl-free; original passed-key error retained with independent typed schema closeout; full8NPZ2.56GB control/reset/dynamicfamily/signed/40s prefix CPU reviewed; three fresh3060full1500 query-contactCOMhardware paired initialq30-DR-25RNG and actorbytes, center1of7-ordinary20 and margin0of7-ordinary3 rejected, current Linux final3of7-ordinary0 diagnostic; CPU107 whole20k left mean-std repair source8ff and actual independent targetCPU/disk admitted, GPU-PPO approval remains false.','--push'];rec.main()
    tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
    p=D/'reports/FINAL_LEFT_JOINT_STAGE_GIT_RECORDED.json';p.write_text(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),actual_saved_sources=len(rows),later_receipt_ordinary_supplement_required=True),indent=2),encoding='utf8');print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,actual_saved_sources=len(rows))))
if __name__=='__main__':main()
