"""Archive only the interactive replay source, fixed launch evidence and actual full40m PT."""
from pathlib import Path
import sys
T=Path(__file__).resolve().parent;p=T/'archive_run.py';s=p.read_text(encoding='utf8')
s=s.replace("ID='rearward-supported-stairs-40m-'+phase+'-01'","ID='rearward-supported-stairs-40m-manual-replay-01'")
s=s.replace("snapshot=E/'launch_snapshot'","snapshot=E/'manual_replay_snapshot_r1'")
a=s.index('files=[]');b=s.index('binary[:]=',a)
s=s[:a]+"files=[T/'local_low_speed_manual.py',T/'archive_manual_replay.py',T/'archive_run.py',T/'README.md',T/'weights/model_040m.pt',E/'MANUAL_LOW_SPEED_LATEST.json',E/'MANUAL_GUI_LAUNCH_SNAPSHOT.json',E/'MANUAL_GUI_REFRESH.json',E/'MANUAL_SCENE_ASSETS.json']\nfiles += list((T/'manual_low_speed_scene').glob('*.xml'))\nfiles += list((E/'manual_low_speed').glob('*/READY.json'))\n"+s[b:]
s=s.replace("'--kind','training'","'--kind','evaluation'")
s=s.replace("'--title','MOD4 video-supported rearward-wheel stairs40m '+phase","'--title','MOD4 latest40m low-speed interactive MuJoCo replay'")
sys.argv=[str(p),'--phase','launch'];exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
