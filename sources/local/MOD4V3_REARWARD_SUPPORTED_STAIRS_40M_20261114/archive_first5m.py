"""Archive the verified first5m fullPPO and its inspection without re-running training."""
from pathlib import Path
import sys
T=Path(__file__).resolve().parent;p=T/'archive_run.py';s=p.read_text(encoding='utf8')
s=s.replace("ID='rearward-supported-stairs-40m-'+phase+'-01'","ID='rearward-supported-stairs-40m-first5m-inspection-01'")
s=s.replace("snapshot=E/'launch_snapshot'","snapshot=E/'first5m_snapshot_r1'")
s=s.replace("files=[]","files=[E/'ARCHIVE_LAUNCH.log',E/'ARCHIVE_LAUNCH_ERROR.log',E/'ARCHIVE_START_FOLLOWUP.log',E/'ARCHIVE_START_FOLLOWUP_ERROR.log',E/'inspections/INSPECTION_005M.json',E/'training/PERIODIC_005M.json']")
s=s.replace("'--title','MOD4 video-supported rearward-wheel stairs40m '+phase","'--title','MOD4 rearward stairs: first5m completePPO and inspection'")
sys.argv=[str(p),'--phase','launch'];exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
