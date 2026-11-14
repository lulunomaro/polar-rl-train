"""Select pitch-stability candidate while retaining measured flat and stair skills."""
from pathlib import Path
import json,hashlib,shutil,time
T=Path(__file__).resolve().parent;R=T.parents[2];rows=[]
for p in sorted((T/'evidence/checkpoint_evals').glob('*/EVALUATION.json')):
 j=json.loads(p.read_text())
 if not j.get('complete'):continue
 source=Path(j['model']);assert source.is_file()and hashlib.sha256(source.read_bytes()).hexdigest()==j['sha256']
 groups=j['pitch_summary'];complete=sum(x['completed_without_reset']for x in groups.values())
 values=list(groups.values());rms=sum(x['pitch_RMS_deg_mean']or 90. for x in values)
 peaks=sum((x['startup_peak_deg_max']or 90.)+(x['braking_peak_deg_max']or 90.)for x in values)
 preservation=j['flat60_passed']==60 and j['descent_passed']==5 and j['straight_passed']>=4
 error=sum(x['moving_vx_MAE_mean']or 10. for x in values)
 row=dict(j,source_file=source.name,preserves_comprehensive_fixed_baseline=preservation,pitch_complete_cases=complete,stability_score=rms+.15*peaks,selection_score=[int(preservation),complete,-(rms+.15*peaks),-error,j['actual_oblique_passed']]);rows.append(row)
assert rows,'No complete pitch comparison'
rows.sort(key=lambda r:tuple(r['selection_score']),reverse=True);best=rows[0];source=Path(best['model']);target=T/'weights/selected_specialist_student.pt'
if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==best['sha256']
else:shutil.copy2(source,target)
selected=dict(model_id='pitch_stability_level9_20261115_'+source.stem.removeprefix('model_'),sha256=best['sha256'],source_file=source.name,source=source.relative_to(R).as_posix(),alias=target.relative_to(R).as_posix(),pitch_summary=best['pitch_summary'],pitch_complete_cases=best['pitch_complete_cases'],flat60=best['flat60_passed'],straight5=best['straight_passed'],actual_oblique20=best['actual_oblique_passed'],descent5=best['descent_passed'],preserves_comprehensive_fixed_baseline=best['preserves_comprehensive_fixed_baseline'],status='Experimental fixed-suite pitch selection;frozen comprehensive db6 remains default;native results reported separately',selected_epoch=time.time())
(T/'weights/SELECTED_STUDENT.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n');(T/'evidence/STUDENT_FIXED_RANKING.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(json.dumps(selected),flush=True)
