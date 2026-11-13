"""Summarize paired native tests and the original finite training budget."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil

T = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--outputs',required=True)
parser.add_argument('--final',action='store_true')
args = parser.parse_args()
output = Path(args.outputs)
output.mkdir(parents=True,exist_ok=True)
rows = []
for path in sorted((T/'evidence').glob('eval_*/RESULT.json')):
    data = json.loads(path.read_bytes())
    checkpoint = Path(data.get('checkpoint',path.parent.name)).name
    revision = 'R4' if path.parent.name.startswith('eval_r4_') else ('R3' if path.parent.name.startswith('eval_r3_') else ('R2' if path.parent.name.startswith('eval_r2_') else 'R1'))
    if 'parent' in path.parent.name:
        minute = 0.
    elif checkpoint == 'model_final.pt':
        train = {'R1':'train120m_r1','R2':'train_cont_r2','R3':'train_cont_r3','R4':'train_cont_r4'}[revision]
        final_path = T/'evidence'/train/'FINAL.json'
        if not final_path.exists():
            continue
        final = json.loads(final_path.read_bytes())
        minute = final.get('total_window_elapsed_seconds',final['elapsed_seconds'])/60.
    else:
        minute = int(checkpoint.split('_')[1].removesuffix('m.pt'))
    row = dict(job=path.parent.name,revision=revision,minute=minute,checkpoint=checkpoint,
        sha256=data['checkpoint_sha256'],iteration=data.get('iteration',0))
    for group in ('nominal','fullDR'):
        for key,value in data['summary'][group].items():
            row[group+'_'+key] = value
        episodes=[item for item in data['episodes'] if bool(item['nominal'])==(group=='nominal')]
        row[group+'_success_survived']=sum(bool(item['success']) and not bool(item['terminated']) for item in episodes)
        row[group+'_late_failure_after_success']=sum(bool(item['success']) and bool(item['terminated']) for item in episodes)
    row['raw_total_success'] = row['nominal_success']+row['fullDR_success']
    row['total_success'] = row['nominal_success_survived']+row['fullDR_success_survived']
    rows.append(row)
rows.sort(key=lambda row:(row['revision'],row['minute'],row['job']))
if not rows:
    raise RuntimeError('No complete fixed evaluations collected')
csv_path = T/'evidence/EVALUATION_TABLE.csv'
with csv_path.open('w',newline='',encoding='utf8') as stream:
    writer = csv.DictWriter(stream,fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
candidates = [row for row in rows if row['revision'] in ('R3','R4') and 'parent' not in row['job']]
best = max(candidates,key=lambda row:(row['total_success'],row['nominal_success_survived'],
    row['fullDR_retracted']+row['nominal_retracted'],row['fullDR_takeoff']+row['nominal_takeoff'],row['minute'])) if candidates else None
nominal_best=max(candidates,key=lambda row:(row['nominal_success_survived'],row['total_success'],row['minute'])) if candidates else None
summary = dict(evaluations=rows,selected=best,selection_rule='Total balanced complete successes with no episode termination among256fixed cases; nominal success, measured retraction, takeoff and recency break ties. Original completed-event counts remain separately reported.',
    nominal_best=nominal_best,
    parent_sha256='03884d680c0fcb4c5216f8aeaa42c319473ea1cbc7261df089f42c1136b07edd',
    evaluation_protocol='R3phase commands/progress; R4adds descending-flight landing preparation. Versioned input producer, shared fixed seed10066and physical criteria;205fullDR/51nominal;deterministic learned action only, no optimizer',
    pending=not args.final)
if args.final:
    r1 = json.loads((T/'evidence/train120m_r1/FINAL.json').read_bytes())
    r2 = json.loads((T/'evidence/train_cont_r2/FINAL.json').read_bytes())
    r3 = json.loads((T/'evidence/train_cont_r3/FINAL.json').read_bytes())
    r4 = json.loads((T/'evidence/train_cont_r4/FINAL.json').read_bytes())
    phases=(r1,r2,r3,r4)
    started = json.loads((T/'evidence/train120m_r1/TRAINING_STARTED.json').read_bytes())
    summary['budget'] = dict(original_start_epoch=started['epoch'],deadline_epoch=started['epoch']+7200.,
        target_wall_window_seconds=7200,actual_window_seconds=r4['total_window_elapsed_seconds'],
        R1_owner_elapsed_seconds=r1['elapsed_seconds'],R2_owner_elapsed_seconds=r2['elapsed_seconds'],R3_owner_elapsed_seconds=r3['elapsed_seconds'],
        R4_owner_elapsed_seconds=r4['elapsed_seconds'],
        total_owner_phase_elapsed_seconds=sum(value['elapsed_seconds'] for value in phases),
        preparation_and_admission_inside_window_seconds=r4['total_window_elapsed_seconds']-sum(value['elapsed_seconds'] for value in phases),
        total_PPO_updates=sum(value['last_progress']['new_updates'] for value in phases),
        environment_steps=sum(value['last_progress']['total_env_steps'] for value in phases),
        concurrent_optimizers_max=1,automatic_extension=False,
        note='Elapsed owner phases include rollout/update/save work; independent GPU1evaluation has zero optimizer steps')
    assert best is not None
    source = T/'weights'/('train_cont_'+best['revision'].lower()+'__'+best['checkpoint'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == best['sha256']
    deliverable = output/'selected_forward_jump_full_ppo.pt'
    shutil.copy2(source,deliverable)
    summary['selected_output'] = dict(path=str(deliverable),bytes=deliverable.stat().st_size,sha256=best['sha256'])
    if nominal_best['nominal_success_survived']>0 and nominal_best['job']!=best['job']:
        other=T/'weights'/('train_cont_'+nominal_best['revision'].lower()+'__'+nominal_best['checkpoint'])
        assert hashlib.sha256(other.read_bytes()).hexdigest()==nominal_best['sha256']
        shutil.copy2(other,output/'best_nominal_forward_jump_full_ppo.pt')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig,axes = plt.subplots(2,1,figsize=(10,7),sharex=True,layout='constrained')
colors = {'nominal':'#107b52','fullDR':'#b54c32'}
def sampled_line(x,y):
    xx=[];yy=[];previous=None
    for a,b in zip(x,y):
        if previous is not None and a-previous>7.5:
            xx.append(float('nan'));yy.append(float('nan'))
        xx.append(a);yy.append(b);previous=a
    return xx,yy
for group in ('nominal','fullDR'):
    subset = sorted([row for row in rows if row['revision'] in ('R3','R4')],key=lambda row:row['minute'])
    x = [row['minute'] for row in subset]
    rate = [100*row[group+'_success_survived']/row[group+'_requested'] for row in subset]
    axes[0].plot(*sampled_line(x,rate),'o-',color=colors[group],label=group)
    for key,style in (('takeoff','-'),('retracted','--')):
        y = [100*row[group+'_'+key]/row[group+'_requested'] for row in subset]
        axes[1].plot(*sampled_line(x,y),style,color=colors[group],label=group+' '+key)
for axis in axes:
    axis.set_ylim(-2,102)
    axis.set_ylabel('Fixed cases passed (%)')
    axis.grid(alpha=.18)
    axis.spines[['top','right']].set_visible(False)
    axis.legend(loc='upper left',frameon=False,ncol=2)
axes[0].set_title('Learned forward jump | complete sequence, air balance and stable landing',loc='left',fontsize=12)
axes[1].set_title('Measured takeoff and airborne retraction',loc='left',fontsize=11)
axes[1].set_xlabel('Minutes in the original 120-minute window')
r4_start=T/'evidence/train_cont_r4/TRAINING_STARTED.json'
if r4_start.exists():
    switch=json.loads(r4_start.read_bytes())
    minute=(switch['epoch']-switch['original_start_epoch'])/60.
    for axis in axes:axis.axvline(minute,color='#777777',linestyle=':',linewidth=1.)
    axes[0].text(minute-1.,96.,'R4: descending cue',rotation=90,ha='right',va='top',fontsize=8,color='#555555')
fig.savefig(T/'evidence/learning_curve.png',dpi=160)
plt.close(fig)
shutil.copy2(csv_path,output/'evaluation_table.csv')
shutil.copy2(T/'evidence/learning_curve.png',output/'learning_curve.png')
(T/'evidence/RESULTS_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
shutil.copy2(T/'evidence/RESULTS_SUMMARY.json',output/'results_summary.json')
print(json.dumps(dict(evaluations=len(rows),selected=best,budget=summary.get('budget'),pending=summary['pending']),indent=2))
