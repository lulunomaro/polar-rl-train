from second_io import *
from curb_io import WIN
import base64

def worker_actual(w,wf):
    try:attention=json.loads(wf.open(WIN+'/E1_WAVE50_QUERY_REVIEW_WORKER_ATTENTION.json').read())
    except FileNotFoundError:attention=None
    source=wf.open(WIN+'/eval_worker_e1_wave50_query_review.py').read();assert source==(D/'eval_worker_e1_wave50_query_review.py').read_bytes()
    base=wf.open(WIN+'/eval_worker_closure2500.py').read();assert H(base)=='0b7e7a700a952dda0a08edc7587406f39880d10843ee4ef49132fe979e6268f1'
    started=json.loads(wf.open(WIN+'/E1_WAVE50_QUERY_REVIEW_WORKER_STARTED.json').read())
    ps="[pscustomobject]@{rows=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
    _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    procs=json.loads(raw)['rows'];own=[p for p in procs if p['ProcessId']==started['pid'] and 'eval_worker_e1_wave50_query_review.py' in p['CommandLine'] and abs(p['creation_epoch']-started['epoch'])<2]
    if attention is None:assert len(own)==1
    return dict(worker=own,processes=procs,source_SHA=H(source),base_SHA=H(base),attention=attention,namespace='E1_WAVE50_QUERY_REVIEW',healthy_worker_not_restarted=True)
