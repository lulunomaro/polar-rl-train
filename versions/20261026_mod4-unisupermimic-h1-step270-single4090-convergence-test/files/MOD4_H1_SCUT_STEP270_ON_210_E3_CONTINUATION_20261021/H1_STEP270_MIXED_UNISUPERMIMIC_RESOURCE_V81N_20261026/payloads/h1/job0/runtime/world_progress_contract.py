"""Factual world-progress confirmation, separate from learning admission."""
import math
from scut_curriculum_gate_v4 import assess
def target(report,goal):
 a=assess(report);rows=report.get('world_cycle_metrics') or [];out=[]
 tolerance=max(.03,.10*goal)
 for r in rows:
  along=r.get('complete_prefix_along_m_s');cross=r.get('complete_prefix_cross_m_s')
  yaw=(report.get('per_environment') or {}).get('yaw_rate',[])
  observed=yaw[r['env_id']] if r['env_id']<len(yaw) else None
  commanded=r.get('command_yaw_rad_s')
  valid=bool(r.get('valid') and r.get('complete_cycle_count',0)>=1 and isinstance(along,(int,float)) and isinstance(cross,(int,float)) and math.isfinite(along) and math.isfinite(cross)
             and isinstance(observed,(int,float)) and math.isfinite(observed) and isinstance(commanded,(int,float)) and abs(observed-commanded)<=.2)
  out.append(dict(env_id=r['env_id'],group_id=r['group_id'],goal_m_s=goal,cycles=r.get('complete_cycle_count'),along_m_s=along,cross_m_s=cross,
   observed_yaw_rad_s=observed,command_yaw_rad_s=commanded,
   pass_=bool(valid and abs(along-goal)<=tolerance and abs(cross)<=tolerance),all_cycles_retained=r.get('cycles'),cross_peak_to_peak_m=r.get('cross_peak_to_peak_m')))
 # Final confirmation uses every sampled moving environment; this is never a
 # physical safety veto or an intermediate curriculum graduation requirement.
 return dict(pass_=bool(a['pass_'] and len(out)==64 and all(x['pass_'] for x in out)),rows=out,
  factual_net_progress_tolerance_m_s=tolerance,used_for_learning_veto=False,
  scope='Signed measured net along/cross progress over all actual full turns from first sample. Periodic lateral motion retained, not an instantaneous straight-line promise.')
