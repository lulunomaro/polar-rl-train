from pathlib import Path
import sys,json,numpy as np
P=Path(__file__).resolve().parent

def interval(f,v,i,j):
 if j<i:return None
 x=f[i:j+1,1]
 return dict(pitch_peak_deg=float(np.rad2deg(abs(f[i:j+1,5])).max()),min_vx=float(v[i:j+1].min()),max_retreat_mm=float(np.max(np.maximum.accumulate(x)-x)*1000),net_travel_mm=float((x[-1]-x[0])*1000))
def metrics(d):
 r=json.loads((d/'RESULT.json').read_text());a=np.load(d/'trace.npz');f=a['trace'];v=a['qvel'][:,0];ph=a['phases'][:,0];t=f[:,0]
 il=np.flatnonzero(ph=='lift');ic=np.flatnonzero(ph=='capture')
 if not len(il)or not len(ic):return dict(name=d.name,pass_scoring=r['pass_teacher_stair'],full=interval(f,v,0,len(t)-1),transitions=r['phase_transitions'])
 l,c=int(il[0]),int(ic[0]);en=np.searchsorted(t,r['entry']['time']);ends=np.flatnonzero((np.arange(len(t))>c)&(ph=='idle'));end=int(ends[0])if len(ends)else min(len(t)-1,c+50)
 wait_start=np.searchsorted(t,t[l]-.12)
 return dict(name=d.name,pass_scoring=r['pass_teacher_stair'],stable_hold_s=r['max_continuous_top_hold_s'],actual_entry_mps=r['entry']['pre_100ms_speed'],prelift=interval(f,v,en,l-1),wait=interval(f,v,wait_start,l),climb=interval(f,v,l,c-1),capture=interval(f,v,c,end),climb_window=interval(f,v,en,min(len(t)-1,c+50)),full=interval(f,v,en,len(t)-1),lift_time=float(t[l]),capture_time=float(t[c]),exit_capture_time=float(t[end]),min_top_wheel_margin_mm=float((f[c:,[8,11]].min()-1.2)*1000),final_position=r['final_position'],final_pitch_deg=r['final_rpy_deg'][1],transitions=r['phase_transitions'])
if __name__=='__main__':
 for d in sorted(P.glob(sys.argv[1]if len(sys.argv)>1 else '*mm')):
  if (d/'RESULT.json').exists():print(json.dumps(metrics(d),ensure_ascii=False))
