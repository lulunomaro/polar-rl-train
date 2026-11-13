"""Select the saved experimental student using complete paired fixed-task results."""
from pathlib import Path
import json,hashlib,shutil,time
T=Path(__file__).resolve().parent;R=T.parents[2]
def forward_error(folder):
 j=json.loads((folder/'flat60/RESULT.json').read_text());rows=[r for r in j['rows'] if r['task'] in ('forward20','forward22')];return sum(r['vx_abs_error'] for r in rows)/len(rows)
rows=[]
for p in sorted((T/'evidence/checkpoint_evals').glob('*/EVALUATION.json')):
 j=json.loads(p.read_text())
 if not j.get('complete'):continue
 file=Path(j['model']);assert file.is_file() and hashlib.sha256(file.read_bytes()).hexdigest()==j['sha256']
 preserved=j['flat60_passed']==60 and j['straight_passed']>=4 and j['descent_passed']==5
 row=dict(j,source_file=file.name,forward_MAE_m_s=forward_error(p.parent),preserves_original_fixed_baseline=preserved)
 row['selection_score']=[int(preserved),j['flat60_passed'],j['actual_oblique_passed'],j['straight_passed'],j['oblique_passed'],-row['forward_MAE_m_s']]
 rows.append(row)
assert rows,'No completed student fixed-task evaluation'
# A final alias of040m is the same model; earliest stable source name breaks identical-score ties.
rows.sort(key=lambda r:tuple(r['selection_score']),reverse=True);best=rows[0];source=Path(best['model']);target=T/'weights/selected_specialist_student.pt'
if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==best['sha256']
else:shutil.copy2(source,target)
selected=dict(model_id='stairs_specialist_student_20261113_'+source.stem.removeprefix('model_'),sha256=best['sha256'],source_file=source.name,source=source.relative_to(R).as_posix(),alias=target.relative_to(R).as_posix(),flat60=best['flat60_passed'],straight5=best['straight_passed'],actual_oblique20=best['actual_oblique_passed'],descent5=best['descent_passed'],forward_MAE_m_s=best['forward_MAE_m_s'],preserves_original_fixed_baseline=best['preserves_original_fixed_baseline'],status='Experimental fixed-suite selection; native stair/retainedRough results still required; original frozen parent remains available',selected_epoch=time.time())
(T/'weights/SELECTED_STUDENT.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(T/'evidence/STUDENT_FIXED_RANKING.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(selected),flush=True)
