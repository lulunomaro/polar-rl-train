"""Send the authorized40m independent-evaluation stop verdict to the paused run."""
from pathlib import Path
import json,os
import numpy as np

def assess(T,sftp,remote_job):
    source=T/'evidence/checkpoint_evals/model_040m/single_step/RESULT.json'
    receipt=T/'evidence/ASSESSMENT_040M_SENT.json'
    if receipt.exists()or not source.exists():return
    d=json.loads(source.read_text());cases=[]
    for row in d['rows']:
        tr=np.load(source.parent/f"start_{row['start_offset_mm']:+04d}mm"/'rollout.npz');trace=tr['trace'];obs=tr['obs'];moving=obs[:,0]>.1
        x=trace[moving,1];advance=float(x.max()-x[0])if len(x)else 0.
        guide=row.get('guide_diagnostics',{});blocked=guide.get('guide_wall_stall_seconds',0.)>=.2
        reverse=row.get('maximum_retreat_m',0.)>.15
        stationary=advance<.05
        progress=bool(row.get('physical_bilateral_crossed')or row.get('physical_stable_event')or row.get('actual_single_wheel_top_support_frames',0)>0)
        cases.append(dict(offset_mm=row['start_offset_mm'],real_top_progress=progress,guide_blocked=blocked,reversed=reverse,stationary=stationary,forward_progress_after_command_m=advance))
    no_progress=not any(x['real_top_progress']for x in cases)
    collapsed=sum(x['guide_blocked']or x['reversed']or x['stationary']for x in cases)>=3
    verdict=dict(stop=bool(no_progress and collapsed),reason='no_actual_single_or_bilateral_top_progress_and_at_least3_collapsed_cases'if no_progress and collapsed else'actual_top_progress_or_no_general_collapse',checkpoint_sha256=d['sha256'],formal_qualified=d['passed'],physical_crossed=d['physical_crossed'],cases=cases,optimizer_updates=0)
    temp=remote_job+'/STOP_VERDICT_040M.json.partial';data=(json.dumps(verdict,indent=2)+'\n').encode()
    with sftp.open(temp,'wb')as f:f.write(data)
    sftp.posix_rename(temp,remote_job+'/STOP_VERDICT_040M.json')
    receipt.write_text(json.dumps(verdict,indent=2)+'\n')
