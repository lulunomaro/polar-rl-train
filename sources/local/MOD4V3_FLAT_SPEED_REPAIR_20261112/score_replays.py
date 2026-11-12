"""Compare fixed checkpoint consumers; score is diagnostic, not promotion."""
from pathlib import Path
import json,math
T=Path(__file__).resolve().parent;E=T/'evidence';rows=[];core=['forward20','forward22','forward22_h022','forward22_h038','forward22_h040','forward15_h028','forward15_h040']
locations=[('parent',0.,E/'repair_parent_matched/RESULT.json')]
for phase,folder,job,offset in [('head','repair_checkpoint_evals','training_round',0.),('full','full_actor_checkpoint_evals','training_round_full_actor',json.loads((E/'BUDGET_AFTER_P1.json').read_text())['phase1_used_seconds'])]:
 for f in sorted((E/folder).glob('*/RESULT.json')):
  stem=f.parent.name
  receipt=T/job/('FIRST_UPDATE.json' if stem=='model_first_complete' else 'FINAL.json' if stem=='model_final' else 'PERIODIC_'+stem[6:9]+'M.json')
  if not receipt.exists():continue
  meta=json.loads(receipt.read_text());seconds=(meta['elapsed_seconds'] if stem=='model_final' else meta['training_elapsed_seconds'])+offset
  locations.append((phase+'_'+stem,seconds/60.,f))
for label,minutes,f in locations:
 if not f.exists():continue
 d=json.loads(f.read_text());forward=[r for r in d['rows'] if r['task'] in core];ordinary=[r for r in d['rows'] if r['task'] in ['forward20','forward22']];retention=[r for r in d['rows'] if r['task'] in ['reverse15','yaw14137','height020','height040','stop028']]
 row=dict(label=label,minutes=minutes,model=d['model'],sha256=d['sha256'],result=str(f.relative_to(T)),forward_passed=sum(r['passed'] for r in forward),forward_requested=len(forward),forward_max_error=max(r['vx_abs_error'] for r in forward),forward_mean_error=sum(r['vx_abs_error'] for r in forward)/len(forward),ordinary_passed=sum(r['passed'] for r in ordinary),ordinary_requested=len(ordinary),retention_passed=sum(r['passed'] for r in retention),retention_requested=len(retention),resets=sum(r['reset_count'] for r in d['rows']),nominal={r['task']:{k:r[k] for k in ['vx_mean','wz_mean','height_mean','passed']} for r in d['rows'] if r['delay_ms']==0})
 rows.append(row)
rows.sort(key=lambda x:x['minutes']);(E/'REPLAY_SCOREBOARD.json').write_text(json.dumps(dict(scope='same fixed nominal0/5ms MuJoCo consumer;no fullDR/native graduation claim',core_forward_tasks=core,rows=rows),ensure_ascii=False,indent=2))
for x in rows:print(x['label'],round(x['minutes'],2),str(x['forward_passed'])+'/'+str(x['forward_requested']),'worst',round(x['forward_max_error'],4),'mean',round(x['forward_mean_error'],4),'retained',str(x['retention_passed'])+'/'+str(x['retention_requested']))
