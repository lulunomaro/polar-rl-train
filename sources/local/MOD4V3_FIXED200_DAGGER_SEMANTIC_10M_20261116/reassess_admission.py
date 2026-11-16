"""Reassess stored raw trajectories using native teacher recovery acceptance.
The student whole-episode0.6m/s criterion is retained as a separate, stricter result.
No simulation, replay, model update or raw-result rewriting.
"""
from pathlib import Path
import json,hashlib,numpy as np
T=Path(__file__).resolve().parent
rows=[]
for f in sorted((T/'dagger').rglob('correction.npz')):
 a=np.load(f);z=a['features'];raw=f.parent/'RESULT.json';r=json.loads(raw.read_text());hold=best=0.;peak=np.rad2deg(np.abs(z[:,5])).max()if len(z)else None
 for s in z:
  # Original run_teacher.py stable condition: both actual top contacts,
  # body crosses the edge+30mm, roll/pitch<.35rad, instantaneous speed<.60.
  stable=bool(s[13]and s[14]and s[1]>1.23 and abs(s[4])<.35 and abs(s[5])<.35 and s[10]<.60)
  hold=hold+.02 if stable else 0.;best=max(best,hold)
 qualified=bool(r['error']is None and hold>=.4-1e-7 and z[-1,13]and z[-1,14])
 result=dict(model=r['model'],start_offset_mm=r['start_offset_mm'],node=r['node'],qualified=qualified,reason='native_teacher_stable_final_top_support'if qualified else'no_final0.4s_stable_top_support',max_continuous_top_hold_s=best,final_continuous_top_hold_s=hold,initial_pitch_deg=r['takeover_pitch_deg'],final_pitch_deg=float(np.rad2deg(z[-1,5]))if len(z)else None,pitch_peak_deg=float(peak)if peak is not None else None,maximum_transient_speed_m_s=r['maximum_entry_ascent_speed_m_s'],raw_student_protocol_qualified=r['qualified'],raw_result_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),raw_result_unchanged=True,trajectory=str(f),frames=len(z),protocol='NATIVE_TEACHER_RECOVERY_STABLE_TOP_V2',instantaneous_stable_speed_limit_m_s=.6,student_whole_episode_speed_limit_unchanged=True,teacher_nominal_entry_speed_calibration_not_applied_to_perturbed_student_prefix=True,optimizer_updates=0,additional_simulation=False)
 (f.parent/'ADMISSION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');rows.append(result)
report=dict(protocol='NATIVE_TEACHER_RECOVERY_STABLE_TOP_V2',attempts=len(rows),qualified=sum(x['qualified']for x in rows),rejected=sum(not x['qualified']for x in rows),rows=rows,teacher_only_corrections_not_student_scores=True,raw_strict_results_preserved=True,source='Existing native run_teacher.py stable condition; latest human correction: no student historical-speed veto on teacher corrections')
(T/'dagger/ADMISSION_SUMMARY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('TEACHER_RECOVERY_ADMISSION',report['qualified'],'/',len(rows),'remaining failures',report['rejected'])
