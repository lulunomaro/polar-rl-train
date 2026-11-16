"""Read actual independent student rollouts; official and physical metrics separate."""
from pathlib import Path
import json,argparse,numpy as np
T=Path(__file__).resolve().parent

def analyze(root):
 result=json.loads((root/'single_step/RESULT.json').read_text());rows=[]
 for r in result['rows']:
  a=np.load(root/'single_step'/f"start_{r['start_offset_mm']:+04d}mm/rollout.npz");z=a['trace'];obs=a['obs'];moving=np.flatnonzero(obs[:,0]!=0);last_zero=int(moving[0])-1 if len(moving)else len(z)-1;first_zero=np.arange(max(0,last_zero+1));mask=z[:,9:11].all(1)&(z[:,1]>1.23);run=best=0
  for b in mask:run=run+1 if b else 0;best=max(best,run)
  speed_rejected=bool(r['entry_speed_m_s']is not None and not(.1<=r['entry_speed_m_s']<=.6))or r['maximum_entry_ascent_speed_m_s']>.6
  rows.append(dict(start_offset_mm=r['start_offset_mm'],strict_qualified_pass=r['success'],official_reason=r['reason'],qualified_hold_s=r['max_continuous_top_hold_s'],entry_speed_m_s=r['entry_speed_m_s'],maximum_entry_ascent_speed_m_s=r['maximum_entry_ascent_speed_m_s'],speed_rejected=speed_rejected,zero_command_first_second_displacement_x_m=float(z[last_zero,1]-r['start_offset_mm']/1000)if last_zero>=0 else None,zero_command_first_second_max_speed_m_s=float(z[first_zero,5].max())if len(first_zero)else None,max_continuous_bilateral_top_body_crossed_s=best*.02,final_bilateral_top_body_crossed=bool(mask[-1]),actual_top_body_frames=int(mask.sum()),pitch_peak_deg=r['pitch_peak_deg'],minimum_forward_vx=r['minimum_forward_vx'],maximum_retreat_m=r['maximum_retreat_m'],teacher_actions=0))
 return dict(source=str(root/'single_step/RESULT.json'),strict_passed=result['passed'],requested=result['requested'],physical_top_body_cases=sum(x['max_continuous_bilateral_top_body_crossed_s']>=.4 and x['final_bilateral_top_body_crossed']for x in rows),rows=rows,pure_student=True,physical_metric_does_not_replace_strict_score=True,additional_simulation=False,optimizer_updates=0)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('checkpoint');a=p.parse_args();root=T/'evidence/checkpoint_evals'/a.checkpoint;report=analyze(root);dest=T/'evidence'/('STUDENT_DIAGNOSTICS_'+a.checkpoint+'.json');assert not dest.exists();dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('STUDENT_DIAGNOSTICS',a.checkpoint,json.dumps(report,ensure_ascii=False))
