"""Record the startup receipt and30s frozen low-speed evaluator correction once."""
from pathlib import Path
import sys
T=Path(__file__).resolve().parent;p=T/'archive_run.py';s=p.read_text(encoding='utf8')
s=s.replace("ID='rearward-supported-stairs-40m-'+phase+'-01'","ID='rearward-supported-stairs-40m-startup-followup-01'")
s=s.replace("snapshot=E/'launch_snapshot'","snapshot=E/'launch_followup_snapshot_r1'")
s=s.replace("files=[]","files=[E/'ARCHIVE_LAUNCH.log',E/'ARCHIVE_LAUNCH_ERROR.log']")
s=s.replace("'--title','MOD4 video-supported rearward-wheel stairs40m '+phase","'--title','MOD4 rearward stair startup: align frozen30s evaluation and preserve receipts'")
sys.argv=[str(p),'--phase','launch'];exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
