from slope_io import *
import ast,base64
sys.path.insert(0,str(W/"MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011"))
from curb_io import WIN
def worker_actual(w,wf):
    try:attention=json.loads(wf.open(WIN+'/E1_SLOPE8_QUERY_REVIEW_WORKER_ATTENTION.json').read())
    except FileNotFoundError:attention=None
    assert attention is None,attention
    source=wf.open(WIN+'/eval_worker_e1_slope8_query_review.py').read()
    assert source==(D/'eval_worker_e1_slope8_query_review.py').read_bytes()
    base=wf.open(WIN+'/eval_worker_closure2500.py').read()
    assert any(isinstance(x,ast.Assert) and "manifest['steps'] in [300, 1500]" in ast.unparse(x) for x in ast.walk(ast.parse(base.decode())))
    started=json.loads(wf.open(WIN+'/E1_SLOPE8_QUERY_REVIEW_WORKER_STARTED.json').read())
    ps="[pscustomobject]@{rows=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
    _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    procs=json.loads(raw)['rows']
    own=[p for p in procs if p['ProcessId']==started['pid'] and 'eval_worker_e1_slope8_query_review.py' in p['CommandLine'] and abs(p['creation_epoch']-started['epoch'])<2]
    assert len(own)==1
    return dict(worker=own,processes=procs,source_SHA=H(source),base_SHA=H(base),attention=None,healthy_worker_not_restarted=True)
