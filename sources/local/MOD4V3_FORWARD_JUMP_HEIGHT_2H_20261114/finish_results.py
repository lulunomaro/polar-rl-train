"""Compare only fixed-final-target R2 evaluations and preserve all attempts."""
import csv
import json
from pathlib import Path
import time

T=Path(__file__).resolve().parent
rows=[]
for path in sorted((T/'evidence').glob('eval_*/RESULT.json')):
    if path.parent.name=='eval_parent_fixed':continue
    result=json.loads(path.read_bytes())
    summary=result['summary']
    row=dict(job=path.parent.name,checkpoint=result['checkpoint'],sha256=result['checkpoint_sha256'],iteration=result['iteration'])
    for group in ('nominal','fullDR'):
        s=summary[group]
        for key in ('requested','survived_success','survived_sequence_complete','median_rim_m','median_body_rise_m','max_rim_m','max_body_rise_m'):
            row[group+'_'+key]=s[key]
    rows.append(row)
assert rows,'No independent evaluation was collected'
def rank(row):
    return (row['nominal_survived_success'],row['fullDR_survived_success'],
            row['nominal_survived_sequence_complete'],row['fullDR_survived_sequence_complete'],
            row['nominal_median_rim_m'],row['fullDR_median_rim_m'])
selected=max(rows,key=rank)
final_path=T/'evidence/train7200/FINAL.json'
error_path=T/'evidence/train7200/ERROR.json'
report=dict(epoch=time.time(),selected=selected,evaluations=rows,
            training_final=json.loads(final_path.read_bytes()) if final_path.exists() else None,
            training_error=json.loads(error_path.read_bytes()) if error_path.exists() else None,
            height_targets=dict(wheel_clearance_m=.35,body_rise_m=.32),
            player_model_replaced=False,real_robot_certified=False)
(T/'evidence/RESULTS_SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
with (T/'evidence/checkpoint_results.csv').open('w',encoding='utf8',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
text=f'''# Forward Jump Height Training Results

One new7200-second training owner was requested. Full checkpoint records, fixed-final-target evaluations and prior R1/R2 admission attempts are retained. The existing interactive player was not changed.

Candidate selected by survived fixed-height successes, complete sequences and measured clearance: `{selected['job']}`. Checkpoint SHA: `{selected['sha256']}`.

Nominal35cm-clearance/32cm-body-rise survived successes: {selected['nominal_survived_success']}/{selected['nominal_requested']}. FullDR: {selected['fullDR_survived_success']}/{selected['fullDR_requested']}. Legacy complete-sequence survived passes: nominal{selected['nominal_survived_sequence_complete']},fullDR{selected['fullDR_survived_sequence_complete']}.

Nominal median wheel-rim clearance: {selected['nominal_median_rim_m']:.4f}m. FullDR median: {selected['fullDR_median_rim_m']:.4f}m. These medians include the fixed requested cases and are not obstacle-clearance guarantees. Full per-environment results and measured body rise are in the linked JSON/NPZ evidence.

Training final record present: {final_path.exists()}. Training error record present: {error_path.exists()}. This is a simulation candidate and does not promote a policy to hardware or replace the manual player.
'''
(T/'FINAL_REPORT.md').write_text(text,encoding='utf8')
print(json.dumps(dict(selected=selected,evaluations=len(rows)),indent=2))
