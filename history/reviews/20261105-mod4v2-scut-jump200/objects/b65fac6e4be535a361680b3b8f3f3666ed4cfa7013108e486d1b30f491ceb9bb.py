"""Reuse authored-mesh playback for the actual saved Newton final1940 pose."""
from pathlib import Path
N=Path(__file__).resolve().parent
source=(N/'render_final357_video.py').read_text(encoding='utf8')
source=source.replace("A=N/'takeoff_velocity_weight12_final346_1h'", "A=N/'supermimic_final881_host_replay02_1h'")
source=source.replace('final357','final1940').replace('PhysX','Newton')
source=source.replace('[80,800,1600,3192]','[8,80,160,312]')
exec(compile(source,str(N/'render_final357_video.py'),'exec'),dict(__name__='__main__',__file__=str(__file__)))
