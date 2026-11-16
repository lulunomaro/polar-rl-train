from pathlib import Path
import sys,json
T=Path(__file__).resolve().parent;R=T.parent.parents[2]
sys.path.insert(0,str(R/'archive_tools'));import record_experiment as rec
files=[T/n for n in ['play_manual.py','LAUNCH_REPORT.md','INITIAL_READY_SNAPSHOT.json','INITIAL_SELECTION_SNAPSHOT.json','PROTECTED_INPUTS_VERIFICATION.json','archive_manual.py']]
sys.argv=['record_experiment','--id','mod4v3-prewall-probe-wasd-open-01','--title','Open isolated MOD4v3 prewall actor WASD player, default c874 retained','--kind','evaluation','--note-file',str(T/'LAUNCH_REPORT.md'),'--validation','Desktop verified MuJoCo and projectWASD console; default faec0177 andstair paused; native timing; no optimizer or teacher;86protectedSHA unchanged','--files',*[p.relative_to(R).as_posix()for p in files],'--push']
original=rec.git
def git(*a):return original('add','-f','--sparse',*a[1:])if a[:2]==('add','--')else original(*a)
rec.git=git;rec.main()
