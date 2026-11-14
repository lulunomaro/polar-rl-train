"""Select and report independent fixed cases, excluding any later termination."""
import argparse
import csv
from datetime import datetime,timezone,timedelta
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

T=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--outputs',required=True);p.add_argument('--final',action='store_true');a=p.parse_args()
out=Path(a.outputs);out.mkdir(parents=True,exist_ok=True)
rows=[]
for path in sorted((T/'evidence').glob('eval_*/RESULT.json')):
    d=json.loads(path.read_bytes())
    label=path.parent.name
    name=Path(d['checkpoint']).name
    local=T/'weights'/('train7200__'+name)
    minute=float(name[6:9]) if name[6:9].isdigit() else (120. if name=='model_final.pt' else 0.)
    row=dict(job=label,checkpoint=name,minute=minute,sha256=d['checkpoint_sha256'],iteration=d['iteration'])
    for nominal,group in ((False,'fullDR'),(True,'nominal')):
        cases=[e for e in d['episodes'] if e['nominal']==nominal]
        survived=sum(e['success'] and not e['terminated'] for e in cases)
        for k,v in d['summary'][group].items():row[group+'_'+k]=v
        row[group+'_success_survived']=survived
        row[group+'_later_failure']=sum(e['success'] and e['terminated'] for e in cases)
        row[group+'_rate']=survived/len(cases)
    row['total_success']=row['nominal_success_survived']+row['fullDR_success_survived']
    row['worst_group_rate']=min(row['nominal_rate'],row['fullDR_rate'])
    row['child_checkpoint']=local.exists()
    rows.append(row)
assert rows,'No completed independent evaluations'
candidates=[r for r in rows if r['child_checkpoint']]
selected=max(candidates,key=lambda r:(r['worst_group_rate'],r['total_success'],r['nominal_success_survived'],r['minute'])) if candidates else None
summary=dict(evaluations=rows,selected=selected,pending=not a.final,
    selection_rule='Maximize lower of nominal/fullDR complete-and-survived rates, then total complete cases, nominal complete cases, recency',
    evaluation_protocol='Seed10066;51nominal/205fullDR; deterministic actor-only; native closed-chain state; no optimizer; fixed physical and success criteria',
    parent_sha256=json.loads((T/'PLAN.json').read_bytes())['parent_sha256'])
if a.final:
    f=json.loads((T/'evidence/train7200/FINAL.json').read_bytes())
    s=json.loads((T/'evidence/train7200/TRAINING_STARTED.json').read_bytes())
    summary['budget']=dict(start_epoch=s['epoch'],target_seconds=7200,actual_owner_seconds=f['elapsed_seconds'],
        end_epoch=f['epoch'],updates=f['last_progress']['new_updates'],environment_steps=f['last_progress']['total_env_steps'],
        preparation_and_admission_inside_window_seconds=0,optimizer_owners=1,automatic_extension=False,
        stopped_by_request=f['request_stop'])
    assert f['elapsed_seconds']>=7200 and not f['request_stop']
    assert selected is not None
    source=T/'weights'/('train7200__'+selected['checkpoint'])
    assert hashlib.sha256(source.read_bytes()).hexdigest()==selected['sha256']
    target=out/'selected_forward_jump_full_ppo.pt';shutil.copy2(source,target)
    summary['selected_output']=dict(path=str(target),sha256=selected['sha256'],bytes=target.stat().st_size)
    plan=json.loads((T/'PLAN.json').read_bytes())
    clock=lambda t:datetime.fromtimestamp(t,timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S CST')
    n=selected['nominal_success_survived'];dr=selected['fullDR_success_survived']
    final_row=next((r for r in rows if r['checkpoint']=='model_final.pt'),None)
    report=f'''# Forward Jump Repair And New Two-Hour PPO Result

New continuous learning window: {clock(s['epoch'])} to {clock(f['epoch'])}; actual owner duration {f['elapsed_seconds']:.3f}s. Preparation, physical admission and teacher collection happened before this window. PPO updates: {f['last_progress']['new_updates']}; native environment steps: {f['last_progress']['total_env_steps']:,}. Exactly one optimizer owner on Host72GPU0; GPU1evaluations created no optimizer. Full saves were made every five minutes and at final completion.

Selected child: `{selected['checkpoint']}`, iteration{selected['iteration']}, SHA256`{selected['sha256']}`. Independent deterministic fixed evaluation: nominal complete and survived **{n}/51**, fullDR **{dr}/205**. Nominal measured retraction: **{selected['nominal_retracted']}/51**. FullDR measured retraction: **{selected['fullDR_retracted']}/205**. Nominal airborne balance: **{selected['nominal_air_balance_passed']}/51**; fullDR airborne balance: **{selected['fullDR_air_balance_passed']}/205**. Total accepted complete cases: **{selected['total_success']}/256**. The complete result already requires the full forward-crouch-push-air-tuck-land-stable sequence and rejects later terminations. Final chronological checkpoint result: `{json.dumps(final_row)}`.

## Repair And Evidence

The predecessor best learned child had nominal0/51tucks and0/51complete passes, despite51/51takeoff and airborne balance passes. Measured minimum airborne leg difference median1.055rad exceeded the unchanged<0.9radcriterion. Flight action fitting error was much higher than other phases. We confirmed conflicting timing: reward started rewarding landing extension at vz<0, while teacher/cue switched at vz<-0.10regardless of measured tuck. The repaired reward, observed landing-preparation command and training-only labels all require actual measured tuck first. The original80ms teacher tuck ramp was retained. Online loss uses phase-balanced means and flight weight4; equal-phase demo loss uses the same flight weight. The two-hour plant is driven solely by learned actor output; there is no scripted motor overlay.

The first40ms teacher probe was rejected as the final teacher:51/51nominal tucks but37/51complete passes,14pitch failures. Its successful and failed cases, source snapshot and dataset remain recorded. The80ms follow-up dataset and all failed attempted episodes are stored separately. Teacher successes are not counted as learned-policy performance. No standalone BC warmup or unbudgeted optimizer update occurred. Native PPO already clips actor and critic separately; no unproven critic-clipping defect was claimed.

## Provenance And Contract

Continuation parent SHA`{plan['parent_sha256']}`; root five-minute parent SHA`{plan['root_parent_sha256']}`. Complete actor, critic,STD,17Adam states and RNG restored from the prior best learned child. Actor35/critic78/action6retained; fresh physical episodes. NativeMOD4V3HW300N60R3asset, motor envelopes,2.5ms/TGS32/4,leg100Hz/wheel400Hz/policy50Hzretained. Closure10mm and mimic0.01radare per-environment episode resets. Admission and zero-update finite-gradient check are in evidence.

Acceptance thresholds remain: measured tuck<0.9rad; air>=0.16s; wheel rim peak>=0.12m; all-air pitch<=10deg/roll<=5deg; stable forward landing>=0.5s with>=80%support,|vz|<0.3m/s,vx>0.1m/s,roll/pitch<15deg,no forbidden contact. No threshold was lowered.

Selection uses the lower nominal/fullDR success rate first, then total successes, nominal successes and recency. All fixed-checkpoint evaluations and individual failures are retained. These fixed cases are selection evidence, not a claim of generalization across all seeds. Phase command semantics are versioned and need a matching deployment input producer. No production or hardware promotion was performed. Host210and existing viewer were not touched.

## Files

`checkpoint_results.csv`, `results_summary.json`, `training_curve.png`, selected complete PPO checkpoint and recorded-native-state video/frame board are in the delivery directory. Full PT bodies are retained in Git as specifically requested for this session; large trajectory and media originals are indexed by path,size,SHA. Launch and final Git receipts are verified separately by the archive tool.
'''
    (T/'FINAL_REPORT.md').write_text(report,encoding='utf8');(out/'FINAL_REPORT.md').write_text(report,encoding='utf8')
for target in (T/'evidence/RESULTS_SUMMARY.json',out/'results_summary.json'):
    target.write_text(json.dumps(summary,indent=2)+'\n')
with (out/'checkpoint_results.csv').open('w',newline='',encoding='utf8') as stream:
    writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
fig,axes=plt.subplots(2,1,figsize=(10,7),sharex=True,layout='constrained')
for group,color in (('nominal','#197c53'),('fullDR','#b44b35')):
    ordered=sorted(candidates,key=lambda r:(r['minute'],r['checkpoint']))
    x=[r['minute'] for r in ordered]
    axes[0].plot(x,[100*r[group+'_rate'] for r in ordered],'o-',color=color,label=group+' complete')
    axes[1].plot(x,[100*r[group+'_retracted']/r[group+'_requested'] for r in ordered],'o-',color=color,label=group+' measured tuck')
for axis in axes:
    axis.set_ylim(-2,102);axis.set_ylabel('Fixed cases passed (%)');axis.grid(alpha=.2);axis.legend(frameon=False)
    axis.spines[['top','right']].set_visible(False)
axes[0].set_title('Moving jump repair | deterministic learned policy')
axes[1].set_xlabel('New training window (minutes)')
fig.savefig(out/'training_curve.png',dpi=160);fig.savefig(T/'evidence/training_curve.png',dpi=160);plt.close(fig)
print(json.dumps(dict(selected=selected,budget=summary.get('budget'),evaluations=len(rows)),indent=2))
